# -*- coding: utf-8 -*-
"""
This are the classes making up the scene graph.

The comments in this file are written in the reStructured text format and adhere
to the commenting style used by epydoc.
"""

from numpy import array
from OpenGL.GL import *
from OpenGL.GLUT import *

class SceneObject(object):
    def __init__(self, name="Object", position=[0, 0, 0], rotation=[0, 0, 0], offset=[0, 0, 0], scaling=[1, 1, 1], size=[1, 1, 1], color=[1, 1, 1, 1], draw_origin=False):
        self.name           = name
        self.position       = array(position)
        self.rotation       = array(rotation)
        self.offset         = array(offset)
        self.scaling        = array(scaling)
        self.size           = array(size)
        self.color          = array(color)
        self.draw_origin    = draw_origin
        self.children       = []
        
        self._dlist_origin = glGenLists(1)
        glNewList(self._dlist_origin, GL_COMPILE)
        glPushAttrib(GL_CURRENT_BIT)
        glBegin(GL_LINES)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0.25, 0, 0)
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0.25, 0)
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 0.25)
        glEnd()
        glPopAttrib()
        glEndList()
    
    def transform(self):
        glTranslate(*self.position)
        glScale(*self.scaling)
        # rotate around each axis
        #glTranslate(*self.offset)
        glRotate(self.rotation[0], 1, 0, 0)
        glRotate(self.rotation[1], 0, 1, 0)
        glRotate(self.rotation[2], 0, 0, 1)
        glTranslate(*-self.offset)
    
    def draw(self):
        glColor4f(*self.color)
        
    def render(self):
        glPushMatrix()
        
        self.transform()
        
        if self.draw_origin:
            glDisable(GL_LIGHTING)
            glPushMatrix()
            glTranslate(*self.offset)
            #glScale(*self.size)
            glColor4f(1, 1, 1, 0.2)
            glutWireSphere(0.075, 16, 16)
            glCallList(self._dlist_origin)
            glPopMatrix()
            glEnable(GL_LIGHTING)
    
        # apply the local size
        glPushMatrix()
        glScale(*self.size)
        self.draw()
        glPopMatrix()
        
        glTranslate(*self.offset)
        
        for child in self.children:
            child.render()
        
        glPopMatrix()
    
    def update(self, d_time):
        pass
    
    def map(self, func, args=[], kwargs={}, recursive=False):
        """Calls func with this node and the given args and kwargs as arguments. 
        If recursive is set, the function will also be called for the children.
        
        :Parameters:
          func
            a callable
        
        :Keywords:
          args : sequence
            a sequence of positional arguments to be passed to func
          kwargs : mapping
            a mapping of keyword arguments to be passed to func
          recursive : boolean
            whether or not to recursively descent into children
        """
        new_args, new_kwargs = func(self, *args, **kwargs)
        if recursive:
            for child in self.children:
                child.map(func, new_args, new_kwargs, recursive)
        return (args, kwargs)

class Scene(SceneObject):
    def __init__(self, application, *args, **kwargs):
        SceneObject.__init__(self, *args, **kwargs)
        self.application = application
    
    def _init_projection(self):
        pass
    
    def init(self):
        self._init_projection()

class Node(SceneObject):
    def __init__(self, scene, *args, **kwargs):
        SceneObject.__init__(self, *args, **kwargs)
        self.scene = scene

class CuboidNode(Node):
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
    
    #def transform(self):
    #    Node.transform(self)
    #    glScale(*self.size)
    
    def draw(self):
        Node.draw(self)
        glutSolidCube(1.0)
