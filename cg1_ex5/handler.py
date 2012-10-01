# -*- coding: utf-8 -*-
"""
This file contains the keyboard event handler.

The comments in this file are written in the reStructured text format and adhere
to the commenting style used by epydoc.
"""

import logging
import sys

from numpy import array
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import Image

from writer import capture_screen

class BaseHandler(object):
    def __init__(self, application, scene):
        self._application   = application
        self._scene         = scene
        self._log = logging.getLogger(self.__class__.__name__)
        
        self.handles_types  = {}
        
        self._selected_node = scene

class BaseKeyboardHandler(object):
    def __init__(self):
        self.handles_types.update({
            'keyboard'      : self.handle_keyboard, 
            })
        
        self._keymapping = {
            chr(27) : self._handle_escape, 
            }
    
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

class BaseMouseHandler(object):
    def __init__(self):
        self.handles_types.update({
            'mouse_button'  : self.handle_mouse_button, 
            'mouse_motion'  : self.handle_mouse_motion, 
            })
        
        self._mouse_position        = [0, 0]
        self._mouse_button_left     = False
        self._mouse_button_right    = False
        
        self._keyboard_alt          = False
        self._keyboard_ctrl         = False
        self._keyboard_shift        = False

class BaseMenuHandler(object):
    def __init__(self):
        self.handles_types.update({
            'menu'          : self.handle_menu, 
            })
            
        self._menu_entries          = {}
    
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

class BaseReshapeHandler(object):
    def __init__(self):
        self.handles_types.update({
            'reshape'       : self.handle_reshape, 
            })
    def handle_reshape(self, width, height):
        self._scene._init_projection()
        return True

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
            'r'     : self._handle_raytrace, 
            's'     : self._handle_screenshot, 
            'v'     : self._handle_toggle_mesh_visibility, 
            'a'     : self._handle_area_raytrace, 
            }
        
        self._mouse_position        = [0, 0]
        self._mouse_button_left     = False
        self._mouse_button_right    = False
        
        self._keyboard_alt          = False
        self._keyboard_ctrl         = False
        self._keyboard_shift        = False
        
        self._menu_entries          = {}
        
        self._selected_node         = None
        self._area_selection_mode   = 0
    
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
        if self._area_selection_mode == 0:
            if button == GLUT_LEFT_BUTTON:
                self._mouse_button_left = state == GLUT_DOWN
            if button == GLUT_RIGHT_BUTTON:
                self._mouse_button_right = state == GLUT_DOWN
            
            modifiers = glutGetModifiers()
            self._keyboard_ctrl = modifiers & GLUT_ACTIVE_CTRL
            self._keyboard_alt = modifiers & GLUT_ACTIVE_ALT
            self._keyboard_shift = modifiers & GLUT_ACTIVE_SHIFT
        elif self._area_selection_mode == 1 and state == GLUT_DOWN:
            self._point1 = self._mouse_position
            self._area_selection_mode = 2
            self._log.info(u"top left point is now %s" % self._point1)
        elif self._area_selection_mode == 2 and state == GLUT_DOWN:
            self._point2 = self._mouse_position
            self._area_selection_mode = 0
            self._log.info(u"bottom right point is now %s" % self._point2)
            self._application._current_scene.raytrace(area=(self._point1, self._point2))
            
        return True
    
    def handle_mouse_motion(self, x, y):
        dx = x - self._mouse_position[0]
        dy = y - self._mouse_position[1]
        if self._mouse_button_left:
            if self._keyboard_ctrl:
                self._application._current_scene.rotation[1] += dx
                self._application._current_scene.rotation[2] -= dy
            else:
                self._selected_node.rotation[1] += dx
                self._selected_node.rotation[2] -= dy
        #world_point = gluUnProject(float(x), float(y), 0.0)
        #self._log.debug(u"mouse point: %s" % str(world_point))
        #self._application._current_scene.pointer.position = array([world_point[0], -world_point[1], world_point[2]])
        self._mouse_position = [x, y]
        return True
    
    def handle_menu(self, menu_id):
        menu_entry, args, kwargs = self._menu_entries.get(menu_id, (False, None, None))
        self._log.debug(u"Handling menu entry '%s'...", menu_entry)
        if menu_entry == 'menu_quit':
            self._application.stop()
        if menu_entry == 'menu_raytrace':
            self._handle_raytrace()
        if menu_entry == 'menu_take_screenshot':
            self._handle_screenshot()
        if menu_entry == 'menu_visibility':
            self._handle_toggle_mesh_visibility()
        if menu_entry and menu_entry.startswith('menu_scene_select') and len(args) == 1:
            self._selected_node = args[0]
    
    def _handle_area_raytrace(self, *args, **kwargs):
        self._area_selection_mode = 1
        self._log.info(u"Select raytrace area via clicking (top left, then bottom right)...")
    
    def _handle_raytrace(self, *args, **kwargs):
        self._application._current_scene.raytrace()
    
    def _handle_screenshot(self, *args, **kwargs):
        image, filename = capture_screen()
        self._log.info(u"Saved screenshot as '%s'." % filename)
    
    def _handle_toggle_mesh_visibility(self, *args, **kwargs):
        self._application._current_scene.mesh.visible = not self._application._current_scene.mesh.visible
    
    def get_menu_id(self, menu_entry, args=[], kwargs={}):
        menu_id = hash(menu_entry) + hash(self)
        #self._log.debug(u"Menu id for '%s' is %u", menu_entry, menu_id)
        self._menu_entries[menu_id] = (menu_entry, args, kwargs)
        return menu_id

class TextureEditHandler(BaseHandler, 
                         BaseKeyboardHandler, 
                         BaseMouseHandler, 
                         BaseMenuHandler):
    def __init__(self, application, scene):
        BaseHandler.__init__(self, application, scene)
        BaseKeyboardHandler.__init__(self)
        BaseMouseHandler.__init__(self)
        BaseMenuHandler.__init__(self)
    
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
            self._application._current_texture.putpixel((x, y),  (1, 0, 0))
            self._application._current_scene.children[0].tex.refresh()
            self._application._current_scene.children[1].tex.refresh()
        self._application._current_scene.children[1].cursor.rotation = array([float(x-256)/512.0*(-180.0),
                                                                              float(y-256)/512.0*(-180.0),
                                                                              0.0])
        self._mouse_position = [x, y]
        return True
    
    def handle_menu(self, menu_id):
        menu_entry, args, kwargs = self._menu_entries.get(menu_id, (False, None, None))
        self._log.debug(u"Handling menu entry '%s'...", menu_entry)
        if menu_entry == 'menu_quit':
            self._application.stop()
        if menu_entry == 'menu_clear':
            width = self._application._current_texture.size[0]
            height = self._application._current_texture.size[1]
            self._application._current_texture.paste("#ffffff", (0, 0, width, height))
            self._application._current_scene.children[0].tex.refresh()
            self._application._current_scene.children[1].tex.refresh()
        
class TexturedObjectHandler(BaseHandler, 
                         BaseKeyboardHandler, 
                         BaseMouseHandler, 
                         BaseMenuHandler):
    def __init__(self, application, scene):
        BaseHandler.__init__(self, application, scene)
        BaseKeyboardHandler.__init__(self)
        BaseMouseHandler.__init__(self)
        BaseMenuHandler.__init__(self)
    
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
                self._selected_node.rotation[2] -= dy
        self._mouse_position = [x, y]
        return True
