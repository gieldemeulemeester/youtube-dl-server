$(document).ready(function() {
    // Add classes and buttons to job table.
    $("#table-jobs tr").each(function() {
        updateJobRow(this);
    });

    // Update status for active jobs.
    setInterval(function() {
        $("#table-jobs tr[data-active='true']").each( async function() {
            let id = $(this).children("th").text();
            let status = $(this).children("td:eq(1)").text();
            let updatedStatus = await getJobStatus(id);

            if (updatedStatus != null && updatedStatus !== status) {
                updateJobStatus(id, updatedStatus);
            }
        }); 
    }, 1000)
});

async function getJobStatus(id) {
    try {
        let response = await fetch($("#url-data").data("url-get-status"), {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: id
            })
        });
        data = await response.json();
        return data.status;
    }
    catch (err) {
        console.error(err);
    }
}

function updateJobStatus(id, status) {
    let row = $(`#table-jobs th:contains(${id})`).parent();
    let statusCell = $(row).children("td:eq(1)");

    console.info(`Job ${id} ${status}`);
    $(statusCell).text(status);
    updateJobRow(row);
}

function updateJobRow(row) {
    let id = $(row).children("th").text();
    let status = $(row).children("td:eq(1)").text();
    let isActive = ["pending", "downloading"].includes(status);

    updateJobRowClasses(row, status, isActive);
    updateJobRowButton(row, status, isActive, id);
}

function updateJobRowClasses(row, status, isActive) {
    let className = "";

    // Set row background color based on status.
    if (status === "downloading") {
        className = "bg-primary";
    } else if (status === "cancelled") {
        className = "bg-danger";
    }

    $(row).children(":not(:last)").each(function() {
        $(this).removeClass("bg-primary bg-danger").addClass(className);
    });

    // Set data-active attribute on row based on status.
    $(row).attr("data-active", isActive);
}

function updateJobRowButton(row, status, isActive, id) {
    $(row).children().last().empty();

    if (isActive) {
        $("<button/>", {
            type: "button",
            class: "btn btn-outline-danger",
            text: "Cancel",
            click: function() { cancelJob(this); },
            "data-id": id
        }).appendTo($(row).children().last());
    } else if (status === "completed") {
        $("<button/>", {
            type: "button",
            class: "btn btn-outline-success",
            text: "Open",
            "data-id": id
        }).appendTo($(row).children().last());
    }
}

async function cancelJob(button) {
    try {
        let id = button.getAttribute("data-id");
        let response = await fetch($("#url-data").data("url-cancel"), {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: id
            })
        });        
        data = await response.json()
        
        if (data.cancelled) {
            updateJobStatus(id, "cancelled");
        } else {
            console.warn(`Could not cancel job ${button.getAttribute("data-id")}`);
        }
    } catch (err) {
        console.error(err);
    }
}
