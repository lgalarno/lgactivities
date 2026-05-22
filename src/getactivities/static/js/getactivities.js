/////////////////////////////////////////////////////////////
// waiting function
/////////////////////////////////////////////////////////////
$(function() {
    /////////////////////////////////////////////////////////////
    // Waiting button
    /////////////////////////////////////////////////////////////
    function waiting_js(get_act_form) // Submit button clicked
    {
        var icnDownload = document.getElementById("icnDownload");
        form.btnDownload.value = "Please wait...";
        form.btnDownload.disabled = true;
        icnDownload.style.display = "inline-block";
        return true;
    };

    /////////////////////////////////////////////////////////////
    // Warn the user when the start date day is greater than 28
    // and the frequency is monthly
    /////////////////////////////////////////////////////////////
    var frequencSelect = document.getElementById("id_frequency");
    var startDate = document.getElementById("id_start_date");
    var frequencSelectValue = frequencSelect.value
    var startDateDate = new Date(startDate.value);
    var day = startDateDate.getUTCDate();
    warning_day_28(frequencSelectValue, day);

    frequencSelect.addEventListener(`change`, (e) => {
        const select = e.target;
        frequencSelectValue = select.value;
        warning_day_28(frequencSelectValue, day);
    });

    startDate.addEventListener(`change`, (e) => {
        const select = e.target;
        startDateDate = new Date(select.value);
        day = startDateDate.getUTCDate();
        warning_day_28(frequencSelectValue, day);
    });

    function warning_day_28(f, d)
    {
        var alert_box_display = document.getElementById("alert_box");
        if (f == 30 && d > 28) {
            $(alert_box_display).show();
        } else {
            $(alert_box_display).hide();
        };
    };
});
