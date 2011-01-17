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
    extend_([u'        <script type="text/javascript" src="https://www.google.com/jsapi"></script>\n'])
    extend_([u'        <script type="text/javascript">\n'])
    extend_([u'            // <!--\n'])
    extend_([u'            google.load("jquery", "1");\n'])
    extend_([u'            // -->\n'])
    extend_([u'        </script>\n'])
    extend_([u'    </head>\n'])
    extend_([u'    <body>\n'])
    extend_([u'    <h1>', escape_(content.title, True), u'</h1>\n'])
    extend_([u'    <div>\n'])
    extend_([u'    ', escape_(content, False), u'\n'])
    extend_([u'    </div>\n'])
    extend_([u'    </body>\n'])
    extend_([u'</html>\n'])

    return self

__base__ = CompiledTemplate(__base__, 'templates/__base__.html')
join_ = __base__._join; escape_ = __base__._escape

# coding: utf-8
def game (state, pos2lin):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    self['title'] = "Playing Super Tic-Tac-Toe"
    extend_([u'<script type="text/javascript" src="/static/game.js"></script>\n'])
    extend_([u'<table class="board" id="superboard">\n'])
    for w in loop.setup(range(3)):
        extend_([u'<tr>\n'])
        for x in loop.setup(range(3)):
            extend_([u'<td class="cell supercell">\n'])
            extend_([u'    <table class="board" id="board-', escape_(pos2lin(w, x), True), u'">\n'])
            for y in loop.setup(range(3)):
                extend_(['    ', u'<tr>\n'])
                for z in loop.setup(range(3)):
                    extend_(['    ', u'<td class="cell">\n'])
                    extend_(['    ', u'    <input type="button"\n'])
                    extend_(['    ', u'           data-board="', escape_(pos2lin(w, x), True), u'"\n'])
                    extend_(['    ', u'           data-cell="', escape_(pos2lin(y, z), True), u'" />\n'])
                    extend_(['    ', u'</td>\n'])
                extend_(['    ', u'</tr>\n'])
            extend_([u'    </table>\n'])
            extend_([u'</td>\n'])
        extend_([u'</tr>\n'])
    extend_([u'</table>\n'])

    return self

game = CompiledTemplate(game, 'templates/game.html')
join_ = game._join; escape_ = game._escape

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

