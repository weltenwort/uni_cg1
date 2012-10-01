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

import OpenGL
OpenGL.ERROR_CHECKING = False # to avoid a segfault with mesa >= 7.0.3
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from eventdispatcher import EventDispatcher
from handler import DefaultHandler
from scene_ex1 import RobotScene

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
    
    def _init_windows(self):
        self._log.info(u"Initializing windows...")
        glutInit([])
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self._config.getint('window', 'width'), self._config.getint('window', 'height'))
        glutInitWindowPosition(self._config.getint('window', 'x'), self._config.getint('window', 'y'))
        self._window = glutCreateWindow(self._config.get('window', 'title'))
    
    def _init_callbacks(self):
        self._log.info(u"Initializing callbacks...")
        self._dispatcher = EventDispatcher()
        self._defaultHandler = DefaultHandler(self)
        
        self._dispatcher.push_handlers(self._defaultHandler)
        glutKeyboardFunc(self._dispatcher.handle_type('keyboard'))
        glutReshapeFunc(self._dispatcher.handle_type('reshape'))
        glutMouseFunc(self._dispatcher.handle_type('mouse_button'))
        glutMotionFunc(self._dispatcher.handle_type('mouse_motion'))
        
        self._menu_main = glutCreateMenu(self._dispatcher.handle_type('menu'))
        glutAddMenuEntry("Quit", self._defaultHandler.get_menu_id('menu_quit'))
        glutAttachMenu(GLUT_RIGHT_BUTTON)
        self._menu_scene = glutCreateMenu(self._dispatcher.handle_type('menu'))
        glutSetMenu(self._menu_main)
        glutAddSubMenu("Scene", self._menu_scene)
        
        glutTimerFunc(1, self.update, 1)
        glutDisplayFunc(self.render)
    
    def _init_scene(self):
        self._current_scene = RobotScene(self)
        if self._current_scene:
            self._current_scene.init()
            self._defaultHandler._selected_node = self._current_scene
            glutSetMenu(self._menu_scene)
            def _add_node_menu_entry(node, prefix):
                glutAddMenuEntry(prefix + node.name + "", self._defaultHandler.get_menu_id('menu_scene_select_%u' % hash(node), [node, ]))
                return ([prefix + node.name + " / "], {})
            self._current_scene.map(_add_node_menu_entry, [""], {}, True)
    
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
                glutPostRedisplay()
                
        glutTimerFunc(int(1000/self._config.getint('general', 'framerate')) - (glutGet(GLUT_ELAPSED_TIME) - time), self.update, 1)
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        
        if self._current_scene:
            self._current_scene.render()
        
        glutSwapBuffers()

if __name__ == '__main__':
    app = Application()
    app.run()
