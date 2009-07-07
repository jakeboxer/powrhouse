$(document).ready(function(){
    setupHelpBubbles();
});

function setupHelpBubbles () {
    // Put a top and bottom div in each help bubble
    var topDiv    = '<div class="top"></div>';
    var bottomDiv = '<div class="bottom"></div>';
    $('#side_help .bubble').prepend(topDiv).append(bottomDiv);
}