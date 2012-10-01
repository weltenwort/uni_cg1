# -*- coding: utf-8 -*-
"""
This is the scene definition for exercise 1.

The comments in this file are written in the reStructured text format and adhere
to the commenting style used by epydoc.
"""

import sys

import Image
from numpy import array, dot
from numpy.linalg import inv
from numpy.random import rand
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from scenegraph import Scene, WindowedScene, SubWindowedScene, CuboidNode, TriangleMeshNode,  QuadNode, CursorNode
from reader import openOff
from texture import Texture

class RobotScene(Scene):
    def __init__(self, application):
        Scene.__init__(self, application, name="cg1_ex3", draw_origin=False)
    
    def _init_projection(self):
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        
        # light and material
        self.mat_ambient    = [0.5, 0.5, 0.5, 1.0]
        self.mat_specular   = [0.6, 0.6, 0.6, 1.0]
        self.mat_shininess  = [3.0]
        self.model_ambient  = [0.3, 0.3, 0.3]
        self.light_position = [5.0, 5.0, 5.0, 0.0]
        glMaterialfv(GL_FRONT, GL_AMBIENT, self.mat_ambient)
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.mat_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, self.mat_shininess)
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self.model_ambient)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        # shading
        glShadeModel(GL_FLAT)
        
        glViewport(0, 0, window_width, window_height)
        
        # clear background to black and clear depth buffer
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
 
        # enable depth test (z-buffer)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)

        # enable normalization of vertex normals
        glEnable(GL_NORMALIZE)
        
        # enable line antialiasing
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(1.5)

        # initial view definitions
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # perspective projection
        gluPerspective(40.0, float(window_width) / float(window_height), 1.0, 10.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    def init(self):
        Scene.init(self)
        
        # add child nodes
        torso = CuboidNode(scene=self, 
                          name="torso", 
                          size=[0.3, 0.5, 0.3], 
                          position=[0, 0, 0], 
                          rotation=[0, 0, 0], 
                          offset=[0, 0, 0], 
                          color=[1, 1, 1, 0.1], 
                          draw_origin=True)
        head = CuboidNode(scene=self, 
                          name="head", 
                          size=[0.15, 0.15, 0.15], 
                          position=[0, 0.25, 0], 
                          rotation=[0, 0, 0], 
                          offset=[0, -0.075, 0], 
                          color=[1, 1, 1, 0.1], 
                          draw_origin=True)
        leg = CuboidNode(scene=self, 
                         name="leg", 
                         size=[0.1, 0.4, 0.1], 
                         position=[0, -0.25, 0], 
                         rotation=[0, 0, 0], 
                         offset=[0, 0.2, 0], 
                          color=[1, 1, 1, 0.1], 
                         draw_origin=True)
        foot = CuboidNode(scene=self, 
                          name="foot", 
                          size=[0.2, 0.05, 0.2], 
                          position=[0, -0.4, 0], 
                          rotation=[0, 0, 0], 
                          offset=[0, 0.025, 0], 
                          color=[1, 1, 1, 0.1], 
                          draw_origin=True)
        larm = CuboidNode(scene=self, 
                          name="left arm", 
                          size=[0.1, 0.4, 0.1], 
                          position=[-0.15, 0.25, 0], 
                          rotation=[-30, 0, 0], 
                          offset=[0.05, 0.2, 0], 
                          color=[1, 1, 1, 0.1], 
                          draw_origin=True)
        rarm = CuboidNode(scene=self, 
                          name="right arm", 
                          size=[0.1, 0.4, 0.1], 
                          position=[0.15, 0.25, 0], 
                          rotation=[15, 0, 0], 
                          offset=[-0.05, 0.2, 0], 
                          color=[1, 1, 1, 0.1], 
                          draw_origin=True)
        lhand = CuboidNode(scene=self, 
                          name="left hand", 
                          size=[0.05, 0.15, 0.05], 
                          position=[-0.05, -0.4, 0], 
                          rotation=[-15, 0, 0], 
                          offset=[0, 0.075, 0], 
                          color=[1, 1, 1, 0.1], 
                          draw_origin=True)
        rhand = CuboidNode(scene=self, 
                          name="right hand", 
                          size=[0.05, 0.15, 0.05], 
                          position=[0.05, -0.4, 0], 
                          rotation=[0, 0, 0], 
                          offset=[0, 0.075, 0], 
                          color=[1, 1, 1, 0.1], 
                          draw_origin=True)
        self.children.append(torso)
        torso.children.append(head)
        torso.children.append(leg)
        leg.children.append(foot)
        torso.children.append(larm)
        torso.children.append(rarm)
        larm.children.append(lhand)
        rarm.children.append(rhand)
        
class MeshScene(Scene):
    def __init__(self, application):
        Scene.__init__(self, application, name="cg1_ex3", draw_origin=False)
        self.eye = array([0.0, 0.0, 0.0, 1.0])
    
    def _init_projection(self):
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        
        # light and material
        self.mat_ambient    = [0.5, 0.5, 0.5, 1.0]
        self.mat_specular   = [0.6, 0.6, 0.6, 1.0]
        self.mat_shininess  = [3.0]
        self.model_ambient  = [0.5, 0.5, 0.5]
        self.light_position = [5.0, 5.0, 5.0, 0.0]
        self.light_ambient  = [0.5, 0.5, 0.5, 1.0]
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, self.mat_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.mat_specular)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, self.mat_shininess)
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.light_ambient)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self.model_ambient)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        # shading
        glShadeModel(GL_SMOOTH)
        glPolygonMode(GL_FRONT, GL_FILL)
        glPolygonMode(GL_BACK, GL_LINE)
        
        glViewport(0, 0, window_width, window_height)
        
        # clear background to black and clear depth buffer
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
 
        # disable depth test (z-buffer)
        glDisable(GL_DEPTH_TEST)

        # enable normalization of vertex normals
        glEnable(GL_NORMALIZE)
        
        # enable line antialiasing
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(1.5)

        # initial view definitions
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # perspective projection
        gluPerspective(40.0, float(window_width) / float(window_height), 0.0, 200.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    def init(self):
        Scene.init(self)
        
        # get triangle bsp tree
        triangles = openOff("./meshes/teapot.off").get_triangles()
        self._log.debug(u"Constructing bsp tree...")
        bsptree = TriangleBspTree(triangles,
                                  scene=self, 
                                  #scaling=[0.5, 0.5, 0.5],
                                  position=[0.0, 0.0, 0.0],
                                  draw_origin=False)
        self._log.debug(u"Partitioning using autopartition...")
        bsptree.autopartition()
        #bsptree.testpartition()
        self.children.append(bsptree)
        
    def draw(self):
        modelview = array(glGetDoublev(GL_MODELVIEW_MATRIX)).transpose()
        inv_modelview = inv(modelview)
        self.eye = dot(inv_modelview, array([0.0, 0.0, 0.0, 1.0]))
        #self.eye /= self.eye[3]
        #print modelview
        #print self.eye
        Scene.draw(self)

class InteractivelyTexturedScene(SubWindowedScene):
    def __init__(self, application):
        Scene.__init__(self, application, name="cg1_ex4", draw_origin=False)
    
    def _init_projection(self):
        SubWindowedScene._init_projection(self)
        
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        self._log.debug(u"Setting up projection in window %d (%d, %d)..." % (glutGetWindow(), window_width, window_height))
        
        # light and material
        self.mat_ambient    = [0.5, 0.5, 0.5, 1.0]
        self.mat_specular   = [0.6, 0.6, 0.6, 1.0]
        self.mat_shininess  = [3.0]
        self.model_ambient  = [0.5, 0.5, 0.5]
        self.light_position = [5.0, 5.0, 5.0, 0.0]
        self.light_ambient  = [0.5, 0.5, 0.5, 1.0]
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, self.mat_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.mat_specular)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, self.mat_shininess)
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.light_ambient)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self.model_ambient)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glEnable(GL_TEXTURE_2D)

        # shading
        glShadeModel(GL_SMOOTH)
        #glPolygonMode(GL_FRONT, GL_FILL)
        #glPolygonMode(GL_BACK, GL_LINE)
        
        glViewport(0, 0, window_width, window_height)
        
        # clear background to black and clear depth buffer
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
 
        # disable depth test (z-buffer)
        glEnable(GL_DEPTH_TEST)

        # enable normalization of vertex normals
        glEnable(GL_NORMALIZE)
        
        # enable line antialiasing
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(1.5)
    
    def init(self):
        self.children.append(TextureEditScene(self.application._subwindows[0], self.application))
        self.children.append(TexturedObjectScene(self.application._subwindows[1], self.application))
        SubWindowedScene.init(self)
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        SubWindowedScene.render(self)
        #self._log.debug(u"rendering main in window %d" % glutGetWindow())
        glutSwapBuffers()

class TexturedObjectScene(WindowedScene):
    def __init__(self, window, application):
        WindowedScene.__init__(self, window, application, name="cg1_ex4_textured_object", draw_origin=False)
    
    def _init_projection(self):
        WindowedScene._init_projection(self)
        
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        self._log.debug(u"Setting up projection in window %d (%d, %d)..." % (glutGetWindow(), window_width, window_height))
        
        # light and material
        self.mat_ambient    = [0.5, 0.5, 0.5, 1.0]
        self.mat_specular   = [0.6, 0.6, 0.6, 1.0]
        self.mat_shininess  = [3.0]
        self.model_ambient  = [0.5, 0.5, 0.5]
        self.light_position = [5.0, 5.0, 5.0, 0.0]
        self.light_ambient  = [0.5, 0.5, 0.5, 1.0]
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, self.mat_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.mat_specular)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, self.mat_shininess)
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.light_ambient)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self.model_ambient)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glEnable(GL_TEXTURE_2D)

        # shading
        glShadeModel(GL_SMOOTH)
        #glPolygonMode(GL_FRONT, GL_FILL)
        #glPolygonMode(GL_BACK, GL_LINE)
        
        glViewport(0, 0, window_width, window_height)
        
        # clear background to black and clear depth buffer
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
 
        # enable depth test (z-buffer)
        glEnable(GL_DEPTH_TEST)

        # enable normalization of vertex normals
        glEnable(GL_NORMALIZE)
        
        # enable line antialiasing
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(1.5)
        
        # initial view definitions
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, float(window_width) / float(window_height), 1.0, 250.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, 15.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        
    def init(self):
        WindowedScene.init(self)
        glutSetWindow(self.window)
        
        self.tex = Texture(image = self.application._current_texture)
        # get triangle mesh
        self._log.debug(u"Loading mesh...")
        triangles = openOff("./data/cow.off").get_triangles()
        mesh = TriangleMeshNode(triangles   = triangles,
                                scene       = self, 
                                #scaling=[0.5, 0.5, 0.5],
                                position    = [0.0, 0.0, 0.0],
                                texture     = self.tex, 
                                draw_origin = False)
        self.cursor = CursorNode(scene      = self, 
                                 draw_origin= False)
        self.children.append(mesh)
        mesh.children.append(self.cursor)
    
    def render(self):
        #glutSetWindow(self.window)
        #glClearColor(*(tuple(rand(1, 3)[0]) + (1.0, )))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, 15.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0);
        
        WindowedScene.render(self)
        #self._log.debug(u"rendering obj in window %d" % glutGetWindow())
        glutSwapBuffers()

class TextureEditScene(WindowedScene):
    def __init__(self, window, application):
        WindowedScene.__init__(self, window, application, name="cg1_ex4_texture_edit", draw_origin=False)
    
    def _init_projection(self):
        WindowedScene._init_projection(self)
        
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        self._log.debug(u"Setting up projection in window %d (%d, %d)..." % (glutGetWindow(), window_width, window_height))
        
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glEnable(GL_TEXTURE_2D)
        
        glViewport(0, 0, window_width, window_height)
        
        # clear background to black and clear depth buffer
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
 
        # enable depth test (z-buffer)
        glEnable(GL_DEPTH_TEST)

        # enable normalization of vertex normals
        glEnable(GL_NORMALIZE)
        
        # initial view definitions
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #gluPerspective(60.0, float(window_width) / float(window_height), 1.0, 250.0)
        gluOrtho2D(0, window_width, window_height, 0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        #gluLookAt(0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        
    def init(self):
        WindowedScene.init(self)
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        
        self.tex = Texture(image = self.application._current_texture)
        texture_width, texture_height = self.application._current_texture.size
        quad = QuadNode(vertices   = [(texture_width,  0.0,  0.0),
                                      (texture_width,  texture_height,  0.0),
                                      (0.0,  texture_height,  0.0), 
                                      (0.0, 0.0, 0.0),  
                                       ], 
                        scene       = self, 
                        #scaling=[0.5, 0.5, 0.5],
                        position    = [0.0, 0.0, 0.0],
                        texture     = self.tex, 
                        draw_origin = False)
        self.children.append(quad)
    
    def render(self):
        #glutSetWindow(self.window)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        #gluLookAt(0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0);
        
        WindowedScene.render(self)
        #self._log.debug(u"rendering tex in window %d" % glutGetWindow())
        glutSwapBuffers()
