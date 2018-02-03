function second_field() {
    var options = $('#drop2_id option');
    if ( $('#drop1_id' ).val() == "-----" || $('#drop1_id' ).val() == ""){
        $('#drop1_id').val("");
    }
    else {
    }
}
function third_field() {
    if ( $('#drop2_id' ).val() == "-----" || $('#drop2_id' ).val() == ""){
        $('#drop2_id').val("");
    }
}