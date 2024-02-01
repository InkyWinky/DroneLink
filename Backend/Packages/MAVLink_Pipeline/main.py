from datetime import datetime
from .Logger import ImageLogger, FileLogger, TelemetryLogger
from typing import Callable, Tuple, Any

from pymavlink import mavutil

from .CubeConnection import CubeConnection
from .telemetry import TelemetryBuilder


def main(
  cube_connection: CubeConnection,
  take_picture: Callable[[], Tuple[bool, Any]],
  process_image
):
  filters = {
    "ATTITUDE": mavutil.mavlink.MAVLink_attitude_message,
    "GLOBAL_POSITION_INT": mavutil.mavlink.MAVLink_global_position_int_message
  }

  start_time = datetime.now().strftime('%H-%M-%S')

  # Telemetry from cube
  # Data comes in batches of message types that have to be collated
  # into one telemetry data for the purpose of logging and gv.
  telem_builder = TelemetryBuilder()

  # Logging
  telem_logger = TelemetryLogger(start_time=start_time)
  img_logger = ImageLogger(start_time=start_time)

  # None value indicates waiting for next image
  # False values indicate a frame error and so image should be ignore for current batch
  current_image = None
  # None value indicates new batch of data; there is always a timestamp in the message
  current_timestamp = None
  try:
    while True:
      msg = cube_connection.next_message(filters=list(filters.keys()))

      # Received new batch of telemetry data but previous data was not processed
      if current_timestamp is not None and current_timestamp != msg.time_boot_ms:
        telem_logger.log_data(telem_builder.build())

        # Reset to record next batch of telemetry data
        current_image = current_timestamp = None
        telem_builder = TelemetryBuilder()

      # Record data for new batch of telemetry data
      if current_timestamp is None: current_timestamp = msg.time_boot_ms
      if current_image is None:
        ret, current_image = take_picture()
        if not ret:
          current_image = []

      # Parse incoming message by types
      if isinstance(msg, filters["ATTITUDE"]):
        telem_builder.attitude(msg)
      elif isinstance(msg, filters["GLOBAL_POSITION_INT"]):
        telem_builder.gps(msg)
      else:
        print("Unhandled message", msg)
        # Skip processing for unhandled messages
        continue

      # Received all the telemetry data required
      if telem_builder.is_complete():
        telem = telem_builder.build()
        telem_logger.log_data(telem)

        # Process data and image if there was a trigger
        if (
          cube_connection.process_trigger()
          # There is an image
          and current_image is not None
          and len(current_image) > 0
        ):
          coords = process_image(img=current_image, coords=[telem.lat, telem.lon])
          print(f"Target found {telem.time_stamp} {coords}")

          img_logger.log_data(img=current_image, telem=telem)

        # Reset to record next batch of telemetry data
        current_image = current_timestamp = None
        telem_builder = TelemetryBuilder()
  except KeyboardInterrupt:
    print("Exiting ...")
