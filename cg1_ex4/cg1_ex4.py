# -*- coding: utf-8 -*-
"""
This is the main application file for the exercise 4 of the course computer 
graphics 1.

The comments in this file are written in the reStructured text format and adhere
to the commenting style used by epydoc.
"""

if __name__ == '__main__':
    # Import Psyco if available
    try:
        import psyco
        print(u"Using psyco with full optimization...")
        psyco.full()
    except ImportError:
        pass

import logging
import sys
from optparse import OptionParser
from ConfigParser import SafeConfigParser

import Image
import OpenGL
OpenGL.ERROR_CHECKING = False # to avoid a segfault with mesa >= 7.0.3
from OpenGL.arrays import numpymodule
numpymodule.NumpyHandler.ERROR_ON_COPY = True
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from eventdispatcher import EventDispatcher
from handler import DefaultHandler, TextureEditHandler, TexturedObjectHandler
from scene_ex4 import InteractivelyTexturedScene

class Application(object):
    def __init__(self):
        """Initialize a new application by creating a logger object and calling
        the required initialization methods.
        """
        self._init_log()
        self._init_config(['cg1_defaults.conf'])
        self._init_windows()
        self._init_scene()
        self._init_callbacks()
            
    def __del__(self):
        self._log.info(u"Exiting...")
    
    def _init_log(self):
        logging.basicConfig(level=logging.DEBUG)
        self._log = logging.getLogger("Application")
        self._log.info(u"Starting up...")
    
    def _init_config(self, default_config_files):
        self._log.info(u"Initializing configuration...")
        config_files = list(default_config_files)
        
        parser = OptionParser()
        parser.add_option('-c', '--conf', dest='config_file', default=None, help=u"config file to use (besides cg1_defaults.conf)")
        (options, args) = parser.parse_args()
        
        if options.config_file:
            config_files.append(options.config_file)
        
        self._log.info(u"Reading config files %s...", config_files)
        self._config = SafeConfigParser()
        self._config.read(config_files)
        
        self._current_texture = Image.open(self._config.get('general', 'start_texture'))
        #sys.setrecursionlimit(4000)
        #self._log.info(u"Recursion limit is now %d." % sys.getrecursionlimit())
    
    def _init_windows(self):
        self._log.info(u"Initializing windows...")
        glutInit([])
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        window_width  = self._config.getint('window', 'width')
        window_height = self._config.getint('window', 'height')
        glutInitWindowSize(window_width, window_height)
        glutInitWindowPosition(self._config.getint('window', 'x'), self._config.getint('window', 'y'))
        self._window = glutCreateWindow(self._config.get('window', 'title'))
        self._subwindows = []
        gap = self._config.getint('window', 'gap')
        self._subwindows.append(glutCreateSubWindow(self._window, gap, gap, (window_width-3*gap) / 2, (window_height-2*gap)))
        self._subwindows.append(glutCreateSubWindow(self._window, (window_width-3*gap) / 2 + 2*gap, gap, (window_width-3*gap) / 2, (window_height-2*gap)))
        glutSetWindow(self._window)
    
    def _init_callbacks(self):
        self._log.info(u"Initializing callbacks...")
        
        self._main_dispatcher       = EventDispatcher()
        self._texture_dispatcher    = EventDispatcher()
        self._object_dispatcher     = EventDispatcher()
        
        self._main_handler          = DefaultHandler(self)
        self._texture_handler       = TextureEditHandler(self, self._current_scene.children[0])
        self._object_handler        = TexturedObjectHandler(self, self._current_scene.children[1])
        
        self._main_dispatcher.push_handlers(self._main_handler)
        self._texture_dispatcher.push_handlers(self._texture_handler)
        self._object_dispatcher.push_handlers(self._object_handler)
        
        glutSetWindow(self._window)
        glutKeyboardFunc(self._main_dispatcher.handle_type('keyboard'))
        glutReshapeFunc(self._main_dispatcher.handle_type('reshape'))
        
        self._menu_main = glutCreateMenu(self._main_dispatcher.handle_type('menu'))
        glutAddMenuEntry("Quit", self._main_handler.get_menu_id('menu_quit'))
        glutAttachMenu(GLUT_RIGHT_BUTTON)
        
        glutSetWindow(self._subwindows[0])
        glutKeyboardFunc(self._main_dispatcher.handle_type('keyboard'))
        glutReshapeFunc(self._texture_dispatcher.handle_type('reshape'))
        glutMouseFunc(self._texture_dispatcher.handle_type('mouse_button'))
        glutMotionFunc(self._texture_dispatcher.handle_type('mouse_motion'))
        glutPassiveMotionFunc(self._texture_dispatcher.handle_type('mouse_motion'))
        
        self._menu_texture = glutCreateMenu(self._texture_dispatcher.handle_type('menu'))
        glutAddMenuEntry("Clear", self._texture_handler.get_menu_id('menu_clear'))
        glutAddMenuEntry("Quit", self._texture_handler.get_menu_id('menu_quit'))
        glutAttachMenu(GLUT_RIGHT_BUTTON)
        
        glutSetWindow(self._subwindows[1])
        glutKeyboardFunc(self._main_dispatcher.handle_type('keyboard'))
        glutReshapeFunc(self._object_dispatcher.handle_type('reshape'))
        glutMouseFunc(self._object_dispatcher.handle_type('mouse_button'))
        glutMotionFunc(self._object_dispatcher.handle_type('mouse_motion'))
        
        self._menu_main = glutCreateMenu(self._object_dispatcher.handle_type('menu'))
        glutAddMenuEntry("Quit", self._object_handler.get_menu_id('menu_quit'))
        glutAttachMenu(GLUT_RIGHT_BUTTON)
        
        glutTimerFunc(1, self.update, 1)
    
    def _init_scene(self):
        self._current_scene = InteractivelyTexturedScene(self)
        if self._current_scene:
            self._current_scene.init()
            glutSetWindow(self._window)
            glutDisplayFunc(self._current_scene.render)
            glutSetWindow(self._subwindows[0])
            glutDisplayFunc(self._current_scene.children[0].render)
            glutSetWindow(self._subwindows[1])
            glutDisplayFunc(self._current_scene.children[1].render)
    
    def run(self):
        self._log.info(u"Running...")
        self._time = glutGet(GLUT_ELAPSED_TIME)
        glutMainLoop()
    
    def stop(self):
        self._log.info(u"Stopping...")
        sys.exit()
    
    def update(self, enabled):
        # update the current time
        time = glutGet(GLUT_ELAPSED_TIME)
        d_time = time - self._time
        self._time = time
        
        if enabled == 1:
            #self._log.debug(u"%u ms elapsed", d_time)
            
            if self._current_scene:
                self._current_scene.update(d_time)
                
        glutTimerFunc(int(1000/self._config.getint('general', 'framerate')) - (glutGet(GLUT_ELAPSED_TIME) - time), self.update, 1)
    
#    def render(self):
#        glutSetWindow(self._window)
#        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#        glMatrixMode(GL_MODELVIEW)
#        glLoadIdentity()
#        #gluLookAt(0.0, 0.0, 15.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
#        gluLookAt(0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0);
#        #glTranslate(0, 0, -15)
#        
#        if self._current_scene:
#            self._current_scene.render()
#        
#        glutSetWindow(self._window)
#        glutSwapBuffers()

if __name__ == '__main__':
    app = Application()
    app.run()
