
token = localStorage.getItem("token");

//all_tasks = []

function process_all_tasks(data, status) {
    console.log("KASJDLKSDJFLKDJF")
    console.log(data)
    all_tasks = []
    for (i = 0; i < data.length; i++) {
        task = data[i];
        all_tasks.push(task)
        add_task_to_dom(task["text"], task["uuid"])
    }

}

function add_task_to_dom(text, uuid) {
    $("#todo-list").append("<div class='task' id = '" + uuid + "'> \
        <input type='checkbox' id = '" + uuid + "-input" + "' > \
        <label for="+ uuid + "-input" + ">" + text + "</label>\
        <i class='fa fa-trash task-delete' \
        onclick='delete_task_from_server(\""+ uuid + "\")'></i></div>");
}

function delete_task_from_server(uuid) {
    console.log(uuid);
    response = $.ajax({
        type: "DELETE",
        url: "/tasks",
        headers: {
            Authorization: 'Bearer ' + token
        },
        data: {
            "uuid": uuid
        },
        success: function(response) {
            $("#" + uuid).fadeOut();
        },
        error: function(error) {
            console.log("Error deleting task. Error:", error)
        }
    });
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
            },
            success: function(response) {
                add_task_to_dom($("#text-entry input").val(), response);
            },
            error: function(error) {
                console.error("Error adding task. Error: ", error)
            }
        },
        )
        return false;
    });


});

