var geoJSONZone = L.geoJSON(JSON.parse($("#polygon").html()));

var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    osm = L.tileLayer(osmUrl, {
        maxZoom: 18,
        attribution: osmAttrib
    }),
    map = new L.Map('map', {
        center: new L.LatLng(41.648, -0.889),
        zoom: 14
    }),
    drawnItems = L.featureGroup().addTo(map);

osm.addTo(map);

var drawControlNone = new L.Control.Draw({
    edit: false,
    draw: false
});

map.addControl(drawControlNone);

geoJSONZone.addTo(map);
map.fitBounds(geoJSONZone.getBounds());
