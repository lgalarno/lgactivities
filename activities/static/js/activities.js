/////////////////////////////////////////////////////////////
// DataTable
/////////////////////////////////////////////////////////////
$(document).ready(
    function () {
        $('#efforts_table').DataTable({
                "dom": 'ltip',
                "searching": false,
                "columnDefs": [
                    { "orderable": false,
                        "targets": 0 }
                ]
            }
        );
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
        //data: {},
        success: function (data){
            all_times = data.all_times;
            all_dates = data.all_dates;
            best_perf_time = data.best_perf_time;
            best_perf_date = data.best_perf_date;
            best_perf_index = data.best_perf_index;
            // console.log(all_times);
            plot_plotly();
        }, error: function (error){
            console.log("error")
            console.log(error)
        }
    })
}
function plot_plotly() {
    var trace0 = {
        type: "scatter",
        mode: "markers",
        name: 'Effort',
        x: all_dates,
        y: all_times.map(time => '2020-01-08 ' + time)
        };
    var trace1 = {
        type: 'scatter',
        mode: 'markers',
        name: 'Best',
        x: [all_dates[best_perf_index]],
        y: ['2020-01-08 ' + all_times[best_perf_index]],
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
                }
           }
           ],
        showlegend: false
    };
    Plotly.newPlot( 'recent_efforts_chart', data, layout, {responsive: true});
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
        //data: {},
        success: function (data){
            coord = data.coord;
            // center = data.center;
            leafletmap()
        }, error: function (error){
            console.log("error")
            console.log(error)
        }
    })
}

function leafletmap(){
     var map = L.map('mapid'); // .setView(JSON.parse(center), 15);
     L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
     let polyline = new L.Polyline([
        JSON.parse(coord)
        ]).addTo(map);
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
    //var children_ = $(this).children()
    var verb = "Segment stared"
    let staringUrl = this_.attr("data-href")
    if (staringUrl){
         $.ajax({
            url: staringUrl,
            method: "GET",
            data: {},
            success: function (data){
                if (data.staring){
                    this_.children().removeClass('far fa-bookmark').addClass('fas fa-bookmark')
                } else {
                    this_.children().removeClass('fas fa-bookmark').addClass('far fa-bookmark')
                    verb = "Segment not stared"
                }
                updateTitle(this_, verb)
            }, error: function (error){
                console.log("error")
                console.log(error)
            }
        })
    }
})