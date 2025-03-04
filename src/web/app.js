// Tasks and their data are stored in the DOM.
// I thought it would be bad to duplicate data


token = localStorage.getItem("token");

confettiEnabled = localStorage.getItem("confetti")
if (confettiEnabled == "true") {
    confettiEnabled = true
}
else if (confettiEnabled == "false") {
    confettiEnabled = false
}
else {
    confettiEnabled = true
    localStorage.setItem('confetti', 'true')
}


function process_all_tasks(data, status) {
    // Data is a json array of items
    console.log(data)
    sorted = data.sort(function(a, b) {
        var aVal = a["order"],
            bVal = b["order"]
        return aVal - bVal
    })
    console.log(sorted)
    data = sorted


    completed = []
    for (i = 0; i < data.length; i++) {
        task = data[i];
        if (task["status"] == true) {
            completed.push(task)
            continue
        }
        add_task_to_dom(task["text"], task["uuid"], task["status"], task["order"])
    }
    for (i = 0; i < completed.length; i++) {
        task = completed[i];
        add_task_to_dom(task["text"], task["uuid"], task["status"], task["order"])
    }
}

// This awesome function is from https://stackoverflow.com/questions/8433691/sorting-list-of-elements-in-jquery
function getSorted(selector, attrName) {
    return $($(selector).toArray().sort(function(a, b) {
        var aVal = parseInt(a.getAttribute(attrName)),
            bVal = parseInt(b.getAttribute(attrName));
        return aVal - bVal;
    }));
}

// This function from
function escapeHTML(str) {
    return str.replace(/[&<>"'\/]/g, function(char) {
        switch (char) {
            case '&':
                return '&amp;';
            case '<':
                return '&lt;';
            case '>':
                return '&gt;';
            case '"':
                return '&quot;';
            case '\'':
                return '&#39;';
            case '/':
                return '&#x2F;';
            default:
                return char;
        }
    });
}



function add_task_to_dom(text, uuid, status, order) {
    let checked = ""
    let label_style = ""
    if (status == true) {
        checked = "checked"
        label_style = 'style="text-decoration: line-through;" '
    }

    let checkbox_id = uuid + "-input"
    let checkbox = "<input type='checkbox' id = '" + checkbox_id + "' \
        onclick='update_task_status(\"" + uuid + "\", this)'\
        " + checked + ">"

    let label = "<label for=" + checkbox_id + " " + label_style + "\
    " + "onclick=''>" + text + "</label>"

    $("#todo-list").append("\
        <div class='task' id = '" + uuid + "' \
        data-order='" + order + "'> \
            <div class='task-left-side'>\
                " + checkbox + "\
                " + label + "\
            </div>\
            <div class='task-right-side'>  \
                <i class='fa fa-pen' aria-label='Edit task' \
                onclick='edit_task(\"" + uuid + "\")' ></i>\
                <i class='fa fa-trash task-delete' aria-label='Delete task' \
                onclick='delete_task_from_server(\""+ uuid + "\")'></i>\
            </div>\
        </div>");
}

function edit_task(uuid) {
    let element = $("#" + uuid + " .task-left-side label")
    let old_label = element[0]
    let text = old_label.innerText

    // Generate a new input element with old text
    let input = $("<textarea type='text' class='task-edit'>").val(text)
    console.log(input[0])

    old_label.replaceWith(input[0])
    input.focus();

    function exit_edit_mode() {
        let new_text = input.val();
        console.log("This is old label", old_label)
        old_label.textContent = new_text;
        let new_label = old_label;
        input.replaceWith(new_label)
        console.log("Sending request to server with updated text")
        response = $.ajax({
            type: "POST",
            url: "/updateTaskText",
            headers: {
                Authorization: 'Bearer ' + token
            },
            data: {
                "uuid": uuid,
                "text": new_text
            },
            success: function(response) {
                console.log("Success updating task text")
            },
            error: function(error) {
                console.log("Error changing task text :(. Error:", error)
            }
        });

    }
    input.on("blur", exit_edit_mode);
    input.on("keydown", function(event) {
        console.log("event", event)
        if (event.key === "Enter" || event.key === "Escape") {
            exit_edit_mode();
        }
    })

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
            window.confetti({ "origin": { "x": 0.5, "y": 1 } })
        }
        // This delay makes it so that if you accidentally checked the task,
        // you can then undo it by unchecking it in that timeout
        function moveTask() {
            if (element.checked === true) {
                // First check if task is at the bottom.
                e = $("#" + uuid)
                tasks = $(".task")
                if (tasks[tasks.length - 1].id == uuid) {
                    console.log("Task was already at bottom")
                    return
                }

                // Move task to bottom
                console.log("Moving task")
                e.fadeOut(400, (() => {
                    console.log("Appending task")
                    e.appendTo("#todo-list")
                    e.fadeIn()
                }))
            }
            else {
                console.log("Not checked")
            }
        }
        setTimeout(moveTask, 1000)
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
                add_task_to_dom(escapeHTML($("#text-entry input").val()), response);
                $("#text-entry input").val("");
            },
            error: function(error) {
                console.error("Error adding task. Error: ", error)
            }
        },
        )
        return false;
    });

    confetti_switch = "<input type='checkbox' id='confetti-toggle' \
        aria-label='Confetti Toggle Switch' \
        onclick='localStorage.setItem(\"confetti\", this.checked); \
        confettiEnabled = this.checked'"

    if (confettiEnabled) {
        $("#confetti-toggler").prepend(confetti_switch + "checked>")
    }
    else {
        $("#confetti-toggler").prepend(confetti_switch + ">")
    }


    // Make elements sortable
    $("#todo-list").sortable({
        update: function(event, ui) {

            let all_tasks = $(".task")

            for (i = 0; i < all_tasks.length; i++) {
                let task = all_tasks[i]
                console.log(task)



                let new_index = Array.prototype.indexOf.call($("#todo-list")[0].children, task)
                console.log(new_index)

                // Make request to server to update order
                // POST /taskOrder


                // This is horrible for performance, but i dont have time to be better

                // For every task, get its index and update it

                $.ajax({
                    type: "POST",
                    url: "/taskOrder",
                    headers: {
                        Authorization: 'Bearer ' + token
                    },
                    data: {
                        "uuid": task.id,
                        "order": new_index
                    },
                    success: function(response) {
                        console.log("ORDER UPDATED")
                    },
                    error: function(error) {
                        console.error("ERROR UPDATING ORDFER")
                    }
                })
            }

        }
    })

});

