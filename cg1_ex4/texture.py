# -*- coding: utf-8 -*-

import logging

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Texture(object):
    """Holder for an OpenGL compiled texture

    This object holds onto a texture until it
    is deleted.  Provides methods for storing
    raw data or PIL images (store and fromPIL
    respectively)

    Attributes:
        components -- number of components in the image,
            if 0, then there is no currently stored image
        texture -- OpenGL textureID as returned by a call
            to glGenTextures(1), will be freed when the
            Texture object is deleted
    """
    def __init__( self, image=None ):
        """Initialise the texture, if image is not None, store it

        image -- optional PIL image to store
        """
        self._log = logging.getLogger(self.__class__.__name__)
        self.components = 0
        self.texture = glGenTextures(1)
        self.source_image = None
        self.window = glutGetWindow()
        if image is not None:
            self.fromPIL( image )
    def store(
        self,
        components, format,
        x,y,
        image,
    ):
        """define the texture's parameters...
            components -- number of components (3 or 4 for
                RGB and RGBA respectively)
            format -- GL_RGB, GL_RGBA, GL_LUMINANCE
            x,y -- dimensions of the image
            image -- string, data in raw (unencoded) format

        See:
            glBindTexture, glPixelStorei, glTexImage2D
        """
        glutSetWindow(self.window)
        #self._log.debug(u"Storing texture %d (%d x %d x %d) for window %d..." % (self.texture, x, y, components, glutGetWindow()))
        self.components = components
        # make our ID current
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        # copy the texture into the current texture ID
        #glPixelStorei(GL_PACK_ALIGNMENT, 1)
        glTexImage2D(
            GL_TEXTURE_2D, 0, components, x, y, 0, format, GL_UNSIGNED_BYTE, image
        )
    def __call__( self ):
        """Enable and select the texture...
        See:
            glBindTexture, glEnable(GL_TEXTURE_2D)
        """
        glutSetWindow(self.window)
        #self._log.debug(u"Binding texture %d in window %d..." % (self.texture, glutGetWindow()))
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glEnable(GL_TEXTURE_2D)
        
    def __del__( self, glDeleteTextures = glDeleteTextures ):
        """Clean up the OpenGL display-list resources
        See:
            glDeleteTextures
        """
        glutSetWindow(self.window)
        glDeleteTextures( [self.texture])
    def fromPIL( self, image ):
        """Automated storage of image data from a PIL Image instance

        Uses the ensureRGB method to convert the image to RGB,
        then ensurePow2 to make the image a valid size for OpenGL,
        then calls self.store(...) with the appropriate arguments.

        Returns the number of components in the image
        """
        image = self.ensureRGB( image )
        image = self.ensurePow2( image )
        self.source_image = image
        components, format = getLengthFormat( image )
        x, y, image = image.size[0], image.size[1], image.tostring("raw", image.mode, 0, -1)
        self.store(
            components, format,
            x,y,
            image,
        )
        return components
    def ensureRGB( self, image ):
        """Ensure that the PIL image is in RGB mode

        Note:
            This method will create a _new_ PIL image if
            the image is in Paletted mode, otherwise just
            returns the same image object.
        """
        if image.mode == 'P':
            self._log.info( "Paletted image found, converting: %s", image.info )
            image = image.convert( 'RGB' )
        return image
    def ensurePow2( self, image ):
        """Ensure that the PIL image is pow2 x pow2 dimensions

        Note:
            This method will create a _new_ PIL image if
            the image is not a valid size (It will use BICUBIC
            filtering (from PIL) to do the resizing). Otherwise
            just returns the same image object.
        """
        from Image import BICUBIC
        ### Now resize non-power-of-two images...
        # should check whether it needs it first!
        newSize = bestSize(image.size[0]),bestSize(image.size[1])
        if newSize != image.size:
            self._log.info( "Non-power-of-2 image %s found resizing: %s", image.size, image.info )
            image = image.resize( newSize, BICUBIC )
        return image
    
    def refresh(self):
        self.fromPIL(self.source_image)

def getLengthFormat( image ):
    """Return PIL image component-length and format

    This returns the number of components, and the OpenGL
    mode constant describing the PIL image's format.  It
    currently only supports GL_RGBA, GL_RGB and GL_LUIMANCE
    formats (PIL: RGBA, RGBX, RGB, and L), the Texture
    object's ensureRGB converts Paletted images to RGB
    before they reach this function.
    """
    if image.mode == "RGB":
        length = 3
        format = GL_RGB
    elif image.mode in ("RGBA","RGBX"):
        length = 4
        format = GL_RGBA
    elif image.mode == "L":
        length = 1
        format = GL_LUMINANCE
    elif image.mode == 'LA':
        length = 2
        format = GL_LUMINANCE_ALPHA
    else:
        raise TypeError ("Currently only support Luminance, RGB and RGBA images. Image is type %s"%image.mode)
    return length, format

def bestSize( dim ):
    """Try to figure out the best power-of-2 size for the given dimension

    At the moment, this is the next-largest power-of-two
    which is also <= glGetInteger( GL_MAX_TEXTURE_SIZE ).
    """
    boundary = min( (glGetInteger( GL_MAX_TEXTURE_SIZE ), dim))
    test = 1
    while test < boundary:
        test = test * 2
    return test
