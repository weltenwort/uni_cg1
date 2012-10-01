# -*- coding: utf-8 -*-
"""
This are the classes making up the scene graph.

The comments in this file are written in the reStructured text format and adhere
to the commenting style used by epydoc.
"""

import logging

from numpy import array
from numpy.random import rand
from OpenGL.GL import *
from OpenGL.GLUT import *
#from psyco.classes import psyobj

class SceneObject(object):
    def __init__(self, name="Object", position=[0, 0, 0], rotation=[0, 0, 0], offset=[0, 0, 0], scaling=[1, 1, 1], size=[1, 1, 1], color=[1, 1, 1, 1], texture=None, draw_origin=False):
        self.name           = name
        self.position       = array(position)
        self.rotation       = array(rotation)
        self.offset         = array(offset)
        self.scaling        = array(scaling)
        self.size           = array(size)
        self.color          = array(color)
        self.texture        = texture
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
        #logging.debug(u"rendering %s in window %d" % (self.__class__.__name__, glutGetWindow()))
        glPushMatrix()
        
        self.transform()
        
        if self.draw_origin:
            glPushAttrib(GL_ENABLE_BIT)
            glDisable(GL_LIGHTING)
            glPushMatrix()
            glTranslate(*self.offset)
            #glScale(*self.size)
            glColor4f(1, 1, 1, 0.2)
            glutWireSphere(0.075, 16, 16)
            glCallList(self._dlist_origin)
            glPopMatrix()
            glPopAttrib()
    
        # apply the local size
        glPushMatrix()
        glScale(*self.size)
        #if self.texture:
        #    self.texture()
        self.draw()
        glPopMatrix()
        
        glTranslate(*self.offset)
        
        for child in self.children:
            child.render()
        
        glPopMatrix()
    
    def update(self, d_time):
        for child in self.children:
            child.update(d_time)
    
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
        self._log = logging.getLogger(self.__class__.__name__)
    
    def _init_projection(self):
        pass
    
    def init(self):
        self._init_projection()
    
    def update(self, d_time):
        SceneObject.update(self, d_time)
        glutPostRedisplay()
    
class WindowedScene(Scene):
    def __init__(self, window, application, *args, **kwargs):
        Scene.__init__(self, application, *args, **kwargs)
        self.window = window
    
    def _init_projection(self):
        glutSetWindow(self.window)
        Scene._init_projection(self)
    
    def init(self):
        glutSetWindow(self.window)
        Scene.init(self)
    
    def update(self, d_time):
        glutSetWindow(self.window)
        SceneObject.update(self, d_time)
        glutPostWindowRedisplay(self.window)

class SubWindowedScene(Scene):
    def _init_projection(self):
        glutSetWindow(self.application._window)
        Scene._init_projection(self)
        for subwindow in self.children:
            subwindow._init_projection()
        glutSetWindow(self.application._window)
        
    def init(self):
        glutSetWindow(self.application._window)
        Scene.init(self)
        for subwindow in self.children:
            subwindow.init()
        glutSetWindow(self.application._window)
    
    def update(self, d_time):
        glutSetWindow(self.application._window)
        SceneObject.update(self, d_time)
        glutPostWindowRedisplay(self.application._window)
    
    def render(self):
        pass
        #glutSetWindow(self.application._window)
        #glutSwapBuffers()

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
        
class QuadNode(Node):
    def __init__(self, vertices,  *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.vertices = vertices
        self.texture_coords = [(1.0, 1.0), 
                               (1.0, 0.0),
                               (0.0, 0.0), 
                               (0.0, 1.0)]
        self.update_display_list()
    
    def update_display_list(self):
        logging.debug(u"Updating display lists in window %d" % glutGetWindow())
        
        # prepare display list
        self._dlist_geom = glGenLists(1)
        glNewList(self._dlist_geom, GL_COMPILE)
        glPushAttrib(GL_CURRENT_BIT)
        
        if self.texture:
            self.texture()
        glBegin(GL_QUADS)
        for vertex_index, vertex in enumerate(self.vertices):
            #print(u"using normal %s" % normal_map[tuple(vertex)])
            #print(u"using texture coords %s" % str(texture_map[tuple(vertex)]))
            #glColor3fv(tuple(rand(1, 3)[0]))
            #glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, tuple(rand(1, 3)[0]+(1.0, )))
            glTexCoord2fv(self.texture_coords[vertex_index])
            #glNormal3fv(tuple(normal_map[tuple(vertex)]))
            glVertex3fv(tuple(vertex))
        glEnd()
        #glBegin(GL_LINES)
        #for geom_object in self.node_objects:
        #    for vertex in geom_object.vertices:
        #        glVertex3fv(tuple(vertex))
        #        glVertex3fv(tuple(vertex + normal_map[(tuple(vertex))]))
        #glEnd()
        
        glPopAttrib()
        glEndList()

    def draw(self):
        Node.draw(self)
        glCallList(self._dlist_geom)

class TriangleMeshNode(Node):
    def __init__(self, triangles, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.node_objects = triangles
        self.update_display_list()
    
    def update_display_list(self):
        logging.debug(u"Updating display lists in window %d" % glutGetWindow())
        try:
            normal_map = self.node_objects.get_vertex_normal_map()
            texture_map = self.node_objects.get_vertex_sphere_map()
        except AttributeError:
            normal_map = {}
            texture_map = {}
        
        # prepare display list
        self._dlist_geom = glGenLists(1)
        glNewList(self._dlist_geom, GL_COMPILE)
        glPushAttrib(GL_CURRENT_BIT)
        
        if self.texture:
            self.texture()
        glBegin(GL_TRIANGLES)
        for geom_object in self.node_objects:
            for vertex in geom_object.vertices:
                #print(u"using normal %s" % normal_map[tuple(vertex)])
                #print(u"using texture coords %s" % str(texture_map[tuple(vertex)]))
                #glColor3fv(tuple(rand(1, 3)[0]))
                #glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, tuple(rand(1, 3)[0]+(1.0, )))
                glTexCoord2fv(texture_map[tuple(vertex)])
                glNormal3fv(tuple(normal_map[tuple(vertex)]))
                glVertex3fv(tuple(vertex))
        glEnd()
        #glBegin(GL_LINES)
        #for geom_object in self.node_objects:
        #    for vertex in geom_object.vertices:
        #        glVertex3fv(tuple(vertex))
        #        glVertex3fv(tuple(vertex + normal_map[(tuple(vertex))]))
        #glEnd()
        
        glPopAttrib()
        glEndList()
    
    def draw(self):
        Node.draw(self)
        glCallList(self._dlist_geom)

class CursorNode(Node):
    def __init__(self, target=[10, 0, 0],  *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.target = array(target)
        
    def draw(self):
        Node.draw(self)
        glPushAttrib(GL_CURRENT_BIT)
        glBegin(GL_LINES)
        glMaterial(GL_FRONT, GL_DIFFUSE, (0.0, 0.0, 1.0, 1.0))
        glVertex3fv((0.0, 0.0, 0.0))
        glVertex3fv(tuple(self.target))
        glEnd()
        glPopAttrib()
