import logging

from time import time

try:
    import RPi.GPIO as GPIO
    TESTING = False
except:
    class GPIO:
        @staticmethod
        def setup(a, b, pull_up_down=0) -> None:
            return None
    
        @staticmethod
        def input(a) -> bool:
            return False
        
        @staticmethod
        def output(a, b) -> None: ...
        
        @staticmethod
        def cleanup() -> None: ...

class IOManager:
    CONSOLE_FRONT_POWER_PIN = 3
    CONSOLE_STATUS_LED_PIN = 4

    ERROR_BLINK_INTEVAL = 0.3

    LED_STATUS_INFO = {
        "off": 0,
        "on": 1,
        "err": 2
    }

    def __init__(self, testing: bool, final_console_shutdown) -> None:
        self.testing = testing
        self.final_console_shutdown = final_console_shutdown

        if not self.testing:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.CONSOLE_FRONT_POWER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(self.CONSOLE_STATUS_LED_PIN, GPIO.OUT)
        else:
            logging.warning("Console in testing mode so console io is spoofed!")

        self.last_led_blink = 0
        self.err_led_on = False

        self.desired_led_status = 0
        self.led_status = -1

    def show_error(self) -> None:
        self.desired_led_status = self.LED_STATUS_INFO["err"]

    def set_led_on(self) -> None:
        self.desired_led_status = self.LED_STATUS_INFO["on"]

    def set_led_off(self) -> None:
        self.desired_led_status = self.LED_STATUS_INFO["off"]

    def shutdown_console(self) -> None:
        logging.debug("Shutting down all RPi.GPIO pins...")
        GPIO.cleanup()

        self.final_console_shutdown()

    def update(self) -> None:
        front_switch_on = not GPIO.input(self.CONSOLE_FRONT_POWER_PIN)

        if front_switch_on:
            logging.info("Console IO detected front switch off! Console powering off now :)")        
            self.shutdown_console()

        if self.desired_led_status == self.LED_STATUS_INFO["on"]:
            if self.led_status != self.desired_led_status:
                GPIO.output(self.CONSOLE_STATUS_LED_PIN, True)
                self.led_status = self.desired_led_status

        elif self.desired_led_status == self.LED_STATUS_INFO["off"]:
            if self.led_status != self.desired_led_status:
                GPIO.output(self.CONSOLE_STATUS_LED_PIN, False)
                self.led_status = self.desired_led_status
            
        else:
            self.led_status = self.desired_led_status

            if time() - self.last_led_blink:
                self.err_led_on = not self.err_led_on
                GPIO.output(self.CONSOLE_STATUS_LED_PIN, self.err_led_on)

                self.last_led_blink = time()