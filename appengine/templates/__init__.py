from web.template import CompiledTemplate, ForLoop, TemplateResult


# coding: utf-8
def __base__ (content):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<html>\n'])
    extend_([u'    <head>\n'])
    extend_([u'        <meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n'])
    extend_([u'        <title>', escape_(content.title, True), u'</title>\n'])
    extend_([u'        <link rel="stylesheet" href="/static/style.css" />\n'])
    extend_([u'        <script src="/_ah/channel/jsapi"></script>\n'])
    extend_([u'        <script src="https://www.google.com/jsapi"></script>\n'])
    extend_([u'        <script>\n'])
    extend_([u'            google.load("jquery", "1", {uncompressed:true});\n'])
    extend_([u'        </script>\n'])
    extend_([u'    </head>\n'])
    extend_([u'    <body>\n'])
    extend_([u'    <header>\n'])
    extend_([u'        <h1>', escape_(content.title, True), u'</h1>\n'])
    extend_([u'    </header>\n'])
    extend_([u'    <section id="content">\n'])
    extend_([u'        ', escape_(content, False), u'\n'])
    extend_([u'    </section>\n'])
    extend_([u'    <footer>\n'])
    extend_([u'    </footer>\n'])
    extend_([u'    </body>\n'])
    extend_([u'</html>\n'])

    return self

__base__ = CompiledTemplate(__base__, 'templates/__base__.html')
join_ = __base__._join; escape_ = __base__._escape

# coding: utf-8
def game_board():
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    self['title'] = "Super Tic-Tac-Toe"
    extend_([u'<script src="/static/game.js"></script>\n'])
    extend_([u'<div id="SuperTicTacToe">\n'])
    extend_([u'    <table class="super board">\n'])
    extend_([u'        <tr>\n'])
    for x in loop.setup(range(9)):
        extend_(['        ', u'<td class="board square" id="SubBoard_', escape_(x, True), u'" data-square="', escape_(x, True), u'">\n'])
        extend_(['        ', u'    <table>\n'])
        extend_(['        ', u'        <tr>\n'])
        for y in loop.setup(range(9)):
            extend_(['                ', u'<td class="square cell" data-claimed=""\n'])
            extend_(['                ', u'    data-board="', escape_(x, True), u'" data-square="', escape_(y, True), u'"><div/></td>\n'])
            if y%9%3 == 2 and not loop.last:
                extend_(['                ', u'</tr>\n'])
                extend_(['                ', u'<tr>\n'])
        extend_(['        ', u'        </tr>\n'])
        extend_(['        ', u'    </table>\n'])
        extend_(['        ', u'</td>\n'])
        if x % 9 % 3 == 2 and not loop.last:
            extend_(['        ', u'</tr>\n'])
            extend_(['        ', u'<tr>\n'])
    extend_([u'        </tr>\n'])
    extend_([u'    </table>\n'])
    extend_([u'</div>\n'])

    return self

game_board = CompiledTemplate(game_board, 'templates/game_board.html')
join_ = game_board._join; escape_ = game_board._escape

# coding: utf-8
def index (stuff):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    self['title'] = "Super Tic-Tac-Toe"
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<p>', escape_(stuff, True), u'</p>\n'])

    return self

index = CompiledTemplate(index, 'templates/index.html')
join_ = index._join; escape_ = index._escape

