# System Modules
import sys
import uuid

# External Modules
try:
    import json
except:
    from django.utils import simplejson as json

from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# Local Modules
from supertictactoe import SuperTicTacToe

class GameStateHandler(webapp.RequestHandler):
    def get(self):
        game_id = self.get('game_id')
        
        if game_id is not None:
            game = Game.get_by_key_name(game_id)
            self.response.out.write(game.game_state.dump())
        else:
            self.error(404)

def update_clients(game):
    message = json.loads(game._game_state)
    message['mode'] = 'game-state'
    message = json.dumps(message)
    
    channel.send_message(game.player_x.user_id(), message)
    #channel.send_message(game.player_o.user_id(), message)

class Game(db.Model):
    player_x = db.UserProperty(required=True)
    player_o = db.UserProperty()
    move_x = db.BooleanProperty(default=True)
    _game_state = db.TextProperty()
    
    def get_player(self, user):
        if self.player_x == user: return "X"
        elif self.player_o == user: return "O"
        else: return None
    
    def _fget_game_state(self):
        return SuperTicTacToe.load(self._game_state)
    
    def _fset_game_state(self, value):
        self._game_state = value.dump()
    
    game_state = property(_fget_game_state, _fset_game_state)

class MainPageHandler(webapp.RequestHandler):
    def get(self):
        """Entry point for application.
        
        Logs the user in (if he hasn't yet) and then redirects to the
        web client, which handles the rest over Ajax.
        
        There will be another handler to do non-redirect logins.
        Eventually.
        
        """
        user = users.get_current_user()
        
        if user is None:
            self.redirect(users.create_login_url(self.request.uri))
            return
        
        self.redirect("/web-client/client.html")
    
    def post(self):
        pass

class MoveHandler(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        
        game_id = self.request.get('game_id', None)
        board = int(self.request.get('board', None))
        square = int(self.request.get('square', None))
        
        game_model = Game.get_by_key_name(game_id)
        player = game_model.get_player(user)
        
        print >>sys.stderr, game_id, (board, square), user.user_id()
        
        if board is None or square is None or game_model is None:
            # Bad request
            self.error(400)
        
        if player is None:
            # Unauthorized, and that's not going to change.
            self.error(403)
        else:
            game = game_model.game_state
            if game.move(player, board, square):
                # Acceptable move
                self.error(204)
                game_model.game_state = game
                game_model.put()
                update_clients(game_model)
            else:
                # Illegal move
                self.error(400)

class GameFactory(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        
        if user is not None:
            game_id = str(uuid.uuid1())
            
            game = Game(key_name = game_id, player_x = user)
            game.game_state = SuperTicTacToe()
            game.put()
            
            channel.send_message(user.user_id(), json.dumps({
                'mode': "new-game",
                'game_id': game_id}))
        else:
            # not going to catch not-logged-in everywhere. User should
            # login before this stage.
            self.error(401)

class ChannelFactory(webapp.RequestHandler):
    """Serves channels by Ajax"""
    
    def get(self):
        """Create a channel for the user"""
        
        user = users.get_current_user()
        
        if user is not None:
            channel_id = user.user_id()
            channel_token = channel.create_channel(channel_id)
            
            self.response.headers['Content-Type'] = 'text/javascript'
            self.response.out.write(json.dumps({
                "channel_id": channel_id,
                "channel_token": channel_token}))
    
    def post(self):
        """Echo back testing"""
        
        channel_id = self.request.get('channel_id')
        
        if channel_id:
            channel.send_message(channel_id, json.dumps({
            'mode': 'channel-test',
            'status': 'Ok'}))

def main():
    app = webapp.WSGIApplication([
        ('/', MainPageHandler),
        ('/channel', ChannelFactory),
        ('/new-game', GameFactory),
        ('/move', MoveHandler)])
    
    run_wsgi_app(app)


if __name__ == '__main__':
    main()
