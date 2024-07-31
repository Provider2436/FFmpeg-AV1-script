import os
import subprocess
import time
import re
import platform
import shutil
import requests

#detect os
is_windows = platform.system().lower() == 'windows'

#script based on os
if is_windows:
    script_ext = '.bat'
    run_cmd = ['cmd.exe', '/c']
else:
    script_ext = '.sh'
    run_cmd = ['bash']

#script location
script = input(f'Enter where you want the script to be located (with the extension {script_ext}): ').strip()

#erasing script is it already exists
with open(script, 'w') as file:
    pass

#helper for the ffmpeg command variables
def verif(inp, minn, maxx):
    while True:
        try:
            val = int(input(inp))
            if minn <= val <= maxx:
                return val
            else:
                print(f'Enter a value between {minn} and {maxx}')
        except ValueError:
            print("Invalid input, you need to input an int")

def verif_str(inp, pattern=None, min_length=None):
    while True:
        val = input(inp).strip()
        if pattern and not re.match(pattern, val):
            print(f"The input must match the pattern: {pattern}")
        elif min_length and len(val) < min_length:
            print(f"The input must be at least {min_length} characters long")
        else:
            return val

def swap_num(filename, new_num):
    pattern = r'(S\d{2}E)\d{2}'
    replacement = r'\g<1>{:02}'.format(new_num)
    new_filename = re.sub(pattern, replacement, filename)
    return new_filename

def check_path_exists(path, is_file=False):
    if not os.path.exists(path):
        raise ValueError(f"The path '{path}' does not exist.")
    if is_file and not os.path.isfile(path):
        raise ValueError(f"The path '{path}' is not a file.")
    if not is_file and not os.path.isdir(path):
        raise ValueError(f"The path '{path}' is not a directory.")

#movie or show
question = verif_str('Enter the type of the media (eg: movie, show): ', pattern=r'movie|show').strip()
if question == "movie":
    files = 1
elif question == "show":
    files = verif('Enter the number of episodes: ', 1, 1000)

#path check
s_path = verif_str("Enter the path of the source file(s): ", min_length=1)
check_path_exists(s_path)

o_path = verif_str("Enter the output path of the encoded file(s): ", min_length=1)
if not os.path.exists(o_path):
    os.makedirs(o_path)  

if files > 1:
    pattern = r'S\d{2}E\d{2}'
    s_name = verif_str("Enter one of the source episodes name (eg: 1883_S01E01.mkv): ", pattern=r'.+S\d{2}E\d{2}.+')
    check_path_exists(os.path.join(s_path, s_name), is_file=True)
    o_name = input("Enter one of the output episodes name (leave empty if you don't want to change it): ").strip()
    if o_name == "":
        o_name = s_name
else:
    s_name = verif_str("Enter the name of the source file (eg: Back_to_the_future_(1985).mkv): ", min_length=1)
    check_path_exists(os.path.join(s_path, s_name), is_file=True)
    o_name = input("Enter the name that you want to give to the output file (leave empty if you don't want to change it): ").strip()
    if o_name == "":
        o_name = s_name

#variables in the ffmpeg command
preset = verif("Enter the preset number (goes from 12 to -1): ", -1, 12)
crf = verif("Enter the crf (goes from 50 to 0): ", 0, 50)
res = verif("Enter the resolution (eg: 1080, 720, 2160): ", 1, 4320)
dv = verif_str("Is your input file in Dolby Vision ? (yes or no): ", pattern=r'yes|no').strip()
grain = verif("Enter the grain (goes from 0 to 50): ", 0, 50)
hw = verif_str("Do you have hardware acceleration (yes or no): ", pattern=r'yes|no').strip()


#setting dolby vision
if dv == "yes":
    dlv = "-dolbyvision true "
else:
    dlv = ""

#setting hw acceleration
if hw == "yes":
    typehw = verif_str("Enter the harware acceleration (eg: cuda, rocm, qsv): ", pattern=r'cuda|rocm|qsv|vaapi|dxva2|vdpau|d3d11va|opencl').strip()
    hwa = f'-hwaccel {typehw}'
else:
    hwa = ""

#audio configuration
num_audio = verif("Enter the number of audio tracks: ", 0, 30)
audio = []
for i in range(num_audio):
    print("Enter audio configuration: ")
    track_num = verif(f'Enter the track number for track {i + 1} (Starts at 0, eg: 0, 1, 2, 43): ', 0, 30)
    channels = verif (f'Enter the number of channels of track {i + 1} (eg: stereo = 2, 5.1 = 6, 7.1 = 8): ', 1, 8)
    bitrate = verif(f'Enter the bitrate of track {i + 1} (in kbps; eg: 128, 160, 224): ', 1, 512)
    audio.append((track_num, channels, bitrate))  

#subtitles
sub_req = verif_str("Do you have subtitles ? (yes or no): ", pattern=r'yes|no')
if sub_req == 'yes':
    sub = "-map 0:s -c:s copy "
else:
    sub = ""

#ffmpeg command generation
a = 1
l = []
for i in range(files):
    if files > 1:
        num = f"{a:02}"
        new_name = s_name
        new_out = o_name
        if re.search(pattern, s_name):
            new_name = swap_num(new_name, a)
        if re.search(pattern, o_name):
            new_out = swap_num(new_out, a)
    else: 
        new_name = s_name
        new_out = o_name
    file_in = os.path.join(s_path, new_name)
    file_out = os.path.join(o_path, new_out)
    
    cmd = (f'ffmpeg {hwa} -i {file_in} -map 0:v:0 -c:v libsvtav1 -preset {preset} -crf {crf} -pix_fmt yuv420p10le -color_range full -vf "scale=-1:{res}" -svtav1-params tune=0:film-grain={grain}:film-grain-denoise=0 {dlv}')
    for j, (track_num, channels, bitrate) in enumerate(audio):
        cmd += f'-map 0:a:{track_num} -c:a:{track_num} libopus -b:a:{track_num} {bitrate}k -ac:a:{track_num} {channels} '
    cmd += sub
    cmd += f'{file_out} -y'
    l.append(cmd)
    a += 1

#pasting the command(s) in script file
with open(script, 'w') as file:
    if is_windows:
        file.write('@echo off\n\n')
    else:
        file.write('#!/bin/bash\n\n')
    for elem in l:
        file.write(elem + '\n\n')

#making the file executable
if not is_windows:
    os.chmod(script, 0o755)


#launching the command and benchmarking the time
time_ini = time.time()

try:
    subprocess.run(run_cmd + [script], check=True)
except subprocess.CalledProcessError as e:
    print(f'Error while running: {e}')

time_end = time.time() - time_ini

hours, remainder = divmod(time_end, 3600)
minutes, seconds = divmod(remainder, 60)

print(f'The encode took: {int(hours)}:{int(minutes):02}:{int(seconds):02}')
