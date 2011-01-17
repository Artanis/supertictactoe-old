$(document).ready(function() {
    $(".board input").click(function() {
        var ident = this.getAttribute('data-board') + " " + this.getAttribute('data-cell');
        console.log(ident);
    });
});
