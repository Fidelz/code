// Add toolbar with full control
function addToolbar() {
    drawControlEdit.remove(map);
    drawControlFull.addTo(map);
}

// Start drawing polygon in the map
function initializeDrawPolygon(){
    $(".leaflet-draw-section").click();
    $(".sr-only").click();
    //$(".leaflet-draw-draw-polygon").click();
}

// Add property to input before submit form
$("#form_add_propierty").submit(function(event) {
    var coord = lastLayer._latlng;
    var lat = coord.lat;
    var long = coord.lng;
    $("#lat").val(lat);
    $("#long").val(long);
    event.preventDefault();   // !!!!!!!!!!!!REMOVE
});

var lastLayer = undefined;

var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    osm = L.tileLayer(osmUrl, {
        maxZoom: 18,
        attribution: osmAttrib
    }),
    map = new L.Map('map', {
        center: new L.LatLng(41.648, -0.889),
        zoom: 14,
        editable: true
    }),
    drawnItems = L.featureGroup().addTo(map);

osm.addTo(map);

var drawControlFull = new L.Control.Draw({
    position: 'topright',
    edit: {
        featureGroup: drawnItems,
        poly: {
            allowIntersection: false
        },
        edit: false,
        remove: false
    },
    draw: {
        polygon: false,
        polyline: false,
        circle: false, // Turns off this drawing tool
        rectangle: false,
        circlemarker: false,
    }
});

var drawControlEdit = new L.Control.Draw({
    position: 'topright',
    edit: {
        featureGroup: drawnItems,
    },
    draw: false
});

var drawControlNone = new L.Control.Draw({
    edit: false,
    draw: false
});

map.addControl(drawControlFull);

map.on("draw:created", function(event) {
    var layer = event.layer;

    drawnItems.addLayer(layer);
    //No allow more creation
    drawControlFull.remove(map);
    drawControlEdit.addTo(map);
    $("#form_add_propierty").removeAttr("hidden");
    lastLayer = layer;
    $("#result").remove();
    var coord = layer._latlng;
    var lat = coord.lat;
    var long = coord.lng;
    layer.bindPopup("Lat: " + lat + "<br>Lng: " + long).openPopup();
});

map.on("draw:editmove", function(event) {
    var layer = lastLayer;
    //No allow more creation

    var coord = layer._latlng;
    var lat = coord.lat;
    var long = coord.lng;
    layer.bindPopup("Lat: " + lat + "<br>Lng: " + long).openPopup();
});

map.on("draw:deleted", function(event) {
    addToolbar();
    if (lastLayer != undefined){
        map.removeLayer(lastLayer);
    }
    $("#form_add_propierty").attr("hidden", "true");
});

initializeDrawPolygon();
