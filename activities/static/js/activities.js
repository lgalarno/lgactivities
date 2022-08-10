$(function() {

        /////////////////////////////////////////////////////////////
        // DataTable
        /////////////////////////////////////////////////////////////

        $('#data_table').DataTable({
            searching: false,
            pageLength: 10
            }
        );

        $('#data_table_list').DataTable({
            searching: true,
            pageLength: 25,
            columnDefs: [
                { orderable: false, targets: 0 }
                ],
            order: [[2, 'asc']],

            initComplete: function () {
                this.api()
                    .columns('.head')
                    .every( function () {
                        let column = this;
                        let select = $('<select><option value=""></option></select>')
                            .appendTo( $("#data_table_list thead tr:eq(0) th").eq(column.index()).empty() )
                            .on( 'change', function () {
                                var val = $.fn.dataTable.util.escapeRegex($(this).val());
                                column.search(val ? '^' + val + '$' : '', true, false).draw();
                            } );
                            column
                                .data()
                                .unique()
                                .sort()
                                .each( function ( d, j ) {
                                    select.append( '<option value="'+d+'">'+d+'</option>' );
                                    } );
                } );
        }



/*            initComplete: function () {
                this.api()
                    .columns()
                    .every(function () {
                        var column = this;
                        var select = $('<select><option value=""></option></select>')
                             .appendTo( $("#table thead tr:eq(0) th").eq(column.index()).empty() )
/!*                            .appendTo($(column.footer()).empty())*!/
                            .on('change', function () {
                                var val = $.fn.dataTable.util.escapeRegex($(this).val());
                                column.search(val ? '^' + val + '$' : '', true, false).draw();
                            });

                        column
                            .data()
                            .unique()
                            .sort()
                            .each(function (d, j) {
                                select.append('<option value="' + d + '">' + d + '</option>');
                            });
                    });
            }*/


            }
        );

        /////////////////////////////////////////////////////////////
        // plotly
        // Plot recent efforts
        // used in segment details
        // Get data from api
        /////////////////////////////////////////////////////////////
        let segment_data_endpoint = document.getElementById("recent_efforts_chart");
        if (segment_data_endpoint != null) {
             segment_data_url = segment_data_endpoint.getAttribute('endpoint');
             $.ajax({
                 url: segment_data_url,
                 method: "GET",
                 dataType: "json",
                 contentType: false,
                 cache: false,
                 processData: false,
                 success: function (data){
                     plot_plotly(data);
                 },
                 error: function (error){
                     console.log("error")
                     console.log(error)
                 }
            });
        }

        function plot_plotly(dataAPI) {
            let all_times = dataAPI.all_times;
            let all_dates = dataAPI.all_dates;
/*            let best_perf_time = dataAPI.best_perf_time;
            let best_perf_date = dataAPI.best_perf_date;*/
            let best_perf_index = dataAPI.best_perf_index;
            let point_url = dataAPI.activity_url;
            let activity_names = dataAPI.activity_names;
            var trace0 = {
                type: "scatter",
                mode: "markers",
                name: "",
                x: all_dates,
                y: all_times.map(time => '2020-01-08 ' + time),
                text: activity_names,
                hoverinfo: 'all'
                };
            var trace1 = {
                type: 'scatter',
                mode: 'markers',
                x: [all_dates[best_perf_index]],
                y: ['2020-01-08 ' + all_times[best_perf_index]],
                hoverinfo: 'skip',
                marker: {
                    color: 'rgba(0, 0, 0, 0)',
                    size: [20],
                    line: {
                        color: 'rgb(255, 0, 0)',
                        width: 2
                        }
                }
                };
            var data = [trace0, trace1];
            var layout = {
                hovermode:'closest',
                yaxis: {
                    tickformat: '%H:%M:%S',
                },
                shapes: [
                    {
                        type: 'line',
                        xref: 'paper',
                        x0: 0,
                        y0: '2020-01-08 ' + all_times[best_perf_index],
                        x1: 1,
                        y1: '2020-01-08 ' + all_times[best_perf_index],
                        line:{
                            color: 'rgb(255, 0, 0)',
                            width: 1,
                            dash:'dot'
                        },
                   }
                   ],
                xaxis:{
                    autorange: true
                },
                showlegend: false
            };
            Plotly.newPlot(segment_data_endpoint, data, layout, {responsive: true});
            segment_data_endpoint.on('plotly_click', function(data){
                if (data.points.length > 0) {
                    let link = point_url[data.points[0].pointNumber];

                    // Note: window navigation here.
                    window.location = link;
                    }
            });
        }

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
                shadowUrl: '/static/images/marker-shadow.png',
                iconSize: [15, 25],
                iconAnchor: [12, 24],
                popupAnchor: [1, -34],
                shadowSize: [25, 25]
                });
            var redIcon = L.icon({
                iconUrl: "/static/images/marker-icon-red.png",
                shadowUrl: '/static/images/marker-shadow.png',
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

        /////////////////////////////////////////////////////////////
        // Segment staring
        // used in segment details
        // using api
        /////////////////////////////////////////////////////////////
        function updateTitle(btn, verb){
             btn.attr("title", verb)
            }
        $(".btn-staring").click(function (e){
            e.preventDefault()
            let this_ = $(this)
            let verb = "Segment stared";
            let staringUrl = this_.attr("data-href")
            if (staringUrl){
                 $.ajax({
                     url: staringUrl,
                     method: "GET",
                     data: {},
                     dataType: "json",
                     contentType: false,
                     cache: false,
                     processData: false,
                     success: function (data){
                        if (data.staring){
                            // this_.children().removeClass('far fa-bookmark').addClass('fas fa-bookmark')
                            $("#staring").attr("src", '/static/images/bookmark_blue.png');
                            verb = "Segment stared"
                        } else {
                            // this_.children().removeClass('fas fa-bookmark').addClass('far fa-bookmark')
                            $("#staring").attr("src", '/static/images/bookmark_blue_outline.png');
                            verb = "Segment not stared"
                        }
                        updateTitle(this_, verb)
                        },
                     error: function (error){
                            console.log("error")
                            console.log(error)
                        }
                })
            }
        })
        }
    );
