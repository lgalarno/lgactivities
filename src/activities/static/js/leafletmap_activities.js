$(function() {
        /////////////////////////////////////////////////////////////
        // leaflet_map_init
        // used in activity and segment details
        // Get data from api
        /////////////////////////////////////////////////////////////
        let mapid_endpoint = document.getElementById("mapid");
        if (mapid_endpoint != null) {
            mapid_url = mapid_endpoint.getAttribute('endpoint');
            var coord = [];
        // var center = [];
            $.ajax({
                url: mapid_url,
                method: "GET",
                dataType: "json",
                contentType: false,
                cache: false,
                processData: false,
                success: function (data){
                    coord = data.coord;
                    // center = data.center;
                    leafletmap(coord)
                },
                error: function (error){
                    console.log("error")
                    console.log(error)
                }
            })
        }

        function leafletmap(coord){
            let coord_json = JSON.parse(coord);
            var map = L.map('mapid'); // .setView(JSON.parse(center), 15);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
               attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
               }).addTo(map);
            let polyline = new L.Polyline([
               coord_json //JSON.parse(coord)
               ]).addTo(map);
            let beg = coord_json[0];
            let end = coord_json[coord_json.length-1];
            var greenIcon = L.icon({
                iconUrl: "/static/images/marker-icon-green.png",
                // shadowUrl: '/static/images/marker-shadow.png',
                iconSize: [15, 25],
                iconAnchor: [12, 24],
                popupAnchor: [1, -34],
                shadowSize: [25, 25]
                });
            var redIcon = L.icon({
                iconUrl: "/static/images/marker-icon-red.png",
                // shadowUrl: '/static/images/marker-shadow.png',
                iconSize: [15, 25],
                iconAnchor: [12, 24],
                popupAnchor: [1, -34],
                shadowSize: [25, 25]
                });
            //
            //
            L.marker(beg, {icon: greenIcon}).addTo(map);
            L.marker(end, {icon: redIcon}).addTo(map);
            map.fitBounds(JSON.parse(coord));
            }
    }
);
