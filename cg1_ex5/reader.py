import logging

from numpy import array

from geometry import Triangle, TriangleList

class FileFormatException(Exception):
    pass

class openOff(object):
    def __init__(self, filename):
        self._filename = filename
        self._log = logging.getLogger('openOff')
    
    def get_triangles(self):
        #f = open(self._filename)
        with open(self._filename) as f:
        #try:
            self._log.debug(u"Opened file '%s' as OFF file." % self._filename)
            vertices = []
            triangles = TriangleList()
            first_line = f.readline()
            if first_line.startswith("OFF"):
                vertice_count, polygon_count, edge_count = [ int(value.strip()) for value in f.readline().split(" ") ]
                for vertex_index in range(vertice_count):
                    vertices.append(array([ float(coord.strip()) for coord in f.readline().split(" ") if coord.strip() != "" ]))
                for polygon_index in range(polygon_count):
                    n, v1, v2, v3 = [ int(value.strip()) for value in f.readline().split(" ") if value.strip() != "" ]
                    if n != 3:
                        raise FileFormatException("The file '%s' contains polygons, that are not triangles." % self._filename)
                    triangles.append(Triangle([vertices[v1], vertices[v2], vertices[v3]]))
            else:
                raise FileFormatException("The file '%s' is not of the expected format: %s" % (self._filename, first_line))    
        #finally:
        #    f.close()
                
        self._log.debug(u"Read %d triangles from file '%s'." % (len(triangles), self._filename))
        return triangles
