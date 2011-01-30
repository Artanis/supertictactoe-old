# System Modules
import sys

# External Modules
try:
    import json
except ImportError:
    from django.utils import simplejson as json

# Local Modules

class TicTacToe(object):
    """A simple Tic-Tac-Toe game.
    
    """
    
    def __init__(self, game_state={}):
        self.moves  = game_state.get('moves', [])
        self.cells  = game_state.get('cells', [None for x in range(9)])
        self.winner = game_state.get('winner', None)
    
    def move(self, player, cell):
        """Markes the desired square for the player, if it hasn't been
        claimed already.
        
        Also checks victory conditions, and marks the game as won if
        any are met, or tied if the board is full.
        
        """
        
        if self.playable(cell):
            self.cells[cell] = player
            self.moves.append(
                (player, cell))
            
            if self.is_winner(player, cell) and self.winner is None:
                self.winner = player
            elif len(self.moves) >= 9 and self.winner is None:
                self.winner = "cats"
            return True
        return False
    
    def playable(self, cell):
        """Returns true if the board index is playable (``None``)"""
        
        return self.cells[cell] is None
    
    def is_winner(self, player, cell):
        """Determine if the given player has won the game.
        
        The ``cell`` argument should be the last move the player has
        made. It is used to determine which column and row needs to be
        checked, and if the diagonals need to be checked.
        
        """
        if len(self.moves) > 2:
            # Need at least 3 moves for a player to win. Normally
            # would be 5, but turn enforcement is not implemented here.
            
            column   = cell % 3
            row      = cell - (cell % 3)
            diagonal = cell % 2 == 0
            
            victory = False
            
            # For these checks, we slice the cells in question out of the
            # board, compare them all to the player, and finally check that
            # each is True.
            if diagonal:
                victory = victory or \
                    all([c == player for c in self.cells[0:9:4]]) or \
                    all([c == player for c in self.cells[2:8:2]])
            
            victory = victory or \
                all([c == player for c in self.cells[column:9:3]]) or \
                all([c == player for c in self.cells[row:row+3]])
            
            return victory
        return False
    
    def dump(self):
        """Dumps the game state to JSON"""
        
        return json.dumps({
            'moves': self.moves,
            'cells': self.cells,
            'winner': self.winner})
    
    @classmethod
    def load(cls, json_str):
        """Loads the game state from JSON.
        
        Really just shunts the unserialized dict into the constructor.
        
        """
        game_state = json.loads(json_str)
        return cls(game_state)
    
    def __str__(self):
        return "[%s] winner: %s" % (
            "".join([cell or "." for cell in self.cells]),
            self.winner)

class SuperTicTacToe(TicTacToe):
    """A Tic-Tac-Toe variant played on a grid of Tic-Tac-Toe boards.
    
    Rules
    -----
    *Adapted from the Wikipedia description.*
    
    http://en.wikipedia.org/wiki/Tic-tac-toe
    
    *   Nine Tic-Tac-Toe boards are arranged in a 3 by 3 grid.
    *   The first player's move ('X') may be played on any board.
        Subsequent moves are played in the board corresponding to the
        square played in the previous move. For example, if a move is
        in the upper-left cell of a board, the next move takes place in
        the upper-left board.
    *   If a player can't move because the indicated board is full, the
        next move may go on any board.
    *   Getting three in a row on any board wins that board for the
        player, but can still be played until full.
    *   Winning three boards in a row on the super board wins the game.
    
    """
    
    def __init__(self, game_state={}):
        cells = game_state.get('cells', None)
        self.moves  = game_state.get('moves', [])
        self.winner = game_state.get('winnner', None)
        self.next = game_state.get('next', None)
        self.cells = []
        
        if cells:
            self.cells = [(m, TicTacToe(b)) for m, b in cells]
#            for mark, board in cells:
#                self.cells.append((mark, TicTacToe(**board)))
        else:
            self.cells = [(None, TicTacToe()) for x in range(9)]
    
    def move(self, player, board, cell):
        if self.playable(board, cell):
            mark, sub_board = self.cells[board]
            
            sub_board.move(player, cell)
            self.moves.append(
                (player, board, cell))
            
            # Set the next board to play on
            if len(self.cells[cell][1].moves) < 9:
                self.next = cell
            else:
                self.next = None
            
            if sub_board.winner:
                mark = sub_board.winner
            
            self.cells[board] = (mark, sub_board)
            
            if self.is_winner(player, cell) and self.winner is None:
                self.winner = player
            elif len(self.moves) >= 81 and self.winner is None:
                self.winner = "cats"
            return True
        return False
    
    def playable(self, board, cell=None):
        if cell is not None:
            board_ok = board == self.next or self.next is None
            cell_ok  = self.cells[board][1].playable(cell)
            return board_ok and cell_ok
        else:
            return self.cells[board] is None
    
    def dump(self):
        """Dumps the game state to JSON"""
        
        return json.dumps({
            'moves': self.moves,
            'winner':self.winner,
            'next': self.next,
            'cells': [(m, b.__dict__) for m, b in self.cells]})
    
    def __str__(self):
        result = []
        result.append("   cells: 012345678  winner: %s" % self.winner)
        for i, cell in enumerate(self.cells):
            mark, board = cell
            result.append("Board %s: %s" % (i, str(board)))
        
        return "\n".join(result)

def main(*args, **kwargs):
    mode = args[1] if len(args) > 1 else "st3"
    
    {"t3": t3, "st3": st3}[mode]()

def t3():
    from random import shuffle
    from itertools import cycle
    
    game = TicTacToe()
    
    moves = range(9)
    shuffle(moves)
    
    for player, cell in zip(cycle("XO"), moves):
        game.move(player, cell)
        print game 
        if game.winner is not None:
            break

def st3():
    import yaml
    from random import shuffle
    from itertools import cycle
    
    game = SuperTicTacToe()
    
    moves = yaml.load(open("docs/GAME01.yaml"))
    for player, board, cell, comment in moves:
        if player is not None and board is not None and cell is not None:
            game.move(player, board, cell)
            print game
            print "PLAYER {0} PLAYS ON ({1}, {2})".format(
                player, board, cell),
            raw_input()
        if comment: print comment,
        print
    
    print game.winner

if __name__ == "__main__":
    import sys
    main(*sys.argv)
