# System Modules
import sys

# External Modules
from django.utils import simplejson as json
from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import web

# Local Modules
#import supertictactoe

# Application
render = web.template.render('templates', base='__base__')

class MainPageHandler(webapp.RequestHandler):
    def get(self):
        game_id = self.request.get('game_id')
        user = users.get_current_user()
        
        if user is None:
            self.redirect(users.create_login_url(self.request.uri))
            return
        
        self.response.out.write(
            render.game_board())
    
    def post(self):
        pass

class MoveHandler(webapp.RequestHandler):
    def post(self):
        game_id = self.request.get('game_id')
        board = self.request.get('board')
        square = self.request.get('square')
        
        print >>sys.stderr, game_id, (board, square)

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
        print >>sys.stderr, "(",channel_id, ")"
        if channel_id:
            channel.send_message(channel_id, json.dumps({
            'mode': 'channel-test',
            'status': 'Ok'}))

def main():
    app = webapp.WSGIApplication([
        ('/', MainPageHandler),
        ('/channel', ChannelFactory),
        ('/move', MoveHandler)])
    
    run_wsgi_app(app)


if __name__ == '__main__':
    main()
