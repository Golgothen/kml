import logging

logger = logging.getLogger()
# Remove after testing
f = logging.Formatter('%(levelname)-8s:%(funcName)-20s %(lineno)-5s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(f)
logger.addHandler(h)
logger.setLevel(logging.DEBUG)

from datetime import datetime
from time import time
#from inspect import getmro
#from enum import Enum, EnumMeta

from abstract import *


class entry_exit(object):
    # Decorator class to assist in logger tracing
    def __init__(self, f):
        self.f = f
    
    def __call__(self, *args):
        t = time()
        logger.debug('Entering {}'.format(self.f.__name__))
        retval = self.f(*args)
        logger.debug('Exiting {}, took {} microseconds'.format(self.f.__name__, (time() - t)*1000000.0))
        return retval


################################################################################################
#                                                                                              #
#   KML Data Type definitions                                                                  #
#                                                                                              #
################################################################################################

class number(float):
    """
    Subclass of the float datatype.
    
    Provides two class methods:
    
        isInt() - returns true or false if a given argument can be converted to an int
        
        isFloat() - returns true or false if a given argument can be converted to a float
    
    """
    #
    # Extends      : float
    #
    # Extended by  : angle, angle90, angle180, angle360
    #
    # Contains     :
    #
    # Contained By : LabelStyle, IconStyle, Coords, LookAtCoords
    # 
    def __new__(self, value):
        if type(value) not in [float, int]:
            raise TypeError('Value must be a number, not {}'.format(type(value)))
        return float.__new__(self, value)

    @classmethod
    def isInt(number, value):
        try:
            int(str(value))
            return True
        except ValueError:
            return False

    @classmethod
    def isFloat(number, value):
        try:
            float(str(value))
            return True
        except ValueError:
            return False

class colorAttribute(int):
    """
    Subclass of the int datatype.  Used to represent a color attribute.
    Valid values are from 0 to 255.
    
    Can be created in two ways:
    
        x = colorAttribute(255)
        x = colorAttribute('FF')
    
    """
    #
    # Extends      : int
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained By : Color
    # 

    def __new__(self, value=0):
        if type(value) not in [int, str]:
            raise TypeError('Value must be of type int or str, not {}'.format(type(value)))
        if type(value) is str:
            value = int(value, 16)
        if not 0 <= value <= 255:
            raise ValueError('Value must be between 0 and 255')
        return int.__new__(self, value)

    def __str__(self):
        return '{:02X}'.format(self)

class numberPercent(number):
    """
    Subclass of number class.  Used to represent a percentage value between 0.0 and 1.0
    """

    #
    # Extends      : number
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained By : LineStyle,
    # 

    def __init__(self, value):
        if not (0.0 <= value <= 1.0):
            raise ValueError('Value out of range')

class angle90(number):
    """
    Subclass of number class.  Used to represent an angle value between -90.0 and 90.0
    """

    #
    # Extends      : number
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained By : Coords, LatLonBox
    # 

    def __init__(self, value):
        if not (-90.0 <= value < 90.0):
            raise ValueError('Value out of range')

class anglepos90(number):
    """
    Subclass of number class.  Used to represent an angle value between 0.0 and 90.0
    """

    #
    # Extends      : number
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained By : ViewCoords
    # 

    def __init__(self, value):
        if not (0.0 <= value <= 90.0):
            raise ValueError('Value out of range')

class angle180(number):
    """
    Subclass of number class.  Used to represent an angle value between -180.0 and 1800.0
    """
    #
    # Extends      : number
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained By : Coords, ViewCoords, CameraCoords
    # 

    def __init__(self, value):
        if not (-180.0 <= value < 180.0):
            raise ValueError('Value out of range')

class angle360(number):
    """
    Subclass of number class.  Used to represent an angle value between 0.0 and 360.0
    """

    #
    # Extends      : number
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained By : IconStyle, Heading
    # 

    def __init__(self, value):
        if not (0.0 <= value < 360.0):
            raise ValueError('Value out of range')

################################################################################################
#                                                                                              #
#   KML Enum definitions                                                                       #
#                                                                                              #
################################################################################################

class altitudeModeEnum(Enum):
    """
        clampToGround - (default)
            Indicates to ignore the altitude specification and drape the overlay over
            the terrain.
        relativeToGround
            Interprets the <altitude> as a value in meters above the ground.
        absolute
            Sets the altitude of the overlay relative to sea level, regardless
            of the actual elevation of the terrain beneath the element. For example, if
            you set the altitude of an overlay to 10 meters with an absolute altitude
            mode, the overlay will appear to be at ground level if the terrain beneath
            is also 10 meters above sea level. If the terrain is 3 meters above sea
            level, the overlay will appear elevated above the terrain by 7 meters.
        relativeToSeaFloor
            Interprets the <altitude> as a value in meters above the sea floor. If the
            point is above land rather than sea, the <altitude> will be interpreted as
            being above the ground.
        clampToSeaFloor
            The <altitude> specification is ignored, and the overlay will be draped over
            the sea floor. If the point is on land rather than at sea, the overlay will
            be positioned on the ground.
    """
    clampToGround = 0
    relativeToGround = 1
    absolute = 2
    relativeToSeaFloor = 3
    clampToSeaFloor = 4
    
    def __str__(self):
        if self.value < 3:
            return ' <altitudeMode>{}</altitudeMode>\n'.format(self.name)
        else:
            return ' <gx:altitudeMode>{}</gx:altitudeMode>\n'.format(self.name)

class booleanEnum(Enum):
    no = 0
    off = 0
    false = 0
    yes = 1
    on = 1
    true = 1
    
    @classmethod
    def default(cls):
        return cls.yes
    
    

    def __str__(self):
        return str(self.value)

class colorModeEnum(Enum):
    normal = 0
    random = 1
    
    def __str__(self):
        return ' <colorMode>{}</colorMode>\n'.format(self.name)

class displayModeEnum(Enum):
    default = 0
    hide = 1
    
    def __str__(self):
        return ' <displayMode>{}</displayMode>\n'.format(self.name)



attributeTypes = {
    'latitude'      : angle90,
    'longitude'     : angle180,
    'altitude'      : number,
    'visibility'    : booleanEnum,
    'name'          : str,
    'description'   : str,
    'open'          : booleanEnum,
    'atom:link'     : ATOMLink,
}



