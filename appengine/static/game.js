$(document).ready(function() {
    var channel_ready = false;
    var player_class = "playerX";
    
    function update_game(game_state) {
        console.log(game_state);
    }
    
    $.getJSON('/channel', function(data) {
        $.ajaxSetup({data: {channel_id: data.channel_id}});
        
        var channel_api = new goog.appengine.Channel(data.channel_token);
        var socket = channel_api.open();
        socket.onmessage = function(m) {
            msg = JSON.parse(m.data);
            
            switch(msg.mode) {
                case "channel-test":
                    channel_ready = (msg.status !== undefined &&
                        msg.status === "Ok");
                    break;
                case "game-state":
                    update_game(msg);
                    break;
                default:
                    break;
            }
        };
        
        socket.onopen = function() {
            $.post('/channel')
        }
    });
    
    var cells = $('.square.cell')
    
    cells.click(function(e) {
        var widget = $(e.currentTarget);
        console.log(widget.attr('data-board'), widget.attr('data-square'));
        widget.addClass(player_class);
        widget.attr('data-claimed', "True");
        $.post("/move", {
            game_id: 1,
            board: widget.attr('data-board'),
            square: widget.attr('data-square')});
    });
    
    cells.mouseenter(function(e) {
        var widget = $(e.currentTarget);
        if (widget.attr('data-claimed') === "") {
            widget.addClass(player_class);
        }
    });
    
    cells.mouseleave(function(e) {
        var widget = $(e.currentTarget);
        if (widget.attr('data-claimed') === "") {
            widget.removeClass(player_class);
        }
    });
});
