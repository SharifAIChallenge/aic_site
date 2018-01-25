function second_field() {
    var options = $('#drop2_id option');
    if ( $('#drop1_id' ).val() == "-----" || $('#drop1_id' ).val() == ""){
        $('#drop1_id').val("");
        $('#third_member').hide(800);
    }
    else {
        $('#third_member').show(800);
    }
}
function third_field() {
    if ( $('#drop2_id' ).val() == "-----" || $('#drop1_id' ).val() == ""){
        $('#drop2_id').val("");
    }
}