$(function() {
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
                            console.log(eror)
                        }
                })
            }
        })
    }
);
