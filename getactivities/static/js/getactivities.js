/////////////////////////////////////////////////////////////
// waiting function
/////////////////////////////////////////////////////////////

function waiting_js(form) // Submit button clicked
{
    var icnDownload = document.getElementById("icnDownload");
    form.btnDownload.value = "Please wait...";
    form.btnDownload.disabled = true;
    icnDownload.style.display = "inline-block";
    return true;
}


