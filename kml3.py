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

from inspect import getmro
from enum import Enum, EnumMeta

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
        return self.name

class displayModeEnum(Enum):
    default = 0
    hide = 1
    
    def __str__(self):
        return ' <displayMode>{}</displayMode>\n'.format(self.name)


################################################################################################
#                                                                                              #
#   KML Abstract Object definitions (base classes)                                             #
#                                                                                              #
################################################################################################


class KMLObject(object):

    def __init__(self, permittedAttributes):
        #self.__parent = None
        self.__id = None
        self.__attributes = {}
        self.__depth = 0
        self.__permittedAttributes = permittedAttributes
        logging.debug('KMLObject created')
    
    @property
    def indent(self):
        return ' ' * self.depth
    
    @property
    def depth(self):
        return self.__depth
    
    @depth.setter
    def depth(self, value):
        self.__depth = value
        for a in self.__attributes:
            if KMLObject in getmro(self.__attributes[a].__class__):
                self.__attributes[a].depth = self.depth + 1

    @property
    def id(self):
        """
        Many object contain an ID tag for later reference.
        
        If set, this property will return the tag.  if not, it returns and empty
        string.
        """
        if self.__id is None:
            return ''
        else:
            return ' id="{}"'.format(self.__id)

    @id.setter
    def id(self, id):
        self.__id = id

    
    def __getitem__(self, key):
        return self.__attributes[key]
    
    def __setitem__(self, key, value):
        if key in self.__permittedAttributes:                                                           # Check if this object supports this attribute
            if key not in attributeTypes:                                                               # Check if the datatype has been defined
                raise RuntimeError('Type for attribute {} not defined'.format(key))                     # Datatype not defined
            if type(value) == attributeTypes[key]:                                                      # Check if the data passed in is already of the correct type
                self.__attributes[key] = value                                                          # - if so, assign it
                logger.debug('Object of type {} appended'.format(type(value)))                          
                if hasattr(self.__attributes[key], 'depth'):                                            # Check if the attribute has a depth property
                    self.__attributes[key].depth = self.depth + 1                                       # - if so, increase it
            else:                                                                                       # Data is not of the correct type
                if Enum in getmro(attributeTypes[key]):                                                 # Check if type is an Enum
                    logger.debug('Attribute type of Enum')
                    # Enums are created slightly different than objects
                    if number.isInt(value):                                                             # Check if the value can be converted to an integer (Enums can be set by integer value)
                        self.__attributes[key] = attributeTypes[key](int(value))                        # Set the Enum type by integer value
                    else:                                                                               # 
                        self.__attributes[key] = attributeTypes[key][str(value).lower()]                # Set the enum by name (case insensitive as Key is used to build the tag)
                elif KMLObject in getmro(attributeTypes[key]):                                          # Check if type is an Object
                    logger.debug('Attribute type of KMLObject')
                    # Setting an object as an attribute increases is indentation
                    self.__attributes[key] = attributeTypes[key](value)                                 # Create an instance of the object, passing the value to the init
                    self.__attributes[key].depth = self.depth + 1                                       # Increase the objects depth
                else:                                                                                   # All other types
                    logger.debug('Standard attribute type')
                    self.__attributes[key] = attributeTypes[key](value)                                 # Create an instance of the type passing the value to the init
        else:
            logging.debug('Attibute {} not permitted at {}'.format(key, self.__class__.__name__))       # Attribute is not permitted/supported by this object
    
    def __delitem__(self, key):
        del self.__attributes[key]
    
    def __str__(self):
        tmp = ''
        for a in self.__attributes:
            logging.debug(a)
            if KMLObject in getmro(self.__attributes[a].__class__):
                # Objects handle their own code formatting and indentation
                tmp += str(self.__attributes[a])
            else:
                # Simple attributes and be easily formatted
                # All enums should know how to return the proper value when requested.  See the __str__() of the respective enum.
                tmp += self.indent + ' <{}>{}</{}>\n'.format(a,str(self.__attributes[a]),a)
        return tmp

class KMLFeature(KMLObject):
    def __init__(self):
        super().__init__(['name', 'description', 'visibility', 'open', 'atom:link', 'atom:author', 'address', 'xal:AddressDetails', 'phoneNumber', 'Snippet'])
        logging.debug('KMLFeature created')
    
    def __str__(self):
        return super().__str__()

class ATOMLink(KMLObject):
    # atom:link is a special case.  It has the link value inside the tag.  No other attributes permitted
    def __init__(self, value):
        self.link = value
        super().__init__([])
        logging.debug('ATOMLink created')
    
    def __str__(self):
        return self.indent + '<atom:link href="{}" />\n'.format(self.link)
    
class ATOMAuthor(KMLObject):
    def __init__(self, name):
        super().__init__(['atom:name'])
        logging.debug('ATOMName created')
        self['atom:name'] = name
    
    def __str__(self):
        tmp = self.indent + '<atom:author>\n'
        tmp += super().__str__()
        tmp += self.indent + '</atom:author>\n'
        return tmp

class Snippet(KMLObject):
    def __init__(self, value, maxLines = None):
        self.maxLines = maxLines
        self.value = value
        super().__init__([])
        logging.debug('Snippet created')
    
    def __str__(self):
        tmp = self.indent + '<Snippet'
        if self.maxLines is not None:
            tmp += ' maxLines="{}"'.format(self.maxLines)
        tmp += '>{}</Snippet>\n'.format(self.value)
        return tmp

















attributeTypes = {
    'latitude'              : angle90,
    'longitude'             : angle180,
    'altitude'              : number,
    'visibility'            : booleanEnum,
    'name'                  : str,
    'description'           : str,
    'open'                  : booleanEnum,
    'atom:link'             : ATOMLink,
    'atom:author'           : ATOMAuthor,
    'atom:name'             : str,
    'address'               : str,
    'xal:AddressDetails'    : str,
    'phoneNumber'           : str,
    'Snippet'               : Snippet,
    'View'                  : KMLView,
}
