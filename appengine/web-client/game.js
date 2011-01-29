var cartesian2linear = function(x, y, wrap) {
    return x + (y * wrap);
};

var TicTacToeBoard = function() {
    var table = $(document.createElement("table"));
    
    for(var i = 0; i < 3; i++) {
        var row = $(document.createElement("tr"));
        for(var j = 0; j < 3; j++) {
            var square = $(document.createElement("td"));
            square.addClass("square");
            square.addClass("cell");
            square.attr("data-square", cartesian2linear(j, i, 3));
            square.append(document.createElement("div"));
            
            row.append(square);
        }
        table.append(row);
    }
    
    return table;
};

var SuperTicTacToeBoard = function(id) {
    var table = $(document.createElement("table"));
    table.addClass("super");
    table.addClass("board");
    
    for(var i = 0; i < 3; i++) {
        var row = $(document.createElement("tr"));
        for(var j = 0; j < 3; j++) {
            var square = $(document.createElement("td"));
            square.addClass("board");
            square.addClass("square");
            var board = TicTacToeBoard();
            $(board).children().children().children().attr(
                'data-board', cartesian2linear(j, i, 3));
            square.append(board);
            row.append(square);
        }
        table.append(row);
    }
    
    if(id === undefined) {
        return table;
    } else {
        var div = $(document.createElement("div"));
        div.attr("id", id);
        div.append(table);
        return div;
    }
};

$(document).ready(function() {
    var new_game = function(data) {
        game_id = data.game_id;
        $ajaxSetup({data: {game_id: game_id, channel_id: data.channel_id}});
    };
    
    update_status = function() {
        var statusbar = $("#Status");
        var persistent = "#Status > li[data-persistent=true]:visible";
        
        return function(msg, timeout) {
            var status = $(document.createElement("li"));
            status.append(document.createTextNode(msg));
            
            // end-of-life any visble persistent notifications.
            $(persistent).delay(2000).fadeOut(1000)
            
            statusbar.prepend(status);
            
            if(undefined !== timeout) {
                status.attr('data-persistent', false);
                status.delay(timeout).fadeOut(1000);
            } else {
                status.attr('data-persistent', true);
            }
            
            return status
        };
    }();
    
    update_status("Loading");
    game_board = SuperTicTacToeBoard("SuperTicTacToe");
    $("#Content").append(game_board);
    
    var channel_data = undefined;
    var game_id = undefined;
    var player_class = "playerX";
    
    function update_game(game_state) {
        console.log(game_state);
    }
    
    $.getJSON('/channel', function(data) {
        channel_data = data;
        $.ajaxSetup({data: {channel_id: data.channel_id}});
        
        var channel_api = new goog.appengine.Channel(data.channel_token);
        var socket = channel_api.open();
        socket.onmessage = function(m) {
            msg = JSON.parse(m.data);
            
            switch(msg.mode) {
                case "channel-test":
                    channel_ready = (msg.status !== undefined &&
                        msg.status === "Ok");
                    update_status("Connected", 10000);
                    update_status("Click to start game");
                    break;
                case "game-state":
                    update_game(msg);
                    break;
                default:
                    break;
            }
        };
        
        socket.onopen = function() {
            update_status("Connecting to game server");
            $.post('/channel');
        }
    });
    
    var cells = $('.square.cell');
    
    cells.click(function(e) {
        if(channel_ready && game_ready) {
            var widget = $(e.currentTarget);
            console.log(widget.attr('data-board'), widget.attr('data-square'));
            widget.addClass(player_class);
            widget.attr('data-claimed', "True");
            $.post("/move", {
                game_id: 1,
                board: widget.attr('data-board'),
                square: widget.attr('data-square')});
        } else if(!game_ready) {
            $.getJSON("/new-game", )
        }
    });
    
    cells.mouseenter(function(e) {
        if(channel_data && game_id) {
            var widget = $(e.currentTarget);
            var claimed = widget.attr('data-claimed');
            if (claimed === undefined || claimed === "") {
                widget.addClass(player_class);
            }
        }
    });
    
    cells.mouseleave(function(e) {
        if(channel_ready && game_ready) {
            var widget = $(e.currentTarget);
            var claimed = widget.attr('data-claimed');
            if (claimed === undefined || claimed === "") {
                widget.removeClass(player_class);
            }
        }
    });
});
