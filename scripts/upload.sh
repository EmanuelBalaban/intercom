#!/bin/bash

# Get the name of the current directory
current_dir=$(basename "$PWD")

# If we're in the 'scripts' directory, go up one level
if [ "$current_dir" == "scripts" ]; then
    cd ..
fi

# Compile the files
echo "Compiling files..."
mpy-cross src/intercom.py -o src-mpy/intercom.mpy
mpy-cross src/led.py -o src-mpy/led.mpy
mpy-cross src/mqtt_handler.py -o src-mpy/mqtt_handler.mpy
mpy-cross src/utils.py -o src-mpy/utils.mpy

# Upload compiled files to ESP32
echo "Uploading compiled files..."
cd src-mpy || exit
ampy -p /dev/ttyACM0 put intercom.mpy
ampy -p /dev/ttyACM0 put led.mpy
ampy -p /dev/ttyACM0 put mqtt_handler.mpy
ampy -p /dev/ttyACM0 put utils.mpy

# Upload other source files
echo "Uploading config.py, boot.py, and main.py..."
cd ../src || exit
ampy -p /dev/ttyACM0 put config.py
ampy -p /dev/ttyACM0 put boot.py
ampy -p /dev/ttyACM0 put main.py

echo "Upload complete."
