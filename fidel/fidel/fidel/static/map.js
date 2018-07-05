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

// Add polygon to input before submit form
$("#form_add_zone").submit(function(event) {
    var polygon = JSON.stringify(lastLayer.toGeoJSON());
    $("#polygon").val(polygon);
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
        }
    },
    draw: {
        polygon: {
            allowIntersection: false,
            shapeOptions: {
                color: 'gray'
            }
        },
        polyline: false,
        circle: false, // Turns off this drawing tool
        rectangle: false,
        marker: false,
        circlemarker: false,
    }
});

var drawControlEdit = new L.Control.Draw({
    position: 'topright',
    edit: {
        featureGroup: drawnItems,
        poly: {
            allowIntersection: false
        }
    },
    draw: false
});

var drawControlNone = new L.Control.Draw({
    edit: false,
    draw: false
});

map.addControl(drawControlFull);

//map.on('click', onMapClick);

map.on("draw:created", function(event) {
    var layer = event.layer;

    drawnItems.addLayer(layer);
    //No allow more creation
    drawControlFull.remove(map);
    drawControlEdit.addTo(map);
    $("#form_add_zone").removeAttr("hidden");
    lastLayer = layer;
    $("#result").remove();
});

map.on("draw:deleted", function(event) {
    addToolbar();
    $("#form_add_zone").attr("hidden", "true");
});

initializeDrawPolygon();