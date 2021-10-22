$(document).ready(function () {
    $("#search input").on("keyup", function () {
        const value = $(this).val().toLowerCase();
        $(".contact").filter(function () {
            $(this).toggle(
                $(this).find(".name").text().toLowerCase().indexOf(value) > -1
            );
        });
    });
});
