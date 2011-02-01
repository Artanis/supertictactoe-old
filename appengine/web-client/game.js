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
            var position = cartesian2linear(j, i, 3);
            var square = $(document.createElement("td"));
            square.addClass("board");
            square.addClass("square");
            square.attr('data-board', position);
            var board = TicTacToeBoard();
            
            // TODO: Find better way to do this
            $(board).children().children().children().attr(
                'data-board', position);
            
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
    
    var update_status = function() {
        var statusbar = $("#Status ul");
        var persistent = "#Status ul > li[data-persistent=true]:visible";
        
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
    var game_board = SuperTicTacToeBoard("SuperTicTacToe");
    $("#Content").append(game_board);
    
    var channel_data = undefined;
    var game_id = undefined;
    var player = undefined;
    var next_board = null;
    var move_x = null;
    
    var channel_is_ready = function() {
        return channel_data !== undefined;
    };
    
    var game_is_ready = function() {
        return game_id !== undefined && channel_is_ready();
    };
    
    var can_play = function() {
        return game_is_ready() && current_player() === player;
    };
    
    var playable = function(board) {
        return next_board === null || next_board === undefined || next_board == board;
    };
    
    var current_player = function() {
        return move_x?"X":"O" || "";
    };
    
    var notify_player = function() {
        update_status("Player " + current_player());
    };
    
    var update_game = function(game_state) {
        next_board = game_state.next;
        move_x = game_state.move_x;
        
        notify_player();
        
        console.log(game_state);
        
        for(var i = 0; i < game_state.cells.length; i++) {
            var cell = game_state.cells[i];
            var mark = cell[0];
            var board = cell[1];
            
            for(var j = 0; j < board.cells.length; j++) {
                var cell_mark = board.cells[j];
                
                if (cell_mark !== null) {
                    var squares = $("#SuperTicTacToe td.square.cell[data-board="+i+"][data-square="+j+"]")
                    squares.addClass("player"+cell_mark);
                    squares.attr("data-claimed", true);
                }
            }
            
            html_board = $("#SuperTicTacToe td.square.board[data-board="+i+"]");
            if(mark !== null) {
                html_board.addClass("player"+mark);
            }
            
            if(!playable(i)) {
                html_board.addClass('disabled');
            } else {
                html_board.removeClass('disabled');
            }
        }
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
                    break;
                case "game-state":
                    update_game(msg);
                    break;
                case "start-game":
                    game_id = msg.game_id;
                    player = msg.player;
                    $('#GameMetadata #game_id').attr('value', game_id);
                    $('#GameMetadata #game_id').attr('readonly', 'readonly');
                    $('#GameMetadata input[type=submit]').fadeOut(1000);
                    update_status("Game started");
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
    
    var create_or_join = $('#GameMetadata form');
    
    create_or_join.submit(function() {
        if(channel_is_ready()) {
            var txt_game_id = $('#GameMetadata #game_id').attr('value');
            if (txt_game_id.length) {
                // join game
                $.post("/game", {game_id: txt_game_id}, function(data) {
                    console.log(data);
                });
            } else {
                // new game
                $.post("/game", function(data) {
                    console.log(data);
                });
            }
        }
        
        return false;
    });
    
    var cells = $('#SuperTicTacToe td.square.cell');
    
    cells.click(function(e) {
        if(can_play()) {
            var widget = $(e.currentTarget);
            var board = widget.attr('data-board');
            var square = widget.attr('data-square');
            
            if(playable(board)) {
                $.post("/move", {
                    game_id: game_id,
                    board: board,
                    square: square});
            }
        }
    });
    
    cells.mouseenter(function(e) {
        if(can_play()) {
            var widget = $(e.currentTarget);
            var board = widget.attr('data-board');
            var square = widget.attr('data-square');
            
            if(playable(board)) {
                var claimed = widget.attr('data-claimed');
                if (claimed === undefined || claimed === "") {
                    widget.addClass("player"+player);
                }
            }
        }
    });
    
    cells.mouseleave(function(e) {
        var widget = $(e.currentTarget);
        var claimed = widget.attr('data-claimed');
        if (claimed === undefined || claimed === "") {
            widget.removeClass("player"+player);
        }
    });
});
