# -*- coding: utf-8 -*-
"""
This file contains the keyboard event handler.

The comments in this file are written in the reStructured text format and adhere
to the commenting style used by epydoc.
"""

import logging
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class DefaultHandler(object):    
    def __init__(self, application):
        self._application = application
        self._log = logging.getLogger('KeyHandler')
        
        self.handles_types = {
            'keyboard'      : self.handle_keyboard, 
            'reshape'       : self.handle_reshape, 
            'mouse_button'  : self.handle_mouse_button, 
            'mouse_motion'  : self.handle_mouse_motion, 
            'menu'          : self.handle_menu, 
            }
        
        self._keymapping = {
            chr(27) : self._handle_escape, 
            }
        
        self._mouse_position        = [0, 0]
        self._mouse_button_left     = False
        self._mouse_button_right    = False
        
        self._keyboard_alt          = False
        self._keyboard_ctrl         = False
        self._keyboard_shift        = False
        
        self._menu_entries          = {}
        
        self._selected_node         = None
    
    def handle_keyboard(self, key, mouse_x, mouse_y):
        self._log.debug(u"Handling key '%s' (%u)", key, ord(key))
        try:
            return self._keymapping[key](key, mouse_x, mouse_y)
        except KeyError:
            self._log.debug(u"No handler for key '%s' found.", key)
            return False
    
    def _handle_escape(self, key, mouse_x, mouse_y):
        self._application.stop()
        return True
    
    def handle_reshape(self, width, height):
        self._application._current_scene._init_projection()
        return True
    
    def handle_mouse_button(self, button, state, x, y):
        self._mouse_position = [x, y]
        if button == GLUT_LEFT_BUTTON:
            self._mouse_button_left = state == GLUT_DOWN
        if button == GLUT_RIGHT_BUTTON:
            self._mouse_button_right = state == GLUT_DOWN
        
        modifiers = glutGetModifiers()
        self._keyboard_ctrl = modifiers & GLUT_ACTIVE_CTRL
        self._keyboard_alt = modifiers & GLUT_ACTIVE_ALT
        self._keyboard_shift = modifiers & GLUT_ACTIVE_SHIFT
            
        return True
    
    def handle_mouse_motion(self, x, y):
        dx = x - self._mouse_position[0]
        dy = y - self._mouse_position[1]
        if self._mouse_button_left:
            if self._keyboard_ctrl:
                self._selected_node.rotation[0] += dx
            elif self._keyboard_shift:
                self._selected_node.rotation[2] += dx
            else:
                self._selected_node.rotation[1] += dx
        self._mouse_position = [x, y]
        return True
    
    def handle_menu(self, menu_id):
        menu_entry, args, kwargs = self._menu_entries.get(menu_id, (False, None, None))
        self._log.debug(u"Handling menu entry '%s'...", menu_entry)
        if menu_entry == 'menu_quit':
            self._application.stop()
        if menu_entry and menu_entry.startswith('menu_scene_select') and len(args) == 1:
            self._selected_node = args[0]
    
    def get_menu_id(self, menu_entry, args=[], kwargs={}):
        menu_id = hash(menu_entry) + hash(self)
        #self._log.debug(u"Menu id for '%s' is %u", menu_entry, menu_id)
        self._menu_entries[menu_id] = (menu_entry, args, kwargs)
        return menu_id
