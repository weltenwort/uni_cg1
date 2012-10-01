from numpy import cross, append, sign, inner, mean, pi, arctan2, sqrt
from numpy.linalg import norm

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
        normal = -1 * cross(self.vertices[0] - self.vertices[1], self.vertices[0] - self.vertices[2])
        return normal / norm(normal)
    
    def get_plane(self):
        return Plane(append(self.normal, [-inner(self.normal, self.vertices[0]), ]))
    
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
