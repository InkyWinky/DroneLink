export default {
  async fetchSpline(coordinateData) {
    try {
      const response = await fetch(
        `http://${window.location.host.split(":")[0]}:8000`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            command: "fetchSpline",
            data: coordinateData,
          }),
        }
      );
      const coordinates = await response.json();
      return coordinates;
    } catch (error) {
      console.error(error);
    }
  },

  async getSpline(coordinates, splineData) {
    for (let index = 0; index < splineData.length; index++) {
      console.log(
        "Coordinate: " +
          index +
          " | (" +
          splineData[index].long +
          ", " +
          splineData[index].lat +
          ")"
      );
    }
    console.log("Coordinate data received.");
  },

  async executeCommand(command, data) {
    // console.log(JSON.stringify({ command: command, ...data }));
    try {
      const response = await fetch(
        `http://${window.location.host.split(":")[0]}:8000`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ command: command, ...data }),
        }
      );
      const res = await response;
      // console.log(res);
      return res;
    } catch (error) {
      console.error(error);
    }
  },
};
