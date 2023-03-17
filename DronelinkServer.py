import http.server
import json
import SplineGenerator.SplineGenerator as spline

# Constants
PORT = 8000
FILTERS = ["NAMED_VALUE_INT", "NAMED_VALUE_FLOAT"]


class ServerHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept'
        )
        self.end_headers()


def do_POST(self):
    # Send initial headers
    self.do_HEAD()

    # Get the message from API client
    content_length = int(self.headers.getheader('content-length', 0))
    post_message = self.rfile.read(content_length)

    print("POST MESSAGE:\n", post_message)

    # Extract list of waypoints
    # TODO Get the waypoints sent by GUI into a list of [long, lat] lists.
    waypoint_list = [[49.2, 109.2], [49.9, 110.1], [48.7, 110.9]]
    # TODO END

    # Get list of Waypoint classes
    waypoint_class_list = spline.generate_waypoints_from_list(waypoint_list)

    # Create instance of SplineGenerator class
    spliner = spline.SplineGenerator(waypoints=waypoint_class_list,
                                     radius_range=(38.1, 39),  # Metres
                                     boundary_points=None,
                                     boundary_resolution=None,
                                     tolerance=0.0,
                                     curve_resolution=3)

    # Get the data in a JSON readable format and send it back to whoever asked for it
    waypoint_output_list = spliner.get_waypoint_in_dictionary()
    self.wfile.write(json.dumps(waypoint_output_list).encode("utf-8"))

def log_message(self, format, *args):
    """Disable server logging"""
    return


if __name__ == "__main__":
    server_address = ("", PORT)
    httpd = http.server.HTTPServer(server_address, ServerHandler)

    print("Server started on port", PORT, "...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Closing server...")
    finally:
        stop = True
