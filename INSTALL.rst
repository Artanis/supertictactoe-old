========================================
Installing and running Super Tic-Tac-Toe
========================================

For all platforms, download and unpack the code::
        
        https://github.com/Artanis/supertictactoe

If you plan on running the game server locally, download and setup the
Python development server environment for your platform::
    
    http://code.google.com/appengine/downloads.html#Google_App_Engine_SDK_for_Python
    
The App Engine version should be running at
http://super-tic-tac-toe.appspot.com if you just want to look at it, however.

Ubuntu Linux
============
1.  Ubuntu should come with the lastest Python 2.7 release.
    
    For the development server environment, you will also need
    Python 2.5::
        
        sudo apt-add-repository fkrull/deadsnakes
        sudo apt-get update
        sudo apt-get install python2.5
    
2.  GTK and PyGTK should already be installed.

To run the PyGTK application, open a terminal in the project folder and
run::
    
    python st3.py

For the development app server environment to run the game server
locally::
    
    /path/to/dev_appserver.py app-engine/

Windows
=======
1.  Make sure you have Python installed::
        
        http://www.python.org/download/releases/2.7.1/
    
    Python 3.0 should also work, but no guarantees.
    
    If you plan on running the game server in the development Google
    App Engine environment, you will also need 2.5::
        
        http://www.python.org/download/releases/2.5.5/
    
2.  Install PyGTK for the GTK version::
        
        http://www.pygtk.org/downloads.html
    
    The all-in-one is recommended, though as long as GTK and PyGTK is
    installed on the system it should be ok.

For now, the gtk version is named st3.py, and is in the root folder of
the project (assuming ``C:\supertictactoe``). To run the GTK version,
open a command prompt in the unpacked project and run this command::
    
    C:\supertictactoe> python st3.py

Assuming that you have set up the development app server, to run the
game server locally, use::
    
    C:\supertictactoe> dev_appserver.py app-engine\

