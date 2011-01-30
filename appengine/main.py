# System Modules
import sys
import pickle
import uuid

# External Modules
from django.utils import simplejson as json
from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import web

# Local Modules
from supertictactoe import SuperTicTacToe

# Application
render = web.template.render('templates', base='__base__')

class Game(db.Model):
    player_x = db.UserProperty(required=True)
    player_o = db.UserProperty()
    move_x = db.BooleanProperty(default=True)
    _game_state = db.BlobProperty()
    
    def __fget_game_state(self):
        return SuperTicTacToe.load(self._game_state)
    
    def __fset_game_state(self, value):
        self._game_state = value.dump()
    
    game_state = property(__fget_game_state, __fset_game_state)

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
        game_id = self.request.get('game_id')
        board = self.request.get('board')
        square = self.request.get('square')
        
        game = Game.get_by_key_name(game_id)
        
        print >>sys.stderr, game_id, (board, square)

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
