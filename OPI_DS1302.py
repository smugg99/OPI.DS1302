import time
import datetime
import OPi.GPIO as GPIO


class DS1302:
    CLK_DELAY = 5E-6

    def __init__(self, clk_pin, data_pin, ce_pin):
        GPIO.setwarnings(False)
        GPIO.setboard(GPIO.H616)
        GPIO.setmode(GPIO.BOARD)

        self._clk_pin = clk_pin
        self._data_pin = data_pin
        self._ce_pin = ce_pin

        GPIO.setup(self._clk_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self._ce_pin, GPIO.OUT, initial=GPIO.LOW)

        self._initialize_rtc()

    def _initialize_rtc(self):
        self._start_tx()
        self._write_byte(0x8e, 0x00)
        self._end_tx()

        self._start_tx()
        self._write_byte(0x90, 0x00)
        self._end_tx()

    def _start_tx(self):
        GPIO.output(self._clk_pin, GPIO.LOW)
        GPIO.output(self._ce_pin, GPIO.HIGH)

    def _end_tx(self):
        GPIO.setup(self._data_pin, GPIO.IN)
        GPIO.output(self._clk_pin, GPIO.LOW)
        GPIO.output(self._ce_pin, GPIO.LOW)

    def _read_byte(self):
        GPIO.setup(self._data_pin, GPIO.IN)
        byte = 0

        for i in range(8):
            GPIO.output(self._clk_pin, GPIO.HIGH)
            time.sleep(self.CLK_DELAY)

            GPIO.output(self._clk_pin, GPIO.LOW)
            time.sleep(self.CLK_DELAY)

            bit = GPIO.input(self._data_pin)
            byte |= (bit << i)
        return byte

    def _write_byte(self, command, byte):
        GPIO.setup(self._data_pin, GPIO.OUT)

        for _ in range(8):
            GPIO.output(self._clk_pin, GPIO.LOW)
            time.sleep(self.CLK_DELAY)

            GPIO.output(self._data_pin, byte & 0x01)
            byte >>= 1

            GPIO.output(self._clk_pin, GPIO.HIGH)
            time.sleep(self.CLK_DELAY)

    def _read_burst(self, command):
        self._start_tx()
        self._write_byte(command, 0x00)

        byte_list = [self._read_byte() for _ in range(31)]
        self._end_tx()

        return bytearray(byte_list)

    def _write_burst(self, command, data):
        self._start_tx()
        self._write_byte(command, 0x00)

        for i in range(min(len(data), 31)):
            self._write_byte(data[i], 0x00)  # Use data[i] instead of command
        self._end_tx()

    def read_ram(self):
        return self._read_burst(0xff)

    def write_ram(self, data):
        self._write_burst(0xfe, data)

    def read_datetime(self):
        byte_list = self._read_burst(0xbf)

        return self._decode_datetime(byte_list)

    def write_datetime(self, dt):
        byte_list = self._encode_datetime(dt)
        self._write_burst(0xbe, byte_list)

    @staticmethod
    def close():
        GPIO.cleanup()

    def _encode_datetime(self, dt):
        year = dt.year - 2000
        month = dt.month
        day = dt.day
        hour = dt.hour
        minute = dt.minute
        second = dt.second

        # DS1302 encoding format
        encoded_bytes = [
            self._encode_bcd(year),
            self._encode_bcd(month),
            self._encode_bcd(day),
            self._encode_bcd(hour),
            self._encode_bcd(minute),
            self._encode_bcd(second),
            0x00,  # Placeholder for other relevant data
        ]

        return bytes(encoded_bytes)

    def _encode_bcd(self, value):
        tens = value // 10
        ones = value % 10
        return (tens << 4) | ones
    
    def _decode_datetime(self, byte_list):
        # Assuming DS1302 encoding format
        year = self._decode_bcd(byte_list[0]) + 2000
        month = self._decode_bcd(byte_list[1])  # No bitmask
        day = self._decode_bcd(byte_list[2])
        hour = self._decode_bcd(byte_list[3])
        minute = self._decode_bcd(byte_list[4])
        second = self._decode_bcd(byte_list[5])

        return datetime.datetime(year, month, day, hour, minute, second)

    def _decode_bcd(self, value):
        tens = (value >> 4) & 0x0F
        ones = value & 0x0F
        return tens * 10 + ones