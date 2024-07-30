# ffmpeg-AV1-script

## Overview

`ffmpeg-encoder` is a script designed to batch encode video files using FFmpeg with SVT-AV1 and customizable parameters. It supports both Windows and Unix-based systems and can handle encoding for both movies and TV show episodes. This repository contains scripts to install the latest versions of ffmpeg on both Windows and Unix-based systems.

## Requirements

- **Python 3.x**: Ensure Python 3 is installed on your system.
- **FFmpeg**: FFmpeg must be installed and accessible in your system's PATH.
  - For **Windows users**: `cmd.exe` must be available.
  - For **Unix-based users**: `bash` must be available.

## Installation

### Clone the Repository

```sh
git clone https://github.com/yourusername/ffmpeg-batch-encoder.git
cd ffmpeg-batch-encoder
```

## Install FFmpeg

### Windows

Run the `install_ffmpeg.bat` script to download and install FFmpeg:

```bat
install_ffmpeg.bat
```

### Unix-based Systems

Run the `install_ffmpeg.sh` script to download and install FFmpeg:

```sh
bash install_ffmpeg.sh
```

## Usage

### Run the Encoding Script

```sh
python3 ffmpeg-encoder.py
```

### Follow the Prompts

1. **Script Location**: Enter the path where you want the generated script to be saved (with the appropriate extension).
2. **Media Type**: Specify whether you are encoding a movie or a show.
3. **Source Path**: Provide the directory path containing your source video files.
4. **Output Path**: Enter the directory path where you want to save the encoded files.
5. **File Names**:
   - Enter the specific file names for both source and output files.
   - Leave the output name blank to keep the original name.
6. **Encoding Parameters**: Provide values for various FFmpeg encoding options such as preset, CRF, resolution, Dolby Vision, grain, and hardware acceleration.
7. **Audio Configuration**: Specify the number of audio tracks, channels, and bitrate.
8. **Subtitles**: Indicate whether your video files contain subtitles.

## Configuration Options

- **Media Type**: Choose between **movie** or **show**. If show is selected, you'll need to provide the number of episodes.
- **Paths**
  - **Source Path**: Directory containing the video files to encode.
  - **Output Path**: Directory where encoded files will be saved.
- **File Names**:
  - **Source file name** (e.g., Back_to_the_future_(1985).mkv).
  - **Output file name** (optional; leave empty to use the source file name).
- **Encoding Parameters**:
  - **Preset**: Integer value from -1 to 12.
  - **CRF**: Integer value from 0 to 50.
  - **Resolution**: Integer value (e.g., 1080, 720, 2160).
  - **Dolby Vision**: `Yes` or `No`.
  - **Grain**: Integer value from 0 to 50.
  - **Hardware Acceleration**: `Yes` or `No`. If Yes, specify the type (e.g., cuda, rocm, qsv)
  - **Audio Configuration**: Number of audio tracks, channels per track, and bitrate per track.
  - **Subtitles**: Indicate whether subtitles are present (yes or no).
### Example Run

```sh
python3 ffmpeg-encoder.py
```
### Sample Inputs

```txt
Enter where you want the script to be located (with the extension .sh): batch_encode.sh
Enter the type of the media (e.g., movie, show): show
Enter the number of episodes: 10
Enter the path of the source file(s): /path/to/source
Enter the output path of the encoded file(s): /path/to/output
Enter one of the source episodes name (e.g., 1883_S01E01.mkv): 1883_S01E01.mkv
Enter one of the output episodes name (leave empty if you don't want to change it):
Enter the preset number (goes from 12 to -1): 8
Enter the CRF (goes from 50 to 0): 23
Enter the resolution (e.g., 1080, 720, 2160): 1080
Is your input file in Dolby Vision? (yes or no): no
Enter the grain (goes from 0 to 50): 10
Do you have hardware acceleration (yes or no): yes
Enter the hardware acceleration (e.g., cuda, rocm, qsv): cuda
Enter the number of audio tracks: 1
Enter audio configuration:
Enter the track number for track 1 (Starts at 0, e.g., 0, 1, 2, 43): 0
Enter the number of channels of track 1 (e.g., stereo = 2, 5.1 = 6, 7.1 = 8): 2
Enter the bitrate of track 1 (in kbps; e.g., 128, 160, 224): 128
Do you have subtitles? (yes or no): yes
```
## Output

The script generates and runs a batch script (.bat for Windows or .sh for Unix-based systems) with FFmpeg commands tailored to the provided inputs. The duration of the encoding process will be displayed upon completion.

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/Provider2436/ffmpeg-Av1-script/blob/main/LICENSE) file for details.

## Contributing
Feel free to fork the repository, create a new branch, and submit a pull request with your enhancements. Issues and feature requests are also welcome.
