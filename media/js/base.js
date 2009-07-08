$(document).ready(function(){
    setupHelpBubbles();
    checkIntervalField();
    $("#id_interval").change(function(){
        console.debug("hey");
        checkIntervalField(); 
    });
});

function setupHelpBubbles () {
    // Put a top and bottom div in each help bubble
    var topDiv    = '<div class="top"></div>';
    var bottomDiv = '<div class="bottom"></div>';
    $('#side_help .bubble').prepend(topDiv).append(bottomDiv);
}

function checkIntervalField () {
    // If the interval field (on the New Chore page) is set to other, create the
    // "other" box and manipulate the names so it gets submitted as "interval"
    // instead of the select box
    if($("#id_interval").val() == "other"){
        // find the original value and wipe it after saving it
        original = $("#id_interval").attr("original");
        $("#id_interval").attr("original", "");
        
        $("#id_interval").after('<div id="interval_other">Every <input type="text" name="interval" size="4" value="' + original + '"> day(s).</div>');
        
        $("#interval_other").animate({backgroundColor: "#ff6"}, 500)
            .animate({backgroundColor: "#fff"}, 500);
        $("#id_interval").attr("name", "hidden_interval");
    }
    else{
        // remove the "other" box and swap back the field names so the select
        // box gets submitted correctly
        $("#interval_other").remove();
        $("#id_interval").attr("name", "interval");
    }
}