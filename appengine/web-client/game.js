// Object definition
var STTT = null;
jQuery(function ($) {
    STTT = function () {
        // attributes
        var PLAYER_X = "X";
        var PLAYER_O = "O";
        
        var channel = null;
        var game_id = null;
        var last_game_state = null;
        var client_player = null;
        
        // methods
        var cartesian2linear = function(x, y, wrap) {
            return x + (y * wrap);
        };
        
        var update_status = (function () {
            var fade_out = 1000;
            var status_bar_selector = "#Status ul"
            var persistent_messages = "#Status ul > li[data-persistent=true]:visible";
            
            var create_status_message = function (m) {
                var status_message = $(document.createElement("li"));
                status_message.append(document.createTextNode(m));
                return status_message;
            };
            
            return function (msg, timeout) {
                var status_bar = $(status_bar_selector);
                var status_message = create_status_message(msg);
                
                if(timeout !== undefined) {
                    status_message.attr('data-persistent', false);
                    status_message.delay(timeout).fadeOut(fade_out);
                } else {
                    status_message.attr('data-persistent', true);
                }
                
                // end-of-life any visble persistent notifications.
                $(persistent_messages).delay(2000).fadeOut(fade_out);
                
                status_bar.prepend(status_message);
                
                return status_message;
            };
        }());
        
        var channel_is_ready = function () {
            return channel !== null;
        };
        
        var game_is_ready = function () {
            return (last_game_state !== null &&
                last_game_state.move_x !== null &&
                channel_is_ready());
        };
        
        var current_player = function () {
            if (game_is_ready()) {
                return last_game_state.move_x? PLAYER_X:PLAYER_O;
            }
        };
        
        var is_player_turn = function (plyr) {
            var player = plyr !== undefined?plyr:client_player;
            return current_player() === player;
        };
        
        var board_playable = function (board) {
            if(game_is_ready()) {
                return last_game_state.next === null || last_game_state.next === parseInt(board);
            }
        };
        
        var notify_player = function (player) {
            update_status("Player " + (player || current_player()));
        };
        
        // callbacks
        var update_game_state_cb = (function () {
            var cats = ['Meu', 'Mao', 'Miav', 'Meow', 'Miau', 'Miaou',
                'Nnaiou', 'Nya~an', 'Nya', 'N~yao', 'Yaong', 'Nyaong',
                'Mjau'];
            
            var random_cat = function() {
                var r = Math.floor(Math.random() * cats.length);
                return cats[r];
            };
            
            return function (game_state) {
                var html_boards = $("#SuperTicTacToe td.square.board");
                var html_squares = $("#SuperTicTacToe td.square.cell");
                
                if(last_game_state === null) {
                    update_status("An opponent has arrived");
                }
                
                last_game_state = game_state;
                
                notify_player();
                
                var i = 0;
                for(i = 0; i < html_squares.length; i++) {
                    var html_square = $(html_squares[i]);
                    var board = html_square.attr('data-board');
                    var square = html_square.attr('data-square');
                    var mark = last_game_state.cells[board][1].cells[square];
                    
                    if (mark !== null) {
                        html_square.addClass("player" + mark);
                        html_square.attr('data-claimed', true);
                    }
                }
                
                for(i = 0; i < html_boards.length; i++) {
                    var html_board = $(html_boards[i]);
                    var board = html_board.attr('data-board');
                    
                    var mark = last_game_state.cells[board][0];
                    
                    if (mark !== null) {
                        html_board.addClass("player"+mark);
                    }
                    
                    if(board_playable(board)) {
                        html_board.removeClass('disabled');
                    } else {
                        html_board.addClass('disabled');
                    }
                }
                
                if (last_game_state.winner !== null) {
                    update_status("Game Over", 10000);
                    if(last_game_state.winner == "cats") {
                        update_status(random_cat() + " (Cats Game)");
                    } else {
                        update_status(
                            "Player " + last_game_state.winner + " has won");
                    }
                }
            };
        }());
        
        var build_lobby_cb = (function() {
            var build_game_row = function(game_data) {
                var row = $(document.createElement("tr"));
                var p1 = $(document.createElement("td"));
                var p2 = $(document.createElement("td"));
                var age = $(document.createElement("td"));
                p1.append(document.createTextNode(
                    game_data.player_x));
                p2.append(document.createTextNode(
                    game_data.player_o || "--"));
                
    //            created = new Date(game_data.created);
    //            age.append(document.createTextNode(created.toString()));
                
                row.attr("data-game-id", game_data.game_id);
                row.append(p1, p2, age);
                
                return row;
            };
            
            var row_click_cb = function (e) {
                var widget = $(e.currentTarget);
                join_game(widget.attr("data-game-id"));
            };
            
            return function (data) {
                var i = 0;
                
                $("#PublicLobby table tr[data-game-id]").remove();
                
                for(i = 0; i < data.length; i++) {
                    var row = build_game_row(data[i])
                    row.click(row_click_cb);
                    $("#PublicLobby table").append(row);
                }
            };
        }());
        
        var open_channel_cb = function (data) {
            channel = data;
            var channel_api = new goog.appengine.Channel(channel.channel_token);
            var socket = channel_api.open();
            socket.onmessage = function(m) {
                var msg = JSON.parse(m.data);
                
                switch(msg.mode) {
                    case "channel-test":
                        update_status("Connected", 10000);
                        break;
                    case "game-state":
                        update_game_state_cb(msg);
                        break;
                    case "start-game":
                        game_id = msg.game_id;
                        client_player = msg.player;
                        $("#GameBoard *").remove();
                        $("#GameBoard").append(
                            build_html_supertictactoe_board(
                                {id:"SuperTicTacToe"}));
                        $("#CurrentGameID").attr("value", game_id);
                        $("#GameBoard").parent().slideDown();
                        $("#CreateNewGame").parent().slideUp();
                        update_status("Ready", 10000);
                        update_status("Waiting for opponent");
                        break;
                    default:
                        break;
                }
            };
            
            socket.onopen = function() {
                update_status("Connecting to game server");
                $.post('/channel');
            };
        };
        
        var square_click_cb = function(e) {
            if(is_player_turn()) {
                var widget = $(e.currentTarget);
                var board = widget.attr('data-board');
                var square = widget.attr('data-square');
                
                move(board, square);
            }
        };
        
        var square_mouseenter_cb = function(e) {
            if(is_player_turn()) {
                var widget = $(e.currentTarget);
                var board = widget.attr('data-board');
                
                if(board_playable(board)) {
                    var claimed = widget.attr('data-claimed');
                    if (claimed === undefined || claimed === "") {
                        widget.addClass("player"+client_player);
                    }
                }
            }
        };
        
        var square_mouseleave_cb = function(e) {
            var widget = $(e.currentTarget);
            var claimed = widget.attr('data-claimed');
            if (claimed === undefined || claimed === "") {
                widget.removeClass("player"+client_player);
            }
        };
        
        // requests
        var open_channel = function () {
            if(!channel_is_ready()) {
                $.getJSON('/channel', open_channel_cb);
            }
        };
        
        var refresh_lobby = function () {
            $.getJSON('/lobby', build_lobby_cb);
        };
        
        var refresh_game_state = function () {
            if(channel_is_ready()) {
                $.post('/game-state', {game_id: game_id});
            }
        };
        
        var create_new_game = function (pub) {
            if(pub === true) {
                update_status("Creating public game", 5000);
                $.post("/game");
            } else {
                update_status("Creating private game", 5000);
                $.post("/game", {public_game: false});
            }
        }
        
        var join_game = function(game_id) {
            update_status("Joining game");
            $.post("/game", {game_id: game_id});
        };
        
        var move = function (board, square) {
            if(board_playable(board, square)) {
                $.post("/move", {
                    game_id: game_id,
                    board: board,
                    square: square
                });
                return true;
            }
            return false;
        };
        
        // misc
        var build_html_tictactoe_board = function (config, events) {
            var table = $(document.createElement("table"));
            
            var i = 0;
            var j = 0;
            for(i = 0; i < 3; i++) {
                var row = $(document.createElement("tr"));
                for(j = 0; j < 3; j++) {
                    var square = $(document.createElement("td"));
                    square.addClass("square");
                    square.addClass("cell");
                    square.attr("data-square", cartesian2linear(j, i, 3));
                    
                    if(config.board !== undefined) {
                        square.attr("data-board", config.board);
                    }
                    
                    square.bind(events);
                    
                    square.append(document.createElement("div"));
                    
                    row.append(square);
                }
                table.append(row);
            }
            
            return table;
        };
        
        var build_html_supertictactoe_board = function (config) {
            config = config || {};
            var table = $(document.createElement("table"));
            table.addClass("super");
            table.addClass("board");
            
            var i = 0;
            var j = 0;
            for(i = 0; i < 3; i++) {
                var row = $(document.createElement("tr"));
                for(j = 0; j < 3; j++) {
                    var position = cartesian2linear(j, i, 3);
                    var square = $(document.createElement("td"));
                    square.addClass("board");
                    square.addClass("square");
                    square.attr('data-board', position);
                    var board = build_html_tictactoe_board({board: position}, {
                        click: square_click_cb,
                        mouseenter: square_mouseenter_cb,
                        mouseleave: square_mouseleave_cb});
                    
                    square.append(board);
                    row.append(square);
                }
                table.append(row);
            }
            
            if(config.id === undefined) {
                return table;
            } else {
                var div = $(document.createElement("div"));
                div.attr("id", config.id);
                div.append(table);
                return div;
            }
        };
        
        // public access
        return {
            // attributes
            'open_channel': open_channel,
            'last_game_state': last_game_state,
            'client_player': client_player,
            'channel': channel,
            
            // methods
            'force_refresh': refresh_game_state,
            'update_status': update_status,
            'refresh_lobby': refresh_lobby,
            'create_new_game': create_new_game,
            'join_game': join_game,
            'move': move
        };
    }();
});

// Setup page
jQuery(document).ready(function ($) {
    $("#ClientPanel :header").addClass("collapsible").click(function (e) {
        var widget = $(e.currentTarget);
        widget.next().slideToggle();
    });
    
    $("#CreateNewGame, #PrivateLobby, #PublicLobby, #LobbyHelp").hide();
    
    $("#CreatePrivateGame").click(function () {
        STTT.create_new_game(false);
    });
    
    $("#CreatePublicGame").click(function () {
        STTT.create_new_game(true);
    });
    
    $("#UpdateGameLobby").click(STTT.refresh_lobby);
    
    $("#PrivateLobby input").click(function () {
        var game_id = $("#PrivateGameID").attr('value');
        STTT.join_game(game_id);
    });
    
    $("#ForceGameRefresh").click(function () {
        STTT.force_refresh();
    });
    
    STTT.refresh_lobby();
    STTT.open_channel();
});

