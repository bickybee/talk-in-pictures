"use strict";

$(document).ready(function() {
    /*  Monitor changes to the input field.
        This is a temporary function to make sure the POST call work. */
    $('#input').bind('input propertychange', function() {
        $.ajax({
            url: '/parse',
            dataType: 'json',
            type: 'post',
            contentType: 'application/json',
            data: JSON.stringify( {"input": $(this).val()}),
            success: function(res) {
                handleParse(res);   // render the response
            }
        })
    })

});


/* Format and render JSON received from the server */
function handleParse(raw) {
    $('#output').html('');  // empty the field

    var tokens = raw["tokens"];
    for (var i in tokens) {
        // Create new container:
        var new_item = '<div class="tkn-container">' +
            '<div class="tkn-img"><img src="' + tokens[i]["img"] + '"></img></div>' +
            '<div class="tkn-caption">' + tokens[i]["word"] + '</div>' +
            '</div>';

        $('#output').append(new_item);
    }
}

