Game State JSON
===============

A simple Tic-Tac-Toe board::
    
    Board = [
        null, null, null,
        null, null, null,
        null, null, null];

This is merely a nine-element, one dimensional array. Valid element
values are ``null`` for unclaimed, ``'X'`` for Player 1, and ``'O'``
for Player 2.

----

A cell in the super Tic-Tac-Toe board::
    
    SuperCell = {
        "mark": null,
        "board": Board
    };

The ``mark`` property records the current win state of the SuperCell.
Valid values for ``mark`` are ``null`` for unclaimed, ``'X'`` for Player
1, ``'O'`` for Player 2, and ``'CATS'`` for cats games.

Obviously, ``board`` is an instance of a ``Board`` board described
above.

----

The Super-Tic-Tac-Toe board::
    
    SuperBoard = [
        SuperCell, SuperCell, SuperCell,
        SuperCell, SuperCell, SuperCell,
        SuperCell, SuperCell, SuperCell];

Like the Tic-Tac-Toe board, but with instances of ``SuperCell`` rather
than ``null`` or ``string``.

----

A single move::
    
    Move = {
        "player": String,
        "board": Integer,
        "cell": Integer};

The ``player``, ``board`` and ``cell`` properties record the moving
player, the played ``SuperCell`` (an index), and the played cell in that
``SuperCell``'s board (also an index).

----

The complete game state::
    
    game_state = {
        "state": SuperBoard,
        "moves": []
    }

Just wrapping every thing up. The ``state`` property is simply the
SuperBoard, and ``moves`` is just an array of the moves made by players.

The ``moves`` property will have 81 elements for a full game
(adding ~373 bytes), so this could possibly be optional: available on
request.

Of course, a brand new board state comes in at ~742 bytes, so including
81 moves (and losing ~81 bytes, since ``null``\ s are replaced by
one or three character strings as the game progresses), the final size
would be just over 1KB.

----

Here is an example of a new game, formatted for easy comprehension. The
state by the game server will not be formatted for human reading::
    
    {
        "state": [
            {"mark": null,
             "board": [
                null, null, null,
                null, null, null,
                null, null, null]
            },
            {"mark": null,
             "board": [
                null, null, null,
                null, null, null,
                null, null, null]
            },
            {"mark": null,
             "board": [
                null, null, null,
                null, null, null,
                null, null, null]
            },
            {"mark": null,
             "board": [
                null, null, null,
                null, null, null,
                null, null, null]
            },
            {"mark": null,
             "board": [
                null, null, null,
                null, null, null,
                null, null, null]
            },
            {"mark": null,
             "board": [
                null, null, null,
                null, null, null,
                null, null, null]
            },
            {"mark": null,
             "board": [
                null, null, null,
                null, null, null,
                null, null, null]
            },
            {"mark": null,
             "board": [
                null, null, null,
                null, null, null,
                null, null, null]
            },
            {"mark": null,
             "board": [
                null, null, null,
                null, null, null,
                null, null, null]
            }],
        "moves":[]
    };
