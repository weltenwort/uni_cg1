# -*- coding: utf-8 -*-
"""
This is the scene definition for exercise 1.

The comments in this file are written in the reStructured text format and adhere
to the commenting style used by epydoc.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from scenegraph import Scene, CuboidNode

class RobotScene(Scene):
    def __init__(self, application):
        Scene.__init__(self, application, name="cg1_ex1", draw_origin=False)
    
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
