# OPI.DS1302
Simple Python module to deal with DS1302 RTC on Orange Pi

### Wire map (default conf.)

| Chip        | Rpi pin       |
| ----------- |:-------------:|
| VCC         | 3.3v pin      |
| GND         | GND pin       |
| CLK         | pin 11        |
| DATA        | pin 13        |
| CE (RST)    | pin 15        |

### Setup

    sudo apt-get -y install python3-rpi.gpio
    sudo python3 setup.py install