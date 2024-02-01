import threading
import time

from pymavlink import mavutil

MAVLINK_CONNECTION_STRING = "/dev/ttyACM0"


class CubeConnection:
    connection = None
    trigger_thread = None

    def __init__(self, connection_string=MAVLINK_CONNECTION_STRING, system=0, component=0, baud=None):
        self.stopped = False
        self.trigger_count = 0
        self.boot_time = time.time()

        self.connection = self._create_connection(connection_string, system=system, component=component, baud=baud)
        self.trigger_thread = threading.Thread(
            target=self._detect_trigger,
            args=(),
            daemon=True
        )
        self.trigger_thread.start()

    def __del__(self):
        self.stopped = True
        if self.connection is not None: self.connection.close()
        if self.trigger_thread is not None: self.trigger_thread.join()

    def process_trigger(self):
        if self.trigger_count > 0:
            self.trigger_count -= 1
            return True
        return False

    def get_time(self):
        return int(time.time())

    def next_message(self, filters, conditions="True", blocking=True, timeout=10):
        return self.connection.recv_match(type=filters, condition=conditions, blocking=blocking, timeout=timeout)

    def send_command_acknowledgement(self, command_id, value, progress=100, result=0):
        self.connection.mav.command_ack_send(command_id, value, progress, result, 0, 0)

    @staticmethod
    def _create_connection(connection_string, baud=None, data_rate=8, system=0, component=0):
        """
        Set up a mavlink connection over the given protocol, address and port
        :return: The pymavlink connection object
        """

        if baud is not None:
            print('Establishing connection with ' + connection_string + ' with baud rate ' + str(baud))
            the_connection = mavutil.mavlink_connection(connection_string, baud=baud)
        else:
            print('Establishing connection with ' + connection_string)
            the_connection = mavutil.mavlink_connection(connection_string, source_system=system, source_component=component)

        # Ensure connection is opened, you NEED to ping the connection first!
        the_connection.mav.ping_send(
            int(time.time() * 1e6),  # Unix time in microseconds
            0,  # Ping number
            0,  # Request ping of all systems
            0  # Request ping of all components
        )
        print('Waiting first heartbeat...')
        the_connection.wait_heartbeat()
        print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

        # Request all data streams
        the_connection.mav.request_data_stream_send(
            the_connection.target_system,
            the_connection.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            data_rate,
            1)

        # Wait for a GPS connection
        # print('Waiting for a GPS connection...')
        # the_connection.wait_gps_fix()
        # print('GPS connection fixed!')

        return the_connection

    def _pin_state(self):
        return True

    def _detect_trigger(self):
        #print("Listening to trigger")

        while not self.stopped:
            state = self._pin_state()
            if state:
                # print("Received trigger")
                self.trigger_count += 1
                # Set delay to prevent accidental multi-triggers as pin
                # will be set for a short time
                time.sleep(0.25)
