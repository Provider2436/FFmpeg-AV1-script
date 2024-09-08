import os
import sys
import subprocess
import time
import re
import platform
import json
import glob


# Compile regex patterns for reuse
episode_pattern = re.compile(r'(?P<season>S\d{2}E)(?P<episode>\d{2})')
show_name_pattern = re.compile(r'.+S\d{2}E\d{2}.+')
media_type_pattern = re.compile(r'movie|show')
hardware_pattern = re.compile(r'cuda|rocm|qsv|vaapi|dxva2|vdpau|d3d11va|opencl')
codec_pattern = re.compile(r'aac|libfdk_aac|libopus|ac3|ac3_fixed|eac3|flac|alac|wavpack|dca|truehd')

# Detect OS
is_windows = platform.system().lower() == 'windows'

# Script based on OS
script_ext = '.bat' if is_windows else '.sh'
run_cmd = ['cmd.exe', '/c'] if is_windows else ['bash']

# Script location
script = input(f'Enter where you want the script to be located (with the extension {script_ext}): ').strip()

# Erase script if it already exists
with open(script, 'w') as file:
    pass

def verif(inp, minn, maxx, default=None):
    while True:
        try:
            val = input(inp)
            if not val and default is not None:
                return default
            elif minn <= int(val) <= maxx:
                return val
            else:
                print(f'Enter a value between {minn} and {maxx}')
        except ValueError:
            print("Invalid input, you need to input an int")

def verif_str(inp, pattern=None, min_length=None, default=None):
    while True:
        val = input(inp).strip()
        if not val and default is not None:
            return default
        elif pattern and not pattern.match(val):
            print(f"The input must match the pattern: {pattern.pattern}")
        elif min_length and len(val) < min_length:
            print(f"The input must be at least {min_length} characters long")
        else:
            return val

def swap_num(filename, new_num):
    replacement = r'\g<season>{:02}'.format(new_num)
    new_filename = episode_pattern.sub(replacement, filename)
    return new_filename

def check_path_exists(path, is_file=False):
    while True:
        if not os.path.exists(path):
            print(f"The path '{path}' does not exist. Please enter a valid path.")
            path = input("Please re-enter the correct path: ").strip()
        elif is_file and not os.path.isfile(path):
            print(f"The path '{path}' is not a file.")
            path = input("Please re-enter the correct path: ").strip()
        elif not is_file and not os.path.isdir(path):
            print(f"The path '{path}' is not a directory.")
            path = input("Please re-enter the correct path: ").strip()
        else:
            return path

def get_color_properties(file_path):
    cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=color_space,color_transfer,color_primaries -of json "{file_path}"'
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.decode('utf-8')}")
    output = json.loads(result.stdout.decode('utf-8'))
    stream = output['streams'][0]
    color_props = {
        'color_space': stream.get('color_space'),
        'color_transfer': stream.get('color_transfer'),
        'color_primaries': stream.get('color_primaries')
    }
    return color_props

def list_audio_tracks(file_path):
    cmd = f'ffprobe -v error -select_streams a -show_entries stream=index,codec_name,channels,bit_rate -of json "{file_path}"'
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.decode('utf-8')}")
    output = json.loads(result.stdout.decode('utf-8'))
    audio_tracks = []
    for stream in output['streams']:
        track_info = {
            'index': int(stream['index'])-1,
            'codec_name': stream.get('codec_name', 'unknown'),
            'channels': stream.get('channels', 'unknown'),
            'bit_rate': int(stream.get('bit_rate', '0')) // 1000  # Convert to kbps
        }
        audio_tracks.append(track_info)
    return audio_tracks

def prompt_audio_track_selection(audio_tracks):
    print("Available audio tracks:")
    for track in audio_tracks:
        print(f"Track {track['index']}: Codec = {track['codec_name']}, Channels = {track['channels']}, Bitrate = {track['bit_rate']} kbps")
    
    selected_track = verif("Select the track number you want to copy (or enter -1 to encode audio instead): ", -1, len(audio_tracks) + 2)
    return selected_track

# Media type selection
question = verif_str('Enter the type of the media (eg: movie, show): ', pattern=media_type_pattern)
files = 1 if question == "movie" else verif('Enter the number of episodes: ', 1, 1000)

# Path validation with wildcard support
s_path = verif_str("Enter the path of the source file(s): ", min_length=1)
s_path = check_path_exists(s_path)

matched_files = []

while not matched_files:
    file_pattern = verif_str("Enter the file pattern to match (e.g., Bleach.S09E*.mkv): ", min_length=1)
    full_pattern = os.path.join(s_path, file_pattern)
    matched_files = glob.glob(full_pattern)
    if not matched_files:
        print(f"No files matched the pattern: {file_pattern}. Please try again.")

total_files = len(matched_files)
print(f"Found {total_files} files matching the pattern.")

def extract_episode_num(filename):
    match = episode_pattern.search(filename)
    if match:
        return int(match.group('episode'))
    return -1

matched_files.sort(key=extract_episode_num)

o_path = verif_str("Enter the output path of the encoded file(s): ", min_length=1)
if not os.path.exists(o_path):
    os.makedirs(o_path)

if total_files > 1:
    s_name = os.path.basename(matched_files[0])
    o_name = input("Enter one of the output episodes name (leave empty if you don't want to change it): ").strip()
    if not o_name:
        o_name = s_name
else:
    s_name = os.path.basename(matched_files[0])
    o_name = input("Enter the name that you want to give to the output file (leave empty if you don't want to change it): ").strip()
    if not o_name:
        o_name = s_name

# Variables in the ffmpeg command
preset = verif("Enter the preset number (default: 3): ", -1, 12, 3)
crf = verif("Enter the crf (default: 27): ", 0, 50, 27)
res = verif("Enter the resolution (default: 1080): ", 1, 4320, 1080)
grain = verif("Enter the grain (default: 0): ", 0, 50, 0)
dv = verif_str("Is your input file in Dolby Vision ? (yes or no) (default is no): ", pattern=re.compile(r'yes|no'), default='no')
hw = verif_str("Do you have hardware acceleration (yes or no) (default is no): ", pattern=re.compile(r'yes|no'), default='no')

# Setting Dolby Vision
dlv = "-dolbyvision true " if dv == "yes" else ""

# Setting hardware acceleration
if hw == "yes":
    typehw = verif_str("Enter the hardware acceleration (eg: cuda, rocm, qsv): ", pattern=hardware_pattern)
    hwa = f'-hwaccel {typehw}'
else:
    hwa = ""

# Audio configuration using ffprobe
audio_tracks = list_audio_tracks(os.path.join(s_path, s_name))
audio_cmd = ''
for i in range(len(audio_tracks)):
    selected_track = int(prompt_audio_track_selection(audio_tracks))
    print(audio_cmd)
    if selected_track != -1:
        track_to_copy = audio_tracks[selected_track]
        audio_cmd += f'-map 0:a:{track_to_copy["index"]} -c:a:{track_to_copy["index"]} copy '
    else:
        num_audio = verif("Enter the number of audio tracks: ", 0, 30)
        audio = []
        for i in range(int(num_audio)):
            print("Enter audio configuration: ")
            track_num = verif(f'Enter the track number {i+1} (track 1 = 0, track 2 = 1, ...): ', 0, 30)
            codec = verif_str("Enter the audio codec (eg: aac, libopus, ac3, eac3): ", pattern=codec_pattern)
            bitrate = verif('Enter the audio bitrate (eg: 128, 192, 224, 256, ...): ', 8, 1024)
            channels = verif("Enter the number of channels (1 to 8, 1 = mono, 2 = stereo, 6 = 5.1, 8 = 7.1): ", 1, 8)
            audio.append(f'-map 0:a:{track_num} -c:a:{track_num} {codec} -b:a:{track_num} {bitrate}k -ac:a:{track_num} {channels} ')
        audio_cmd += ' '.join(audio)
        break

# Subtitles
sub_req = verif_str("Do you have subtitles ? (yes or no) (default is no): ", pattern=re.compile(r'yes|no'), default='no')
if sub_req == 'yes':
    sub = "-map 0:s -c:s copy"
else:
    sub = ""

# Summary before execution
settings_summary = f"""
Summary of your settings:
Input Path: {s_path}
Output Path: {o_path}
Preset: {preset}
CRF: {crf}
Resolution: {res}
Grain: {grain}
Dolby Vision: {dlv}
Hardware Acceleration: {hwa}
Audio Configuration: {audio_cmd}
Subtitles: {sub}
"""
print(settings_summary)
confirm = verif_str("Do you want to proceed with these settings? (yes/no): ", pattern=re.compile(r'yes|no'))
if confirm != 'yes':
    os.execv(sys.executable, ['python'] + sys.argv)

# Writing the script file
with open(script, 'w') as file:
    if is_windows:
        file.write('@echo off\n\n')
    else:
        file.write('#!/bin/bash\n\n')
    for i, source_file in enumerate(matched_files):
        color_props = get_color_properties(source_file)
        episode_number = extract_episode_num(source_file)
        output_file = swap_num(o_name, episode_number)
        output_file_path = os.path.join(o_path, output_file)
        ffmpeg_command = (f'ffmpeg {hwa} -i "{source_file}" -map 0:v:0 -c:v libsvtav1 -preset {preset} -crf {crf} -pix_fmt yuv420p10le {dlv}-vf "scale=-1:{res}" -svtav1-params tune=0:film-grain={grain}:film-grain-denoise=0 ')
        
        if color_props['color_space']:
            ffmpeg_command += f'-colorspace {color_props["color_space"]} '
        if color_props['color_transfer']:
            ffmpeg_command += f'-color_trc {color_props["color_transfer"]} '
        if color_props['color_primaries']:
            ffmpeg_command += f'-color_primaries {color_props["color_primaries"]} '
        
        ffmpeg_command += (f'{audio_cmd}{sub} "{output_file_path}" -y' '\n' '\n')
        file.write(ffmpeg_command)

# Making the file executable on Linux/MacOS
if not is_windows:
    os.chmod(script, 0o755)
print(f"Script '{script}' generated successfully.")

start_time = time.time()  # Start the timer

try:
    subprocess.run(run_cmd + [script], check=True)
except subprocess.CalledProcessError as e:
    print(f'Error while running: {e}')
# End of the timer
end_time = time.time()
total_time = end_time - start_time
hours, remainder = divmod(total_time, 3600)
minutes, seconds = divmod(remainder, 60)
print(f"\nEncoding completed in {int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds.")
