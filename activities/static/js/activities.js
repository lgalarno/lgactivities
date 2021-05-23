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

// leaflet_map_init
let center = document.getElementById("leafletCenter").value;
let coord = document.getElementById("leafletCoord").value;
var map = L.map('mapid').setView(JSON.parse(center), 15);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
let polyline = new L.Polyline([
    JSON.parse(coord)
    ]).addTo(map);


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