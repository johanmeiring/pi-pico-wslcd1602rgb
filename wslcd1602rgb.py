import utime
import gc

# https://www.waveshare.com/lcd1602-rgb-module.htm
# https://www.waveshare.com/w/upload/2/2e/LCD1602_RGB_Module.pdf

# Default device I2C Address.
LCD_ADDRESS = (0x7c >> 1)
RGB_ADDRESS = (0xc0 >> 1)

LCD_NUM_LINES = 2
LCD_NUM_COLUMNS = 16

# RGB Driver: PCA9633
# https://files.seeedstudio.com/wiki/Grove_LCD_RGB_Backlight/res/PCA9633.pdf
# RGB commands and addresses.
RGB_RED = 0x04
RGB_GREEN = 0x03
RGB_BLUE = 0x02
RGB_MODE1 = 0x00
RGB_MODE2 = 0x01
RGB_OUTPUT = 0x08

# LCD Controller: AiP31068 (or equivalent).
# https://www.newhavendisplay.com/resources_dataFiles/datasheets/LCDs/AiP31068.pdf
# LCD commands and addresses.
LCD_SET_CGRAM_ADDR = 0x40  # Address for data.
LCD_SET_DDRAM_ADDR = 0x80  # Address for commands.
LCD_CLEAR_DISPLAY = 0x01
LCD_RETURN_HOME = 0x02

# Display entry mode command and flags.
LCD_ENTRY_MODE_SET = 0x04
LCD_ENTRY_RIGHT = 0x00
LCD_ENTRY_LEFT = 0x02
LCD_ENTRY_SHIFT_INCREMENT = 0x01
LCD_ENTRY_SHIFT_DECREMENT = 0x00

# Display on/off command and flags.
LCD_DISPLAY_CONTROL = 0x08
LCD_DISPLAY_ON = 0x04
LCD_DISPLAY_OFF = 0x00
LCD_CURSOR_ON = 0x02
LCD_CURSOR_OFF = 0x00
LCD_BLINK_ON = 0x01
LCD_BLINK_OFF = 0x00

# Display/cursor shift command and flags.
LCD_CURSOR_SHIFT = 0x10
LCD_DISPLAY_MOVE = 0x08
LCD_CURSOR_MOVE = 0x00
LCD_MOVE_RIGHT = 0x04
LCD_MOVE_LEFT = 0x00

# Function set command and flags.
LCD_FUNCTION_SET = 0x20
LCD_FUNCTION_RESET = 0x30
LCD_8BIT_MODE = 0x10
LCD_4BIT_MODE = 0x00
LCD_2_LINE = 0x08
LCD_1_LINE = 0x00
LCD_5x10_DOTS = 0x04
LCD_5x8_DOTS = 0x00


class WSLCD1602RGB():
    def __init__(self, i2c, lcd_address=LCD_ADDRESS, rgb_address=RGB_ADDRESS):
        self._i2c = i2c
        self._lcd_address = lcd_address
        self._rgb_address = rgb_address

        # Init
        utime.sleep_ms(50)

        # Init display.
        self.write_command(LCD_FUNCTION_SET | LCD_FUNCTION_RESET)
        init_command = LCD_8BIT_MODE | LCD_5x8_DOTS | LCD_2_LINE
        # Do this 4 times as part of init sequence.
        self.write_command(LCD_FUNCTION_SET | init_command)
        utime.sleep_ms(5)
        self.write_command(LCD_FUNCTION_SET | init_command)
        utime.sleep_ms(5)
        self.write_command(LCD_FUNCTION_SET | init_command)
        self.write_command(LCD_FUNCTION_SET | init_command)

        self.display_off()
        self.clear()
        self.hide_cursor()
        self.display_on()

        # Set entry mode (default text direction).
        self.write_command(LCD_ENTRY_MODE_SET |
                           LCD_ENTRY_LEFT | LCD_ENTRY_SHIFT_DECREMENT)

        # Init RGB backlight.
        self.set_rgb_reg(RGB_MODE1, 0)
        # set LEDs controllable by both PWM and GRPPWM registers
        self.set_rgb_reg(RGB_OUTPUT, 0xFF)
        # set MODE2 values
        # 0010 0000 -> 0x20  (DMBLNK to 1, ie blinky mode)
        self.set_rgb_reg(RGB_MODE2, 0x20)
        self.set_colour_white()

        gc.collect()

    def write_command(self, command):
        self._i2c.writeto_mem(
            self._lcd_address, LCD_SET_DDRAM_ADDR, chr(command))

    def write_data(self, data):
        self._i2c.writeto_mem(self._lcd_address, LCD_SET_CGRAM_ADDR, chr(data))

    def clear(self):
        self.write_command(LCD_CLEAR_DISPLAY)
        self.write_command(LCD_RETURN_HOME)

    def home(self):
        self.write_command(LCD_RETURN_HOME)

    def show_cursor(self):
        self.write_command(LCD_DISPLAY_CONTROL |
                           LCD_DISPLAY_ON | LCD_CURSOR_ON)

    def hide_cursor(self):
        self.write_command(LCD_DISPLAY_CONTROL |
                           LCD_DISPLAY_ON | LCD_CURSOR_OFF)

    def blink_cursor_on(self):
        self.write_command(LCD_DISPLAY_CONTROL | LCD_DISPLAY_ON |
                           LCD_CURSOR_ON | LCD_BLINK_ON)

    def blink_cursor_off(self):
        self.write_command(LCD_DISPLAY_CONTROL |
                           LCD_DISPLAY_ON | LCD_CURSOR_ON)

    def display_on(self):
        self.write_command(LCD_DISPLAY_CONTROL | LCD_DISPLAY_ON)

    def display_off(self):
        self.write_command(LCD_DISPLAY_CONTROL | LCD_DISPLAY_OFF)

    def set_rgb_reg(self, reg, data):
        self._i2c.writeto_mem(self._rgb_address, reg, chr(data))

    def set_rgb(self, red, green, blue):
        self.set_rgb_reg(RGB_RED, red)
        self.set_rgb_reg(RGB_GREEN, green)
        self.set_rgb_reg(RGB_BLUE, blue)

    def set_colour_white(self):
        self.set_rgb(255, 255, 255)

    def print_out(self, string):
        if (isinstance(string, int)):
            string = str(string)

        for x in bytearray(string, 'utf-8'):
            self.write_data(x)

    def print_lines(self, line1, line2):
        self.home()
        # The following prevents weird cursor shifting behaviour on the first line.
        self.write_command(LCD_FUNCTION_SET | LCD_8BIT_MODE |
                           LCD_5x8_DOTS | LCD_2_LINE)

        self.print_out(line1)

        # Move cursor to next line and shift left twice. Annoying.
        self.write_command(LCD_SET_DDRAM_ADDR)
        self.write_command(LCD_CURSOR_SHIFT | LCD_MOVE_LEFT)
        self.write_command(LCD_CURSOR_SHIFT | LCD_MOVE_LEFT)
        self.print_out(line2)

    # Todo: Implement and test this properly.
    # def custom_char(self, location, charmap):
        # Write a character to one of the 8 CGRAM locations, available
        # as chr(0) through chr(7).
    #    location &= 0x7
    #    self.write_command(LCD_SET_CGRAM_ADDR | (location << 3))
    #    utime.sleep_us(40)
    #    for i in range(8):
    #        self.write_data(charmap[i])
    #        utime.sleep_us(40)
    #    self.move_to(self.cursor_x, self.cursor_y)
