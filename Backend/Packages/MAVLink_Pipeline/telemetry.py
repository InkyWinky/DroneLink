import copy
from dataclasses import dataclass


@dataclass
class Telemetry:
  time_stamp: int = None  # ms as integer

  # GPS data
  lat: float = None  # degE7 as integer? - lat and lon units and type need to be verified
  lon: float = None  # degE7 as integer?
  alt: int = None  # mm as integer
  heading: int = None  # cdeg as integer (range of 0.0..359.99 degrees where each 0.01 deg == 1 cdeg)

  # Attitude data
  roll: float = None  # rad as float
  pitch: float = None  # rad as float
  yaw: float = None  # rad as float

  @staticmethod
  def data_from(obj):
    return Telemetry(
      time_stamp=obj.time_stamp,
      lat=obj.lat,
      lon=obj.lon,
      alt=obj.alt,
      heading=obj.heading,
      roll=obj.__roll,
      pitch=obj.__pitch,
      yaw=obj.__yaw
    )

  def get_data(self):
    """
    Returns a copy of the current telemetry data
    :return: A deepcopy of this class
    """
    return copy.deepcopy(self)

  @staticmethod
  def get_headers_as_list():
    return ['Timestamp (ms)', 'Latitude', 'Longitude', 'Altitude (m)', 'Heading', "Roll", "Pitch", "Yaw"]

  def get_data_as_list(self):
    """
    Gets the telemetry data in a csv friendly format (header names + data values)
    """
    return [self.time_stamp, self.lat, self.lon, self.alt, self.heading, self.roll, self.pitch, self.yaw]


class TelemetryBuilder:
  def __init__(self):
    self.time_stamp = None

    # GPS data
    self.lat = None
    self.lon = None
    self.alt = None
    self.heading = None

    # Attitude data
    self.roll = None
    self.pitch = None
    self.yaw = None

  def attitude(self, attitude):
    self.time_stamp = attitude.time_boot_ms
    self.roll = attitude.__roll
    self.pitch = attitude.__pitch
    self.yaw = attitude.__yaw

  def gps(self, gps):
    self.time_stamp = gps.time_boot_ms
    self.lat = gps.lat
    self.lon = gps.lon
    self.alt = gps.alt
    self.alt_rel = gps.relative_alt
    self.heading = gps.hdg

  def is_complete(self):
    return None not in [self.time_stamp, self.lat, self.lon, self.alt, self.heading, self.roll, self.pitch, self.yaw]

  def build(self):
    return Telemetry.data_from(self)
