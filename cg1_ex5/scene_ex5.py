# -*- coding: utf-8 -*-
"""
This is the scene definition for exercise 5.

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

import sys

import Image
from numpy import array, dot, inner, sum
from numpy.linalg import inv, norm
from numpy.random import rand
from OpenGL.arrays import numpymodule
numpymodule.NumpyHandler.ERROR_ON_COPY = True
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from scenegraph import Scene, CuboidNode, TriangleMeshNode, PointerNode, PointCloudNode, ColoredPointCloudNode
from reader import openOff
from console import ProgressBar

class RaytraceScene(Scene):
    def __init__(self, application):
        Scene.__init__(self, application, name="cg1_ex5", draw_origin=False)
        #self.eye = array([0.0, 0.0, 0.0, 1.0])
        self.max_recursion = 2
    
    def _init_projection(self):
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        
        # light and material
        self.mat_ambient        = [0.5, 0.5, 0.5, 1.0]
        self.mat_diffuse        = [1.0, 1.0, 1.0, 1.0]
        self.mat_specular       = [0.1, 0.1, 0.1, 1.0]
        self.mat_shininess      = [3.0]
        self.model_ambient      = [0.5, 0.5, 0.5]
        self.light_position_0   = [50.0, 50.0, 0.0, 1.0]
        self.light_position_1   = [-50.0, -50.0, 0.0, 1.0]
        self.light_ambient_0    = [0.5, 0.0, 0.0, 1.0]
        self.light_ambient_1    = [0.0, 0.5, 0.0, 1.0]
        self.light_diffuse_0    = [0.5, 0.0, 0.0, 1.0]
        self.light_diffuse_1    = [0.0, 0.5, 0.0, 1.0]
        self.light_specular_0    = [0.5, 0.0, 0.0, 1.0]
        self.light_specular_1    = [0.0, 0.5, 0.0, 1.0]
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.mat_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.mat_diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.mat_specular)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, self.mat_shininess)
        glEnable(GL_COLOR_MATERIAL)
        
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position_0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.light_ambient_0)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.light_diffuse_0)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.light_specular_0)
        
        glLightfv(GL_LIGHT1, GL_POSITION, self.light_position_1)
        glLightfv(GL_LIGHT1, GL_AMBIENT, self.light_ambient_1)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, self.light_diffuse_1)
        glLightfv(GL_LIGHT1, GL_SPECULAR, self.light_specular_1)
        
        #glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self.model_ambient)
        glEnable(GL_LIGHTING)
        #glDisable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        
        # clear background to black and clear depth buffer
        glClearColor(0.2, 0.2, 0.2, 1.0)
 
        # disable depth test (z-buffer)
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # shading
        glShadeModel(GL_SMOOTH)
        glPolygonMode(GL_FRONT, GL_FILL)
        glPolygonMode(GL_BACK, GL_FILL)
        #glPolygonMode(GL_BACK, GL_LINE)
        
        glViewport(0, 0, window_width, window_height)

        # enable normalization of vertex normals
        glEnable(GL_NORMALIZE)
        
        # enable line antialiasing
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(1.5)
        
        self.stepping = 3
        glPointSize(float(self.stepping)*2.0)
        #glPointSize(1.0)

        # initial view definitions
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # perspective projection
        gluPerspective(40.0, float(window_width) / float(window_height), 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    def init(self):
        Scene.init(self)
        
        self.triangles = triangles = openOff("./meshes/icosa.off").get_triangles()
        self.mesh = TriangleMeshNode(triangles   = triangles,
                                scene       = self, 
                                #scaling=[0.5, 0.5, 0.5],
                                scaling     = [1.0, 1.0, 1.0], 
                                position    = [0.0, 0.0, 0.0],
                                draw_origin = False)
        self.pointer = PointerNode(scene       = self, 
                                   draw_origin = False)
        self.points = ColoredPointCloudNode(scene          = self, 
                                            color          = (1.0, 1.0, 1.0, 1.0), 
                                            position       = [0.0, 0.0, 10.0],
                                            draw_origin    = False)
        self.helpers = ColoredPointCloudNode(scene          = self, 
                                            color          = (1.0, 1.0, 1.0, 1.0), 
                                            position       = [0.0, 0.0, 0.0],
                                            draw_origin    = False)
        self.children.append(self.mesh)
        self.children.append(self.pointer)
        self.children.append(self.points)
        self.children.append(self.helpers)
    
    def raytrace(self, area=None):
        self._log.info(u"Starting raytracing...")
        modelview = array(glGetDoublev(GL_MODELVIEW_MATRIX)).transpose()
        inv_modelview = inv(modelview)
        eye = dot(inv_modelview, array([0.0, 0.0, 0.0, 1.0]))
        
        transformation = self.mesh.get_transformation()
        transformed_triangles = self.triangles.transformed(transformation)
        normal_map = transformed_triangles.get_vertex_normal_map()
        
        stepping = self.stepping
        if area:
            point_tl, point_br = area
            window_width = point_br[0] - point_tl[0]
            window_height = point_br[1] - point_tl[1]
            steps_x = range(point_tl[0], point_tl[0]+window_width, stepping)
            steps_y = range(glutGet(GLUT_WINDOW_HEIGHT) - point_br[1], glutGet(GLUT_WINDOW_HEIGHT) - point_br[1]+window_height, stepping)
        else:
            window_width = glutGet(GLUT_WINDOW_WIDTH)
            window_height = glutGet(GLUT_WINDOW_HEIGHT)
            steps_x = range(0, window_width, stepping)
            steps_y = range(0, window_height, stepping)
        self._log.debug(u"Rendering window: %s" % str((window_width, window_height)))
        
        surface_points = []
        progress = ProgressBar(0, len(steps_x) * len(steps_y), mode='fixed')
        progress.output()
        for window_x in steps_x:
            for window_y in steps_y:
                plane_point = array(gluUnProject(float(window_x), float(window_y), 0.0))
                intersection = transformed_triangles.get_closest_intersection(eye[0:3], plane_point, normal_map)
                if intersection:
                    intersection_triangle, intersection_point, intersection_normal = intersection
                    color = self.get_color(intersection_point, eye[0:3], intersection_normal, 0, transformed_triangles, normal_map)
                    surface_points.append((intersection_point, intersection_normal, color))
                progress.increment_amount()
                progress.output()
        
        print
        glDisable(GL_LIGHTING)
        self.mesh.visible = False
        self.points.points = surface_points
        self.points.update_display_list()
    
    def get_color(self, intersection_point, ray_origin, normal, current_recursion, transformed_triangles, normal_map):
        lights = [GL_LIGHT0, GL_LIGHT1]
        colors = array([0.0, 0.0, 0.0, 0.0])
        
        for light in lights:
            light_position          = array(glGetLightfv(light, GL_POSITION))[0:3]
            light_direction         = light_position - intersection_point
            light_direction         = light_direction / norm(light_direction)
            
            if not self.is_in_shadow(intersection_point, light_position, transformed_triangles, normal_map):
                light_ambient       = array(glGetLightfv(light, GL_AMBIENT))
                light_diffuse       = array(glGetLightfv(light, GL_DIFFUSE))
                light_specular      = array(glGetLightfv(light, GL_SPECULAR))
                material_ambient    = array(glGetMaterialfv(GL_FRONT, GL_AMBIENT))
                material_diffuse    = array(glGetMaterialfv(GL_FRONT, GL_DIFFUSE))
                material_specular   = array(glGetMaterialfv(GL_FRONT, GL_SPECULAR))
            else:
                light_ambient       = array([0,0,0,1])
                light_diffuse       = array([0,0,0,1])
                light_specular      = array([0,0,0,1])
                material_ambient    = array([0,0,0,1])
                material_diffuse    = array([0,0,0,1])
                material_specular   = array([0,0,0,1])
                
            incoming_direction = intersection_point - ray_origin
            outgoing_direction = 2 * (normal * inner(normal, incoming_direction)) - incoming_direction
            
            reflective = array([0, 0, 0, 0])
            while current_recursion + 1 < self.max_recursion:
                current_recursion += 1
                new_intersection = transformed_triangles.get_closest_intersection(intersection_point, intersection_point + outgoing_direction, normal_map)
                if new_intersection != None:
                    reflective += self.get_color(new_intersection[1], intersection_point, new_intersection[2], current_recursion, transformed_triangles, normal_map)
            
            ambient     = light_ambient * material_ambient
            diffuse     = light_diffuse * material_diffuse * inner(normal, light_direction)
            specular    = light_specular * material_specular * reflective
            
            colors += ambient + diffuse + specular
        
        return colors
        
    def is_in_shadow(self, intersection_point, light_position, transformed_triangles, normal_map):
        return transformed_triangles.get_closest_intersection(intersection_point+0.1, light_position, normal_map) != None
    
