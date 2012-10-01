import logging

from numpy import cross, append, sign, inner, mean, pi, arctan2, sqrt,  abs, array, dot
from numpy.linalg import norm, inv

from datastructures import MultiValueDict

class GeometricObject(object):
    intersection_tolerance = 0.00001
    def __init__(self):
        pass

class Plane(GeometricObject):
    def __init__(self, params):
        self.params = params
    
    def _get_a(self):
        return self.params[0]
    a = property(_get_a)
    
    def _get_b(self):
        return self.params[1]
    b = property(_get_b)
    
    def _get_c(self):
        return self.params[2]
    c = property(_get_c)
    
    def _get_d(self):
        return self.params[3]
    d = property(_get_d)
    
    def _get_normal(self):
        return self.params[0:3]
    normal = property(_get_normal)
    
    def get_signed_distance(self, point):
        return (inner(self.normal, point) + self.d)# / norm(self.normal)
    
    def get_side(self, geom_object):
        return sign(self.get_signed_distance(geom_object.vertices[0]))
    
    def intersects_edge(self, v1, v2):
        d1 = self.get_signed_distance(v1)
        d2 = self.get_signed_distance(v2)
        return (abs(d1) > self.intersection_tolerance) and (abs(d2) > self.intersection_tolerance) and sign(d1) != sign(d2)
    
    def get_edge_intersection(self, v1, v2):
        diff = v2 - v1
        factor = (inner(self.normal, v1) + self.d) / inner(self.normal, diff)
        return v1 + (abs(factor) * diff)
    
    def __str__(self):
        return str(self.params)

class Polygon(GeometricObject):
    def __init__(self, vertices):
        GeometricObject.__init__(self)
        self.vertices = vertices
    
    def intersects_plane(self, plane):
        any_negative = False
        any_positive = False
        
        for vertex in self.vertices:
            vertex_sign = sign(inner(plane.normal, vertex) + plane.d)
            any_positive = any_positive or (vertex_sign == 1)
            any_negative = any_negative or (vertex_sign == -1)
        
        return any_positive and any_negative
    
    def lies_in_plane(self, plane):
        for vertex in self.vertices:
            if abs(plane.get_signed_distance(vertex)) > self.intersection_tolerance:
                return False
        return True

class Triangle(Polygon):
    def __init__(self, vertices):
        Polygon.__init__(self, vertices)
        self.normal = self._computeNormal()
    
    def _computeNormal(self):
        normal = (cross(self.vertices[1] - self.vertices[0], self.vertices[2] - self.vertices[0]))
        return normal / norm(normal)
    
    def get_plane(self):
        return Plane(append(self.normal, [inner(self.normal, self.vertices[0]), ]))
    
    def get_plane_intersections(self, plane):
        intersections = []
        for vertex_index in range(len(self.vertices)):
            v1 = self.vertices[vertex_index]
            v2 = self.vertices[(vertex_index+1) % len(self.vertices)]
            if plane.intersects_edge(v1, v2):
                intersections.append((vertex_index, plane.get_edge_intersection(v1, v2)))
                if len(intersections) == 2:
                    break; # no need to go on, since only 2 intersections are possible
        return intersections
    
    def split(self, intersection1, intersection2):
        vertex_index1, new_vertex1 = intersection1
        vertex_index2, new_vertex2 = intersection2
        
        if vertex_index1 + 1 == vertex_index2:
            # vertex_index2 is on the triangle side
            quad = Quad([self.vertices[vertex_index1], new_vertex1, new_vertex2, self.vertices[(vertex_index1+2) % len(self.vertices)]])
            triangle = Triangle([new_vertex1, self.vertices[vertex_index2], new_vertex2])
        else:
            # vertex_index1 is on the triangle side
            quad = Quad([new_vertex1, self.vertices[vertex_index2], self.vertices[(vertex_index2+1) % len(self.vertices)], new_vertex2])
            triangle = Triangle([self.vertices[vertex_index1], new_vertex1, new_vertex2])
        
        return quad.tesselate() + [triangle, ]
    
    def __str__(self):
        return "Vertices: %s, Normal: %s" % (str(self.vertices), str(self.normal))

class Quad(Polygon):
    def __init__(self, vertices):
        Polygon.__init__(self, vertices)
    
    def tesselate(self):
        triangle1 = Triangle(self.vertices[0:3])
        triangle2 = Triangle(self.vertices[2:4] + self.vertices[0:1])
        return [triangle1, triangle2]
        
class TriangleList(list):
    def get_vertices(self, distinct=False):
        """Returns a list of all vertices of all vertices of all triangles
        contained within the list.
        
        :Parameters:
            distinct : boolean
                toggle filtering of duplicate vertices
        
        :return: a list of vertices
        """
        vertex_list = []
        vertex_map = {}
        for triangle in self:
            for vertex in triangle.vertices:
                if distinct:
                    vertex_map[tuple(vertex)] = vertex
                else:
                    vertex_list.append(vertex)
        if distinct:
            return vertex_map.values()
        else:
            return vertex_list
    
    def get_vertex_map(self):
        result = MultiValueDict()
        for triangle in self:
            for vertex in triangle.vertices:
                result.appendlist(tuple(vertex), triangle)
        return result
    
    def get_vertex_normal_map(self):
        vertex_map = self.get_vertex_map()
        normal_map = {}
        for vertex, triangles in vertex_map.lists():
            normals = [triangle.normal for triangle in triangles]
            normal_map[tuple(vertex)] = mean([triangle.normal for triangle in triangles], axis=0)
        return normal_map
    
    def get_vertex_sphere_map(self):
        vertex_map = self.get_vertex_map()
        texture_map = {}
        for vertex in vertex_map.keys():
            u = (pi + arctan2(vertex[1], vertex[0])) / (2 * pi)
            v = arctan2(sqrt(vertex[0]**2 + vertex[1]**2), vertex[2]) / pi
            texture_map[tuple(vertex)] = (u, v)
        return texture_map

    def get_bounding_box(self):
        vertices = array(self.get_vertices(distinct=True))
        vertices.sort(0)
        return (vertices[0, :], vertices[-1, :])

    def transformed(self, transformation):
        result = TriangleList()
        for triangle in self:
            new_vertices = [dot(transformation, append(vertex, [1.0, ]))[0:3] for vertex in triangle.vertices]
            new_triangle = Triangle(new_vertices)
            result.append(new_triangle)
        return result
        
    def get_closest_intersection(self, point1, point2, vertex_normal_map):
        """Returns a (triangle, point) pair, where the triangle intersects the line defined by the two given points in the associated point closest to point1."""
        intersection = None
        intersection_distance = None
        direction = point2 - point1
        for triangle in self:
            d = triangle.get_plane().params[3]
            normal = triangle.normal
            w = inner(normal, direction)
            if w != 0:
                t = (d - inner(normal, point1)) / w
                if t < 0:
                    continue
                intersection_point = point1 + t * direction
                A, B, C = triangle.vertices
                q = inner(cross(B-A, C-A), normal)
                b1 = inner(cross(C-B, intersection_point-B), normal) / q
                b2 = inner(cross(A-C, intersection_point-C), normal) / q
                b3 = inner(cross(B-A, intersection_point-A), normal) / q
                if b2>0 and b3>0 and b2+b3<=1:
                    if not intersection or (intersection_distance and intersection_distance > t):
                        intersection_distance = t
                        intersection_normal = b1*vertex_normal_map[tuple(A)] \
                                            + b2*vertex_normal_map[tuple(B)] \
                                            + b3*vertex_normal_map[tuple(C)]
                        intersection_normal = intersection_normal / norm(intersection_normal)
                        intersection = (triangle, intersection_point, intersection_normal)
        return intersection
        
