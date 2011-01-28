# System Modules
import sys

import web
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

render = web.template.render('templates', base='__base__')

class Root:
    def GET(self):
        return render.index("Test")

class Game:
    def GET(self, game_id):
        return render.game("Test", lambda x, y: x * 3 + y)

urls = ('/', 'Root',
    '/game/([A-Za-z0-9]*)', 'Game')

app = web.application(urls, globals())

def main():
    app.cgirun()


if __name__ == '__main__':
    main()
