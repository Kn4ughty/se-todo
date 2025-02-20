
token = localStorage.getItem("token");

//all_tasks = []

function process_all_tasks(data, status) {
    console.log("KASJDLKSDJFLKDJF")
    console.log(data)
    all_tasks = []
    for (i = 0; i < data.length; i++) {
        task = data[i];
        all_tasks.push(task)
        add_task(task["text"])
    }

}

function add_task(text) {
    $("#todo-list").append("<div><input type='checkbox'/ id=" + text + "> \
        <label for ="+ text + ">" + text + "</input></div>");
}


$('document').ready(function() {

    // Load existing tasks from server
    all_tasks = $.ajax({
        type: "GET",
        url: "/tasks",
        headers: {
            Authorization: 'Bearer ' + token
        },
        success: process_all_tasks
    },
    )
    console.log(token)
    console.log(all_tasks)

    // Then put them onto the page

    // Set up bindings
    $('#text-entry').on('submit', function() {
        all_tasks = $.ajax({
            type: "POST",
            url: "/tasks",
            headers: {
                Authorization: 'Bearer ' + token
            },
            data: {
                "text": $("#text-entry input").val()
            }
        },
        )
        add_task($("#text-entry input").val());
        return false;
    });


});

