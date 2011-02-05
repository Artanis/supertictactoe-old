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

PLAYER_X = "X"
PLAYER_O = "O"

class Game(db.Model):
    player_x = db.UserProperty(required=True)
    player_o = db.UserProperty()
    move_x = db.BooleanProperty(default=True)
    public_game = db.BooleanProperty(default=True)
    _game_state = db.TextProperty()
    
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)
    
    def update_players(self):
        # TODO: find a better way to do this:
        message = json.loads(self._game_state)
        message['mode'] = 'game-state'
        message['move_x'] = self.move_x if self.player_o is not None else None
        message = json.dumps(message)
        
        #print >>sys.stderr, str(self)
        
        channel.send_message(self.player_x.user_id(), message)
        
        if self.player_o is not None:
            channel.send_message(self.player_o.user_id(), message)
    
    def get_player(self, user):
        if self.player_x == user: return (PLAYER_X, self.move_x)
        elif self.player_o == user: return (PLAYER_O, not self.move_x)
        else: return (None, False)
    
    def _fget_game_state(self):
        return SuperTicTacToe.load(self._game_state)
    
    def _fset_game_state(self, value):
        self._game_state = value.dump()
    
    def __contains__(self, item):
        return item in (self.player_x, self.player_o)
    
    def __repr__(self):
        return ("<Game(player_x='%s', player_o='%s', public_game='%s')>" %
            (self.player_x, self.player_o, self.public_game))
    
    game_state = property(_fget_game_state, _fset_game_state)


class GameStateHandler(webapp.RequestHandler):
    def get(self):
        """Sends the game-state.
        
        Public games are available to anyone with the game ID. Private
        games only to the players.
        
        Useful for archiving games played on the server locally.
        
        """
        
        user = users.get_current_user()
        game_id = self.request.get('game_id', None)
        
        if game_id is not None:
            game = Game.get_by_key_name(game_id)
            if game.public_game or user in game:
                self.response.out.write(game.game_state.dump())
            else:
                self.error(403)
                return
        else:
            self.error(404)
    
    def post(self):
        """Sends the game state to both players over the channel.
        
        Used for forcing a game-state refresh.
        
        """
        
        user = users.get_current_user()
        game_id = self.request.get('game_id', None)
        
        if game_id is not None:
            game = Game.get_by_key_name(game_id)
            
            if user in game:
                game.update_players()
                self.error(200)
                return
            else:
                self.error(403)
                return
        else:
            self.error(404)
            return

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
        
        #print >>sys.stderr, game_id, (board, square), user.user_id()
        
        # Bad request
        if board is None or square is None or game_id is None:
            self.error(400)
            return
        
        game_model = Game.get_by_key_name(game_id)
        player, is_player_turn = game_model.get_player(user)
        
        if player is None:
            # Unauthorized, and that's not going to change.
            self.error(403)
            return
        
        if not is_player_turn:
            # Turn enforcement
            self.error(409)
            return
        
        else:
            game = game_model.game_state
            if game.move(player, board, square):
                # Acceptable move
                game_model.game_state = game
                game_model.move_x = not game_model.move_x
                game_model.put()
                game_model.update_players()
                self.error(204)
                return
            else:
                # Illegal move
                self.error(403)
                return

class GameFactory(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        game_id = self.request.get('game_id', None)
        public_game = self.request.get('public_game', True)
        
        if user is not None:
            if game_id is None:
                # makes a new game
                game_id = str(uuid.uuid1())
                
                game_model = Game(
                    key_name = game_id,
                    player_x = user,
                    public_game=public_game)
                
                game_model.game_state = SuperTicTacToe()
                game_model.put()
                
                channel.send_message(user.user_id(), json.dumps({
                    'mode': "start-game",
                    'player': PLAYER_X,
                    'game_id': game_id}))
                self.error(200)
            else:
                # join an existing game
                game_model = Game.get_by_key_name(game_id)
                if user in game_model:
                    #returning player
                    player, is_player_turn = game_model.get_player(user)
                    channel.send_message(user.user_id(), json.dumps({
                        'mode': 'start-game',
                        'player': player,
                        'game_id': game_id}))
                    game_model.update_players()
                    self.error(200)
                elif game_model.player_o is None:
                    # Adding player O
                    game_model.player_o = user
                    channel.send_message(user.user_id(), json.dumps({
                        'mode': 'start-game',
                        'player': PLAYER_O,
                        'game_id': game_id}))
                    game_model.update_players()
                    game_model.put()
                    self.error(200)
                    return
                else:
                    self.error(403)
                    return
        else:
            # not going to catch not-logged-in everywhere. User should
            # login before this stage.
            self.error(401)

class LobbyHandler(webapp.RequestHandler):
    def get(self):
        query = db.Query(Game)
        query.filter("public_game = ", True)
        query.filter("player_o = ", None)
        query.order("modified")
        query.order("created")
        
        lobby = []
        for game in query.fetch(10):
            lobby.append({
                'game_id': game.key().name(),
                'player_x': game.player_x.nickname(),
                'player_o': game.player_o.nickname() if game.player_o else None,
                'created': game.created.isoformat(),
                'modified':game.modified.isoformat()})
        
        self.response.out.write(json.dumps(lobby))

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
        ('/game', GameFactory),
        ('/game-state', GameStateHandler),
        ('/move', MoveHandler),
        ('/lobby', LobbyHandler)])
    
    run_wsgi_app(app)


if __name__ == '__main__':
    main()
