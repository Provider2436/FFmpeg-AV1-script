#!/bin/bash

# Define the URL and file name
URL="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
FILE="ffmpeg-master-latest-linux64-gpl.tar.xz"
DIR="ffmpeg-master-latest-linux64-gpl"

# Check if ffmpeg is running
if pgrep -x "ffmpeg" > /dev/null; then
    echo "FFmpeg is running. Exiting."
    exit 1
fi

# Download the latest FFmpeg build
wget -O $FILE $URL

# Extract the tar file
tar -xvf $FILE

# Copy the binaries to /usr/local/bin
sudo cp $DIR/bin/* /usr/local/bin/

# Clean up
rm -rf $FILE $DIR

echo "FFmpeg has been updated successfully."

