Installation
============
1.  Clone the repository:
    ```bash
    git clone https://github.com/ryanfitzsimon/sensorlog
    ```

2.  Connect the sensors to the Raspberry Pi GPIO headers.

| OPC Pin | Function | RPi Pin |
|---------|----------|---------|
|    1    |    5 V   |    4    |
|    2    |    CLK   |   23    |
|    3    |   MISO   |   21    |
|    4    |   MOSI   |   19    |
|    5    |    CE0   |   24    |
|    6    |    GND   |   25    |

3.  Ensure that the required devices are enabled in the device tree. The following line should be present in `/boot/config.txt`
    ```
    dtparam=spi=on
    ```
4.  Run the install script:
    ```bash
    cd sensorlog
    ./install.sh
    ```

    This will install the required python modules, add udev rules to allow access to the required devices and create a symlink to sensorlog in `/usr/local/bin`.

Running Sensorlog
=================
```bash
usage: sensorlog.py [-h] [-l logfile] [-t period] [-v]
```
Select the logfile location using `-l`. The default is `opc-log.csv`.

The period in seconds can be set using `-t`.

Verbose mode can be enabled with the `-v` flag. In verbose mode, each line written to the logfile will also be printed to stdout.

Uninstallation
==============
Simply run the provided uninstall.sh script.
```bash
./uninstall.sh
```
Note that this only undoes the actions performed by the install.sh script. It will not remove any python modules or modify device tree settings.
