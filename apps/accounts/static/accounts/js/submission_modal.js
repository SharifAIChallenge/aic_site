function show_modal(arg) {
    var obj = $(arg);
    obj.parent().find('.ui.modal').modal('show');
}

function close_modal(arg) {
    var obj = $(arg);
    obj.parent().parent().modal('hide');
}
