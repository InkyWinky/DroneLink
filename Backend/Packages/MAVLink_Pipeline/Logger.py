import csv
import os
from datetime import datetime, timedelta
import time

import cv2

from .telemetry import Telemetry


class FileLogger:
  file = None

  def __init__(self, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    self.file = open(file_path, "w", encoding="UTF8")

    self.writer = csv.writer(self.file)

  def __del__(self):
    if self.file is not None: self.file.close()


class TelemetryLogger(FileLogger):
  """
  Class for logging the vehicle's telemetry data into a csv file
  Will print log file as date_vehicleName.csv, additional logs within that data will be appended
  """
  def __init__(self, start_time=datetime.now().strftime("%H-%M-%S")):
    date_str = datetime.today().strftime("%Y-%m-%d")
    file_path = f"logs/{date_str}_Flight_{start_time}.csv"
    super().__init__(file_path)

    headers = ['Time'] + Telemetry.get_headers_as_list()
    self.writer.writerow(headers)
    self.last_write = datetime.now()

    self.data = []

  def __del__(self):
    self._write_data_to_file()

  def _write_data_to_file(self):
    print("Writing logs to file ...")
    self.writer.writerows(self.data)
    self.data = []

  def log_data(self, telem):
    data_values = telem.get_data_as_list()
    print("Logging data", data_values)

    time_str = datetime.now().strftime('%H:%M:%S')
    self.data.append([time_str] + data_values)

    # Write data to file periodically
    if self.last_write + timedelta(minutes=1) <= datetime.now():
      self._write_data_to_file()
      self.last_write = datetime.now()


class ImageLogger:
  def __init__(self, start_time=datetime.now().strftime("%H-%M-%S")):
    date_str = datetime.today().strftime("%Y-%m-%d")
    self.dir_path = f"logs/image/{date_str}_Flight_{start_time}"
    os.makedirs(self.dir_path, exist_ok=True)

  def log_data(self, img, telem):
    now_time = datetime.now().strftime("%H-%M-%S")
    timestamp = time.time()
    file_name = f"capture_{now_time}_{timestamp}"

    # Write image data
    cv2.imwrite(f"{self.dir_path}/{file_name}.png", img)

    # Write gps data
    with open(f"{self.dir_path}/{file_name}.csv", "w") as data_file:
      writer = csv.writer(data_file)
      writer.writerow(Telemetry.get_headers_as_list())
      writer.writerow(telem.get_data_as_list())

    print(f"Logged image data captured at {now_time}")
