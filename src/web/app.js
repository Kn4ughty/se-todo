
token = localStorage.getItem("token");

//all_tasks = []

function process_all_tasks(data, status) {
    console.log("KASJDLKSDJFLKDJF")
    console.log(data)
    all_tasks = []
    for (i = 0; i < data.length; i++) {
        task = data[i];
        all_tasks.push(task)
        add_task_to_dom(task["text"], task["uuid"], task["status"])
    }

}

function add_task_to_dom(text, uuid, status) {
    checked = ""
    if (status == true) {
        checked = "checked"
    }

    $("#todo-list").append("<div class='task' id = '" + uuid + "'> \
        <div class='task-left-side'>\
        <input type='checkbox' id = '" + uuid + "-input" + "' \
        onclick='update_task_status(\"" + uuid + "\", this.checked)'\
        " + checked + "> \
        <label for="+ uuid + "-input" + ">" + text + "</label>\
        </div>\
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

function update_task_status(uuid, status) {
    $.ajax({
        type: "POST",
        url: "/updateTaskStatus",
        headers: {
            Authorization: 'Bearer ' + token
        },
        data: {
            "status": status,
            "uuid": uuid
        }
    })
}

$('document').ready(function() {

    // Load existing tasks from server
    all_tasks = $.ajax({
        type: "GET",
        url: "/tasks",
        headers: {
            Authorization: 'Bearer ' + token
        },
        success: process_all_tasks,
        error: function(error) {
            console.log("Invalid token?", error);
            if (error.status == 401) {
                alert("Invalid token. Please login again");
                window.location.href = "/login.html";
            }
        }
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
                $("#text-entry input").val("");
            },
            error: function(error) {
                console.error("Error adding task. Error: ", error)
            }
        },
        )
        return false;
    });

    $(":checkbox").change(function(){
        if(this.checked) {
            console.log("checked");
        }
        console.log("test");
    })


});

