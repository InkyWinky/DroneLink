console.log("Running Test ...")

var coordinateData = [{
    id: 0,
    long: 12,
    lat: 14,
    alt: 20
},{
    id: 1,
    long: 13,
    lat: 15,
    alt: 20
},{
    id: 2,
    long: 14,
    lat: 16,
    alt: 20
}];

console.log("Data created.\nFetching ...")

async function fetchSpline(id) {
    try {
        const response = await fetch("http://127.0.0.1:8000", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify(coordinateData)
        });
        const coordinates = await response.json();
        return coordinates;
    } catch (error) {
        console.error(error);
    }
}

async function getSpline(coordinates) {
    const splineData = await fetchSpline(coordinates);
    for (var index = 0; index < splineData.length; index++) {
        console.log("Coordinate: " + index + " | (" + splineData[index].long + ", " + splineData[index].lat + ")");
    }
    console.log("Coordinate data received.")
}

getSpline(coordinateData);