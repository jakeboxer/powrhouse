var nextToShow = 0;

$(document).ready(function(){
    setupHelpBubbles();
    checkIntervalField();
    hideHmateForms();
    
    showNextHmateForm(true);
    
    // set events
    $("#id_interval").change(function(){
        checkIntervalField(); 
    });
    $("#hmate_add_form .add a").click(function(e){
        e.preventDefault();
        showNextHmateForm();
    });
    $("#hmate_add_form .identifier a").click(function(e){
        e.preventDefault();
        removeHmateForm($(e.target).attr('remove'));
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

function hideHmateForms () {
    $("#hmate_add_form .form").each(function(){
        var hasValue = false;
        $("input", this).each(function(){
            if($(this).val() != ""){
                hasValue = true;
            }
        });
        
        if(!hasValue){
            $(this).hide();
        }
    });
}

function showNextHmateForm (noAnim) {
    $("#hmate_add_form_" + nextToShow).show();
    
    if(noAnim === undefined || !noAnim){
        $("#hmate_add_form_" + nextToShow).animate({
            backgroundColor: "#0f0"
        }, 500, "linear").animate({
            backgroundColor: "#fff"
        }, 500, "linear");
    }
    
    nextToShow++;
}

function removeHmateForm (formId) {
    // remove the specified form
    $("#hmate_add_form_" + formId).animate({
        backgroundColor: "#f00"
    }, 250, "linear", function(){$(this).remove()});
}