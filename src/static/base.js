$(document).ready(function() {
    // Get flashed messages.
    // setInterval(function() {
    $("#flash-messages").load($("#base-url-data").data("url-flashes"));
    // }, 5000);
    
    // Add close animation to .alert-dismissable.
    $(".alert-dismissible").delay(4000).slideUp(200, function() {
        $(this).alert('close');
    });

    // Update label text after selecting files with .custom-file-input.
    $(".custom-file-input").on("change", function() {
        const length = $(this)[0].files.length;
        var text;

        if (length === 1) {
            text = $(this).val().split("\\").pop();
        } else {
            text = `${length} files selected`;
        }

        $(this).siblings(".custom-file-label").addClass("selected").html(text);
    });
});