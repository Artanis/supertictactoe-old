# System Modules
import gtk
import gobject
import webbrowser
import yaml
# External Modules
try:
    import json
except ImportError:
    from django.utils import simplejson as json

# Local Modules
import supertictactoe

SYMBOL_PLAYER_X = "images/symbol-player-x.png"
SYMBOL_PLAYER_O = "images/symbol-player-o.png"
SYMBOL_PLAYER_X_SMALL = "images/symbol-player-x-small.png"
SYMBOL_PLAYER_O_SMALL = "images/symbol-player-o-small.png"

def get_image_symbol(symbol, small=False):
    """Converts a text player symbol (X or O) into an image
    representation.
    
    """
    if symbol == "X":
        return SYMBOL_PLAYER_X_SMALL if small else SYMBOL_PLAYER_X
    elif symbol == "O":
        return SYMBOL_PLAYER_O_SMALL if small else SYMBOL_PLAYER_O
    else:
        return None

def linear2cartesian(position, wrap):
    """Converts a linear index into a cartesian coordinate.
    
    (0,0) is the upper left corner, wrap specifies the maximum x value.
    
    """
    return (position / wrap, position % wrap)

def cartesian2linear(x_pos, y_pos, wrap):
    """Converts a cartesian coordinate and maximum x value into linear
    position.
    
    """
    return x_pos + y_pos * wrap

class TicTacToeBoard(gtk.Table):
    """A simple Tic-tac-Toe board.
    
    No game logic is implemented.
    
    """
    def __init__(self):
        # gtk doesn't support super yet. Directly calling the
        # parent class's constructor.
        gtk.Table.__init__(self)
        
        self.set_row_spacings(1)
        self.set_col_spacings(1)
        
        # The image widget used when the board is won.
        self.mark = gtk.Image()
        self.attach(self.mark, 0, 3, 0, 3)
        
        # Create and layout the buttons
        # Using 0...9and converting to cartesian rather than two nested
        # 0...3 loops
        self.buttons = []
        for position in range(9):
            x, y = linear2cartesian(position, 3)
            
            # Create and prepare the button for use.
            # `image` is added to each instance store the
            # image widget for later access.
            # `claimed` is added to each instance to store the claimed
            # state of each button.
            btn = gtk.Button()
            btn.image = gtk.Image()
            btn.set_size_request(50, 50)
            btn.add(btn.image)
            btn.claimed = False
            
            # Attach the button to the table and store the button in
            # the buttons list for later access.
            self.attach(btn, y, y+1, x, x+1)
            self.buttons.append(btn)

class SuperTicTacToeBoard(gtk.Table):
    """A Super Tic-Tac-Toe board.
    
    Game logic is implemented. This object enforces turn order, and
    drives the SuperTicTacToe game engine.
    
    """
    def __init__(self):
        gtk.Table.__init__(self)
        
        self.engine = supertictactoe.SuperTicTacToe()
        
        self.set_row_spacings(5)
        self.set_col_spacings(5)
        
        self.boards = []
        for position in range(9):
            x, y = linear2cartesian(position, 3)
            mark = gtk.Image()
            board = TicTacToeBoard()
            self.attach(board, y, y+1, x, x+1)
            self.boards.append(board)
        
        # Loop through all the buttons attaching the event handlers.
        for supercell, cell, board, button in self.buttons:
            button.connect("clicked", self.button_clicked,
                # tell the handler which board and button this is
                supercell, cell)
            button.connect("enter", self.button_enter)
            button.connect("leave", self.button_leave)
    
    def get_player(self, move=0):
        """Calculates the player for a move, relative to the current
        move.
        
        ``get_player(-1)`` is always the last player, while
        ``get_player()`` is always the current player.
        
        """
        return "X" if (len(self.engine.moves) - move) % 2 == 0 else "O"
    
    # This decorator changes the function so that it doesn't need to be
    # called, and is instead accessed as though it were a field.
    # Without a setter function, assignment fails, however.
    @property
    def buttons(self):
        """Generate all the boards and buttons and their indices.
        
        """
        for supercell, board in enumerate(self.boards):
            for cell, button in enumerate(board.buttons):
                yield (supercell, cell, board, button)
    
    def hint_next(self, next_index):
        """Disable all the invalid moves, enable all the valid moves.
        
        """
        for supercell, cell, board, button in self.buttons:
            if next_index is None or supercell == next_index:
                label = button.get_label()
                if not button.claimed:
                    button.set_sensitive(True)
            else:
                button.set_sensitive(False)
    
    def button_clicked(self, button, supercell, cell):
        """Click handler for all buttons.
        
        Attempts to make a move (the engine validates it) and updates
        the GUI if successful.
        
        """
        if self.engine.move(self.get_player(), supercell, cell):
            # disable, claim (won't be re-enabled), and set the image
            # for the button
            button.set_sensitive(False)
            button.claimed = True
            button.image.set_from_file(
                get_image_symbol(self.get_player(-1), True))
            
            self.hint_next(self.engine.next)
            
            # If the move won the board, set the image for the board as
            # well,
            if self.engine.cells[supercell][0] is not None:
                mark = self.engine.cells[supercell][0]
                symbol = get_image_symbol(mark)
                if symbol:
                    self.boards[supercell].mark.set_from_file(symbol)
    
    def button_enter(self, button):
        """Mouse enter handler for all buttons.
        
        Sets the image for the button when the player enters the button.
        Between this and mouse leave handler, the effect is that the
        symbol is dragged around the board.
        
        """
        button.image.set_from_file(
                get_image_symbol(self.get_player(), True))
    
    def button_leave(self, button):
        """Mouse leave handler for all buttons.
        
        Clears the button's image. Between this and mouse enter handler,
        the effect is that the symbol is dragged around the board.
        
        """
        button.image.clear()
    
    def replay(self, game_file):
        """Replay a saved game.
        
        Expects an open file object containing a JSON object literal.
        
        The JSON literal is expected to have an attribute 'moves' which
        is an array of arrays in the form ``[player, board, cell]``.
        
        """
        def send_click(moves_iter):
            """Callback for the timer.
            
            Takes the next move and clicks the button it refers to.
            
            """
            try:
                player, board, cell = moves_iter.next()
                if all([x is not None for x in (player, board, cell)]):
                    self.boards[board].buttons[cell].clicked()
            except StopIteration:
                return False
            return True
        
        # Load the game from the file and determine playback or
        # instant load.
        game_state = json.load(game_file)
        timeout = 0 if game_state['winner'] is None else 1
        
        # Have GTK handle the timing. Since play back can take up to
        # 81 seconds or so, this makes it not block the UI; It just
        # schedules a repeating event instead.
        return gobject.timeout_add_seconds(timeout, send_click,
            iter(game_state['moves']))

class GameWindow(gtk.Window):
    """The game window."""
    
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("Super Tic-Tac-Toe")
        self.connect("destroy", gtk.main_quit)
        
        # Instantiate the game board
        self.game = SuperTicTacToeBoard()
        
        # Build the menu bar
        main_menu = gtk.MenuBar()
        menu_game = gtk.MenuItem("Game")
        menu_game_sub = gtk.Menu()
        menu_game_new = gtk.MenuItem("New Game")
        menu_game_save = gtk.MenuItem("Save Game")
        menu_game_load = gtk.MenuItem("Load Game")
        menu_game_quit = gtk.MenuItem("Exit Game")
        menu_game_new.connect("activate", self.game_new)
        menu_game_save.connect("activate", self.game_save)
        menu_game_load.connect("activate", self.game_load)
        menu_game_quit.connect("activate", gtk.main_quit)
        
        menu_help = gtk.MenuItem("Help")
        menu_help_sub = gtk.Menu()
        menu_help_help = gtk.MenuItem("Help")
        menu_help_about = gtk.MenuItem("About")
        menu_help_help.connect("activate", self.help_help)
        menu_help_about.connect("activate", self.help_about)
        
        main_menu.append(menu_game)
        menu_game.set_submenu(menu_game_sub)
        menu_game_sub.append(menu_game_new)
        menu_game_sub.append(menu_game_save)
        menu_game_sub.append(menu_game_load)
        menu_game_sub.append(gtk.SeperatorMenuItem())
        menu_game_sub.append(menu_game_quit)
        
        main_menu.append(menu_help)
        menu_help.set_submenu(menu_help_sub)
        menu_help_sub.append(menu_help_help)
        menu_help_sub.append(menu_help_about)
        
        # Contain the game board in a box so it can be removed and
        # replaced
        self.game_container = gtk.VBox()
        self.game_container.pack_start(self.game)
        
        # construct the layout. VBox places everything vertically, so
        # the menu is on top, followed by the game board and finally
        # the status bar.
        main_layout = gtk.VBox()
        main_layout.pack_start(main_menu)
        main_layout.pack_start(self.game_container)
        main_layout.pack_start(gtk.Statusbar())
        
        self.add(main_layout)
    
    def game_new(self, widget):
        """Abandon the current game and start a new one.
        
        The old game will be unrecoverably lost unless saved first.
        
        """
        # pull the game board out and delete it.
        self.game_container.remove(self.game)
        del self.game
        
        # reconstruct the game board and insert it into the layout.
        self.game = SuperTicTacToeBoard()
        self.game_container.pack_start(self.game)
        
        #  have to show everything again.
        self.game_container.show_all()
    
    def game_save(self, widget):
        """Menu activation handler for saving the game.
        
        File format is determined by the game engine.
        
        """
        dialog = gtk.FileChooserDialog(title="Save the game",
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            # Open the indicated file and write the game state to it.
            # The with statement handles closing the file when the
            # block leaves scope.
            with open(dialog.get_filename(), "w") as save_target:
                save_target.write(self.game.engine.dump())
        
        dialog.destroy()
    
    def game_load(self, widget):
        """Menu activation handler for loading a game.
        
        """
        dialog = gtk.FileChooserDialog(title="Open a replay file",
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(
                gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            with open(dialog.get_filename()) as open_target:
                self.game.replay(open_target)
        dialog.destroy()
    
    def help_about(self, widget):
        """Menu activation handler for the About dialog.
        
        """
        about = gtk.AboutDialog()
        about.set_name("Super Tic-Tac-Toe")
        about.set_version("0.0.1")
        about.set_authors(["Erik Youngren <erik.youngren@gmail.com>"])
        about.set_comments("""A variation on Tic-Tac-Toe""")
        about.run()
        about.destroy()
    
    def help_help(self, widget):
        """Menu activation handler for the help files.
        
        Opens the online help page in the default web browser.
        
        """
        webbrowser.open_new_tab(
            "http://artanis.github.com/supertictactoe/help.html#pygtk")

# It might be necessary to run this from the interactive interpreter or
# from another script, so these are in a function instead of in the
# below if statement.
def main():
    """Create a game window and run it.
    
    """
    app = GameWindow()
    app.show_all()
    gtk.main()

# Call the main function if this file is run as a script.
# ``__name__`` is only "__main__" in that situation. If imported by
# another script or by the interactive interpreter (a case in which
# starting up the game window might not be appreciated) __name__ will
# be the filename sans file extension.
if __name__ == "__main__":
    main()

