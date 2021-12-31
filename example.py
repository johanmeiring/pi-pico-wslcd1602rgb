import machine
import utime
from wslcd1602rgb import WSLCD1602RGB

sda = machine.Pin(0)
scl = machine.Pin(1)
i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)

lcd = WSLCD1602RGB(i2c)
lcd.set_rgb(0, 128, 255)

count = 0
while True:
    count += 1
    time = utime.localtime()
    formatted = "{year:>04d}/{month:>02d}/{day:>02d} {HH:>02d}:{MM:>02d}".format(
        year=time[0], month=time[1], day=time[2],
        HH=time[3], MM=time[4])

    lcd.print_lines(formatted, "Counter " + str(count))
    utime.sleep_ms(1000)
