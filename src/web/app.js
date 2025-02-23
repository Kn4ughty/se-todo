
token = localStorage.getItem("token");

confettiEnabled = localStorage.getItem("confetti")
if (confettiEnabled == "true") {
    confettiEnabled = true
}
else {
    confettiEnabled = false
}


function process_all_tasks(data, status) {
    all_tasks = []
    for (i = 0; i < data.length; i++) {
        task = data[i];
        all_tasks.push(task)
        add_task_to_dom(task["text"], task["uuid"], task["status"])
    }

}

function add_task_to_dom(text, uuid, status) {
    let checked = ""
    let label_style = ""
    if (status == true) {
        checked = "checked"
        label_style = 'style="text-decoration: line-through;"'
    }

    checkbox_id = uuid + "-input"
    checkbox = "<input type='checkbox' id = '" + checkbox_id + "' \
        onclick='update_task_status(\"" + uuid + "\", this)'\
        " + checked + ">"
 

    $("#todo-list").append("<div class='task' id = '" + uuid + "'> \
        <div class='task-left-side'>" + checkbox +"\
        <label for="+ checkbox_id + " " + label_style + ">" + text + "</label>\
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
            $("#" + uuid).fadeOut(100);
        },
        error: function(error) {
            console.log("Error deleting task. Error:", error)
        }
    });
}

function update_task_status(uuid, element) {
    // Not having this let here cause me a world of hurt.
    // It was being overwritten by a different variable named status
    // This meant that everything was broken and nothing worked.
    // this would be fine if status was like a global variable
    // BUT IT WAS A VARIABLE NAMED STATUS IN A DIFFERENT FUNCTION
    // I hate JS SO FRIGGIN MUCH AAAAAAAAAAAAA
    let status = (element.checked === true);
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
    text_id = "#" + uuid + " .task-left-side label"
    if (status === true) {
        $("#" + uuid + " .task-left-side label").css("text-decoration", "line-through");
        if (confettiEnabled) {
            window.confetti({"origin" : {"x": 0.5, "y": 1}})
        }
    }
    else {
        $("#" + uuid + " .task-left-side label").css("text-decoration", "none");
    }
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
    
    confetti_switch = "<input type='checkbox' id='confetti-toggle' onclick='localStorage.setItem(\"confetti\", this.checked); location.reload()'"
 
    if (confettiEnabled) {
        $("#confetti-toggler").prepend(confetti_switch+"checked>")
    }
    else {
        $("#confetti-toggler").prepend(confetti_switch+">")
    }

});

