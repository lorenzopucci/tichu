
const tooltip_threshold = 8;

function render_map (wrapper_id, height, init_zoom, markers, line_lat) {

    document.getElementById(wrapper_id).innerHTML = '<div id="osm-map"></div>';

    var element = document.getElementById('osm-map');
    element.style = `height:${height}px;`;
    var map = L.map(element);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    function get_icon(col) {
        return new L.Icon({
            iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${col}.png`,
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
    }

    const blue_icon = get_icon("blue");
    const red_icon = get_icon("red");

    markers.forEach(marker => {
        var target = L.latLng(
            marker.lat + Math.random() / 50 - 0.01,
            marker.long + Math.random() / 50 - 0.01
        );
        L.marker(target, {
            icon: ((marker.team == 'N') ? blue_icon : red_icon)
        }).bindTooltip(marker.name,
        {
            permanent: false,
            direction: "right"
        }
        ).addTo(map);
    });

    var lastZoom = 6;
    map.on('zoomend', () => {
        var zoom = map.getZoom();

        if (zoom < tooltip_threshold && (!lastZoom || lastZoom >= tooltip_threshold)) {
            map.eachLayer(l => {
                if (!l.getTooltip()) return;
                l.unbindTooltip().bindTooltip(l.getTooltip(), {permanent: false});
            });
        }
        else if (zoom >= tooltip_threshold && (!lastZoom || lastZoom < tooltip_threshold)) {
            map.eachLayer(l => {
                if (!l.getTooltip()) return;
                l.unbindTooltip().bindTooltip(l.getTooltip(), {permanent: true});
            });
        }
        lastZoom = zoom;
    })

    if (line_lat != -100) {
        const point_list = [
            new L.latLng(line_lat, -10000),
            new L.latLng(line_lat, 10000)
        ];
        L.polyline(point_list, {
            color: "black",
            weight: 1
        }).addTo(map);
    }

    var view_center = L.latLng('42.2', '12.8');
    if (markers.length == 1) view_center = L.latLng(markers[0].lat, markers[0].long);

    map.setView(view_center, init_zoom);
}