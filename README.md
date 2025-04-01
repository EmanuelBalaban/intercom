# Intelligent Intercom Electra IA01

This is a custom thermostat built for the [GroundStudio Carbon S2](https://github.com/GroundStudio/GroundStudio_Carbon_S2/tree/main) board.

See the official documentation for ESP32 and MicroPython [here](https://docs.micropython.org/en/latest/esp32/quickref.html#).

## IDE

The best IDE to use with MicroPython is PyCharm in combination with MicroPython plugin. Just know you will need to setup
it before it can be used:

![MicroPython Plugin Settings](assets/micro_python_plugin_setup.png)

To use vscode read this article: https://micropython-stubs.readthedocs.io/en/main/22_vscode.html

## Virtual env

Install virtualenv:

```shell
pip install virtualenv;
```

Create a virtual env called `.venv` in the current directory:

```shell
virtualenv .venv
```

Activate the venv:

```shell
.\.venv\Scripts\activate
```

Install the requirements from `requirements.txt` file:

```shell
pip --require-virtualenv install -r requirements.txt
```

### For linux users

```shell
source .venv/bin/activate
```

## Optimizing (external) libraries

To optimize the libraries (external or internal), mpy-cross command line tool is used. To install it, use pip:

```shell
pip install mpy-cross
```

To use it, run the CLI tool:

```shell
mpy-cross file.py
```

This will output a .mpy file which is the compiled version of the .py file. 
Upload this to the microcontroller instead of the original one to preserve space and computation power.

Place the newly created files into mpy_libraries directory so you can upload all of them using ampy command (see below).

## Working with files on the microcontroller

To work with files we can use ampy CLI tool.

### How to copy files to the microcontroller?

```shell
ampy -p COM5 put /mpy_libraries /libraries
```

This command can be used for regular files also (not only MPY).

PyCharm also automatically uploads boot.py when you run the file from the run button.

### How to list files on the microcontroller?

```shell
ampy -p COM5 ls
```

## References

- https://github.com/kind3r/electra-esp32-analog
