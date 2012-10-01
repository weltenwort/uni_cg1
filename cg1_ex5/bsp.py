from random import choice

from numpy import inner
from OpenGL.GL import *
from OpenGL.GLUT import *

from scenegraph import Node

class BspTree(Node):
    def __init__(self, node_objects, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.node_objects = node_objects
        self.left_child   = None
        self.right_child  = None
    
    def autopartition(self):
        #print("depth: %d" % depth)
        self.partition(self._get_autopartition_plane)
        if self.left_child:
            self.left_child.autopartition()
        if self.right_child:
            self.right_child.autopartition()
    
    def draw(self, occluded=False):
        """
        :Parameters:
          occluded : boolean
            whether or not this tree is occluded
        """
        Node.draw(self)

class TriangleBspTree(BspTree):
    
    def _get_autopartition_plane(self):
        #partitioning_triangle = choice(self.node_objects)
        partitioning_triangle = self.node_objects[0]
        return partitioning_triangle.get_plane()
    
    def partition(self, partition_plane_factory):
        self.partition_plane = partition_plane = partition_plane_factory()
        keep        = []
        left_side   = []
        right_side  = []
        
        #if not self.node_objects[0].lies_in_plane(partition_plane):
        #print("Triangle: %s" % self.node_objects[0])
        #print("Plane: %s" % partition_plane)
        #print("Distances: %f %f %f" % tuple([partition_plane.get_signed_distance(v) for v in self.node_objects[0].vertices]))
        
        for geom_object in self.node_objects:
            if geom_object.lies_in_plane(partition_plane):
                keep.append(geom_object)
            else:
                if geom_object.intersects_plane(partition_plane):
                    intersections = geom_object.get_plane_intersections(partition_plane)
                    if False and len(intersections) == 2:
                        new_objects = geom_object.split(*intersections)
                    else:
                        new_objects = [geom_object, ]
                    for new_object in new_objects:
                        if partition_plane.get_side(new_object) == 1:
                            right_side.append(new_object)
                        else:
                            left_side.append(new_object)
                else:
                    if partition_plane.get_side(geom_object) == 1:
                        right_side.append(geom_object)
                    else:
                        left_side.append(geom_object)
        
        if not len(keep) > 0:
            assert(False)
        del(self.node_objects)
        self.node_objects = keep
        if len(right_side) > 0:
            self.right_child = TriangleBspTree(right_side, scene=self.scene)
        if len(left_side) > 0:
            self.left_child  = TriangleBspTree(left_side, scene=self.scene)
        #print("same: %d, left: %d, right %d" % (len(keep), len(left_side), len(right_side)))
    
    def draw(self, occluded=False):
        """
        :Parameters:
          occluded : boolean
            whether or not this tree is occluded
        """
        
        # draw plane normal
        glPushAttrib(GL_ENABLE_BIT)
        glPushMatrix()
        glDisable(GL_LIGHTING)
        glBegin(GL_LINES)
        glColor3f(1, 1, 1)
        glVertex3fv(self.node_objects[0].vertices[0])
        glVertex3fv(self.node_objects[0].vertices[0] + self.partition_plane.normal)
        #glColor3f(0, 0, 1)
        #glVertex3fv(-self.scene.eye[0:3])
        #glVertex3fv(self.position)
        #glVertex3fv([0, 0, 2])
        #glVertex3fv([0, 0, 0])
        glEnd()
        #glTranslate(*self.scene.eye[0:3])
        #glutWireSphere(0.075, 16, 16)
        glPopMatrix()
        glPopAttrib()
        
        #left_is_occluded = self.partition_plane.get_signed_distance(self.scene.eye[0:3]) < 0
        left_is_occluded = inner(self.node_objects[0].vertices[0] - self.scene.eye[0:3], self.partition_plane.normal) > 0
        
        if self.left_child:
            self.left_child.draw(left_is_occluded)
        
        #glDisable(GL_LIGHTING)
        #glPushAttrib(GL_CURRENT_BIT)
        glBegin(GL_TRIANGLES)
        
        if occluded:
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.0, 0.0, 0.5])
        else:
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.0, 1.0, 0.0, 0.5])
            
        for geom_object in self.node_objects:
            glNormal3fv(geom_object.normal)
            for vertex in geom_object.vertices:
                glVertex3fv(vertex)
        
        glEnd()
        #glPopAttrib()
        #glEnable(GL_LIGHTING)
        
        if self.right_child:
            self.right_child.draw(not left_is_occluded)
