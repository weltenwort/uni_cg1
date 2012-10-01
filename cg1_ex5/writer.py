# -*- coding: utf-8 -*-

import time

import Image
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def capture_screen(filename=None):
    window_width = glutGet(GLUT_WINDOW_WIDTH)
    window_height = glutGet(GLUT_WINDOW_HEIGHT)
    filename = filename or time.strftime('%Y%m%d_%H%M%S.png')
    
    data = glReadPixels(0, 0, window_width, window_height, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.fromstring('RGB', (window_width, window_height), data)
    image.save(filename)
    
    return (image, filename)
