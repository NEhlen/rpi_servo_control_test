# Set up libraries and overall settings
import RPi.GPIO as GPIO  # Imports the standard Raspberry Pi GPIO library
from time import sleep  # Imports sleep (aka wait or pause) into the program

GPIO.setmode(GPIO.BOARD)  # Sets the pin numbering system to use the physical layout

# Set up pin 11 for PWM
GPIO.setup(11, GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)
GPIO.setup(12, GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)
p = GPIO.PWM(11, 50)  # Sets up pin 11 as a PWM pin
p2 = GPIO.PWM(12, 50)  # Sets up pin 11 as a PWM pin
p.start(0)  # Starts running PWM on the pin and sets it to 0
p2.start(0)
# Move the servo back and forth
p.ChangeDutyCycle(5)  # Changes the pulse width to 2 (so moves the servo)
sleep(1)  # Wait 1 second
p.ChangeDutyCycle(9)  # Changes the pulse width to 12  (so moves the servo)
sleep(1)
p.ChangeDutyCycle(7)  # Changes the pulse width to 7  (so moves the servo)
sleep(1)
p2.ChangeDutyCycle(5)  # Changes the pulse width to 2 (so moves the servo)
sleep(1)  # Wait 1 second
p2.ChangeDutyCycle(9)  # Changes the pulse width to 7  (so moves the servo)
sleep(1)
p2.ChangeDutyCycle(7)  # Changes the pulse width to 7  (so moves the servo)
sleep(1)

# Clean up everything
p.stop()  # At the end of the program, stop the PWM
p2.stop()
GPIO.cleanup()  # Resets the GPIO pins back to defaults
