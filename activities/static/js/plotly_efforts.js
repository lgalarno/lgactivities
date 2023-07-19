$(function() {
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


    // let recent_efforts_urls = $('#recent_efforts_urls');
    // if (recent_efforts_urls != null) {
    //     console.log('aaa')
    //     let point_urls= recent_efforts_urls.val();
    //     console.log(point_urls)
    //
    // }


    // segment_data_endpoint.on('plotly_click', function(data){
    //     if (data.points.length > 0) {
    //         let link = point_url[data.points[0].pointNumber];
    //
    //         // Note: window navigation here.
    //         window.location = link;
    //         }
    // });

    }
);
