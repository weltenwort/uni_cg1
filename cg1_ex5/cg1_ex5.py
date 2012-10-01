# -*- coding: utf-8 -*-
"""
This is the main application file for the exercise 1 of the course computer 
graphics 1.

The comments in this file are written in the reStructured text format and adhere
to the commenting style used by epydoc.
"""

import logging
import sys
from optparse import OptionParser
from ConfigParser import SafeConfigParser

if __name__ == '__main__':
    # Import Psyco if available
    try:
        import psyco
        print(u"Using psyco with full optimization...")
        #psyco.log()
        #psyco.profile()
        psyco.full()
    except ImportError:
        pass


import Image
import OpenGL
#OpenGL.ERROR_CHECKING = False # to avoid a segfault with mesa >= 7.0.3
from OpenGL.arrays import numpymodule
numpymodule.NumpyHandler.ERROR_ON_COPY = True
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from eventdispatcher import EventDispatcher
from handler import DefaultHandler
from scene_ex5 import RaytraceScene

class Application(object):
    def __init__(self):
        """Initialize a new application by creating a logger object and calling
        the required initialization methods.
        """
        self._init_log()
        self._init_config(['cg1_defaults.conf'])
        self._init_windows()
        self._init_callbacks()
        self._init_scene()
            
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
        
        sys.setrecursionlimit(4000)
        self._log.info(u"Recursion limit is now %d." % sys.getrecursionlimit())
    
    def _init_windows(self):
        self._log.info(u"Initializing windows...")
        glutInit([])
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self._config.getint('window', 'width'), self._config.getint('window', 'height'))
        glutInitWindowPosition(self._config.getint('window', 'x'), self._config.getint('window', 'y'))
        self._window = glutCreateWindow(self._config.get('window', 'title'))
    
    def _init_callbacks(self):
        self._log.info(u"Initializing callbacks...")
        self._main_dispatcher = EventDispatcher()
        self._main_handler = DefaultHandler(self)
        
        self._main_dispatcher.push_handlers(self._main_handler)
        
        glutKeyboardFunc(self._main_dispatcher.handle_type('keyboard'))
        glutReshapeFunc(self._main_dispatcher.handle_type('reshape'))
        glutMouseFunc(self._main_dispatcher.handle_type('mouse_button'))
        glutMotionFunc(self._main_dispatcher.handle_type('mouse_motion'))
        glutPassiveMotionFunc(self._main_dispatcher.handle_type('mouse_motion'))
        
        self._menu_main = glutCreateMenu(self._main_dispatcher.handle_type('menu'))
        glutAddMenuEntry("Quit", self._main_handler.get_menu_id('menu_quit'))
        glutAddMenuEntry("Raytrace", self._main_handler.get_menu_id('menu_raytrace'))
        glutAddMenuEntry("Take Screenshot", self._main_handler.get_menu_id('menu_take_screenshot'))
        glutAddMenuEntry("Toggle Mesh Visibility", self._main_handler.get_menu_id('menu_visibility'))
        glutAttachMenu(GLUT_RIGHT_BUTTON)
        
        glutTimerFunc(1, self.update, 1)
        glutDisplayFunc(self.render)
    
    def _init_scene(self):
        self._current_scene = RaytraceScene(self)
        if self._current_scene:
            self._current_scene.init()
            self._main_handler._selected_node = self._current_scene.mesh
    
    def run(self):
        self._log.info(u"Running...")
        OpenGL.ERROR_CHECKING = False
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
                glutPostRedisplay()
                
        glutTimerFunc(int(1000/self._config.getint('general', 'framerate')) - (glutGet(GLUT_ELAPSED_TIME) - time), self.update, 1)
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        
        if self._current_scene:
            self._current_scene.render()
        
        glutSwapBuffers()

if __name__ == '__main__':
    app = Application()
    app.run()
