import RPi.GPIO as GPIO

from .CubeConnection import CubeConnection

TRIGGER_IMAGE_PIN = 15

class CubeGPIOConnection(CubeConnection):
  def __init__(self):
    # Setup GPIO
    GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme
    GPIO.setup(TRIGGER_IMAGE_PIN, GPIO.IN)  # button pin set as input

    super()

  def _pin_state(self):
    return GPIO.input(TRIGGER_IMAGE_PIN)
