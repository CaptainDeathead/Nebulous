import RPi.GPIO as GPIO
import time

# Use BCM numbering
GPIO.setmode(GPIO.BCM)

# Set up GPIO 14 as input with pull-down resistor
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        if GPIO.input(14):
            print("Plug is inserted!")
        else:
            print("Plug is NOT inserted.")
        time.sleep(0.2)  # check 5 times per second
finally:
    GPIO.cleanup()
