# System Modules
import gtk
import yaml
import gobject

# External Modules


# Local Modules
import supertictactoe

SYMBOL_PLAYER_X = "images/symbol-player-x.png"
SYMBOL_PLAYER_O = "images/symbol-player-o.png"
SYMBOL_PLAYER_X_SMALL = "images/symbol-player-x-small.png"
SYMBOL_PLAYER_O_SMALL = "images/symbol-player-o-small.png"

def get_image_symbol(symbol, small=False):
    if symbol == "X":
        return SYMBOL_PLAYER_X_SMALL if small else SYMBOL_PLAYER_X
    elif symbol == "O":
        return SYMBOL_PLAYER_O_SMALL if small else SYMBOL_PLAYER_O
    else:
        return None

def linear2cartesian(position, wrap):
    return (position / wrap, position % wrap)

def cartesian2linear(x_pos, y_pos, wrap):
    return x_pos + y_pos * wrap

class TicTacToeBoard(gtk.Table):
    def __init__(self):
        gtk.Table.__init__(self)
        
        self.set_row_spacings(1)
        self.set_col_spacings(1)
        
        self.mark = gtk.Image()
        self.attach(self.mark, 0, 3, 0, 3)
        
        self.buttons = []
        for position in range(9):
            x, y = linear2cartesian(position, 3)
            
            btn = gtk.Button()
            btn.image = gtk.Image()
            btn.set_size_request(50, 50)
            btn.add(btn.image)
            btn.claimed = False
            
            self.attach(btn, y, y+1, x, x+1)
            self.buttons.append(btn)
        

class SuperTicTacToeBoard(gtk.Table):
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
        
        for supercell, cell, board, button in self.buttons:
            button.connect("clicked",
                self.button_clicked, supercell, cell)
            button.connect("enter", self.button_enter)
            button.connect("leave", self.button_leave)
    
    def get_player(self, move=0):
        return "X" if (len(self.engine.moves) - move) % 2 == 0 else "O"
    
    @property
    def buttons(self):
        for supercell, board in enumerate(self.boards):
            for cell, button in enumerate(board.buttons):
                yield (supercell, cell, board, button)
    
    def hint_next(self, next_index):
        for supercell, cell, board, button in self.buttons:
            if next_index is None or supercell == next_index:
                label = button.get_label()
                if not button.claimed:
                    button.set_sensitive(True)
            else:
                button.set_sensitive(False)
    
    def button_clicked(self, button, supercell, cell):
        if self.engine.move(self.get_player(), supercell, cell):
            button.set_sensitive(False)
            button.claimed = True
            button.image.set_from_file(
                get_image_symbol(self.get_player(-1), True))
            #button.set_label(self.get_player(-1))
            
            self.hint_next(self.engine.next)
            
            if self.engine.cells[supercell] is not None:
                mark = self.engine.cells[supercell]
                symbol = get_image_symbol(mark)
                if symbol:
                    self.boards[supercell].mark.set_from_file(symbol)
    
    def button_enter(self, button):
        #button.set_label(self.get_player())
        button.image.set_from_file(
                get_image_symbol(self.get_player(), True))
    
    def button_leave(self, button):
        #button.set_label("")
        button.image.clear()
    
    def replay(self, game_file):
        moves = yaml.load(game_file)
        
        def send_click(moves_iter):
            try:
                player, board, cell = moves_iter.next()
                if all([x is not None for x in (player, board, cell)]):
                    self.boards[board].buttons[cell].clicked()
            except StopIteration:
                return False
            return True
        
        
        return gobject.timeout_add_seconds(1, send_click, iter(moves))

class GameWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect("destroy", gtk.main_quit)
        
        
        self.game = SuperTicTacToeBoard()
        
        main_menu = gtk.MenuBar()
        menu_game = gtk.MenuItem("Game")
        menu_game_sub = gtk.Menu()
        menu_game_new = gtk.MenuItem("New Game")
        menu_game_save = gtk.MenuItem("Save Game")
        menu_game_load = gtk.MenuItem("Load Game")
        menu_game_new.connect("activate", self.game_new)
        menu_game_save.connect("activate", self.game_save)
        menu_game_load.connect("activate", self.game_load)
        
        main_menu.append(menu_game)
        menu_game.set_submenu(menu_game_sub)
        menu_game_sub.append(menu_game_new)
        menu_game_sub.append(menu_game_save)
        menu_game_sub.append(menu_game_load)
        
        self.game_container = gtk.VBox()
        self.game_container.pack_start(self.game)
        
        main_layout = gtk.VBox()
        main_layout.pack_start(main_menu)
        main_layout.pack_start(self.game_container)
        main_layout.pack_start(gtk.Statusbar())
        
        self.add(main_layout)
    
    def game_new(self, widget):
        # pull the game board out and remove it
        self.game_container.remove(self.game)
        del self.game
        
        # reconstruct the game board and re-insert it
        self.game = SuperTicTacToeBoard()
        self.game_container.pack_start(self.game)
        self.game_container.show_all()
    
    def game_save(self, widget):
        dialog = gtk.FileChooserDialog(title="Save the game",
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(
                gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            with open(dialog.get_filename(), "w") as save_target:
                save_target.write(repr(self.game.engine))
        dialog.destroy()
    
    def game_load(self, widget):
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

def main(*args, **kwargs):
    app = GameWindow()
    
    app.show_all()
    
    gtk.main()

if __name__ == "__main__":
    import sys
    main(*sys.argv)
