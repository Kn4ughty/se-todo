

function add_task(text) {
    $("#todo-list").append("<p>" + text + "</p>");
}


$('document').ready(function() {

    $('.form1').on('submit', function() {
        //alert('Form submitted!');

        add_task($(".form1 input").val());
        return false;
    });


});

