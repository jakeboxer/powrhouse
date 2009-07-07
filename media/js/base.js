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
    // If the interval field (on the New Chore page) is set to other, show the
    // "other" text box. If it's not set to other, hide the "other" text box.
    if($("#id_interval").val() == "other"){
        $("#id_interval_other").removeClass("hidden").addClass("inline")
            .animate({backgroundColor: "#ffc"}, 500)
            .animate({backgroundColor: "#fff"}, 500);
    }
    else{
        $("#id_interval_other").removeClass("inline").addClass("hidden");
    }
}