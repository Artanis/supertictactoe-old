#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
