

import threading
import time

import cv2

import CubeConnection
from main import main

VIDEO_DEVICE = 0

class Camera:
  def __init__(self):
    self.stopped = False
    self.frame = None

    self.capture = cv2.VideoCapture(VIDEO_DEVICE)

    self.thread = threading.Thread(target=self.update, args=(), daemon=True)
    self.thread.start()

  def __del__(self):
    self.stopped = True
    self.capture.release()
    self.thread.join()

  def update(self):
    while not self.stopped:
      if self.capture.isOpened():
        (self.status, self.frame) = self.capture.read()

      time.sleep(.01)

  def take_picture(self):
    return (True, self.frame)

def process_image(img, coords):
  return coords

camera = Camera()

class CubeConnection(CubeConnection.CubeConnection):
  def _pin_state(self):
    return input() == "1"

main(
  cube_connection=CubeConnection(),
  take_picture=camera.take_picture,
  process_image=process_image
)
