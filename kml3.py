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
from collections import deque

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
            raise TypeError('Value must be a number, not {}'.format(value.__class__.__name__))
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
    Subclass of the int datatype.  Used to represent a single color attribute.
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
            raise TypeError('Value must be of type int or str, not {}'.format(value.__class__.__name__))
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

class colorAttribute(int):
    """
    Represents a color attribute.  Valid values are from 0 to 255.
    
    Usage:
    
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
            raise TypeError('Value must be of type int or str, not {}'.format(value.__class__.__name__))
        if type(value) is str:
            value = int(value, 16)
        if not 0 <= value <= 255:
            raise ValueError('Value must be between 0 and 255')
        return int.__new__(self, value)

    def __str__(self):
        return '{:02X}'.format(self)

class Color(object):
    """
    Represents a color as a complete attribute with alpha, red, green and blue.
    
    Color attribute can be expressed as an 8 byte value in the format of aabbggrr:
    
        aa = Alpha
        bb = Blue
        gg = Green
        rr = Red

    Usage:
        x = Color('FF0000FF')                # gives RED
        x = Color('FF00FF00')                # gives GREEN
        x = Color('FFFF0000')                # gives BLUE
        x = Color('FFFF0000')                # gives BLUE
        x = Color('FFFFFFFF')                # gives WHITE
    
    Color can also be expressed as four integer or hex values, in the order of a, b, g, r:
    
    Usage:
        x = Color(255, 0, 0, 255)            # gives RED
        x = Color('FF', '00', '00', 'FF')    # gives RED
        
    All attributes can be modified using decimal values or hex strings.
    
    Usage:
        x.red = 255
        x.green = 'A0'
        x.alpha = '80'
    
    """
    #
    # Extends      :
    #
    # Extended by  :
    #
    # Contains     : colorAttribute
    #
    # Contained by : ColorStyle
    #

    def __init__(self, *args):
        
        self.__alpha = colorAttribute(255)
        self.__red = colorAttribute(255)
        self.__green = colorAttribute(255)
        self.__blue = colorAttribute(255)
        self.__setup(*args)
        logging.debug('Color created')

    def __setup(self, *args):
        if len(args) == 1:                  # If there is only one argument, assume it is a color code
            if type(args[0]) is str:        # Check it's type
                if len(args[0]) != 8:       # check it's length
                    raise ValueError('Color value must be 8 bytes in length, aabbggrr. See help(Color).')
                else:
                    self.color = args[0]    # Assign it to the setter to interpret
        elif len(args) == 4:                # If there are 4 arguments, assume they are color attribute assignments
            self.alpha = args[0]
            self.blue = args[1]
            self.green = args[2]
            self.red = args[3]
        else:
            raise RuntimeError('Invalid number of arguments for Color.  See help(Color) for usage.')
    
    @property
    def color(selfself):
        return self.__str__()
    
    @color.setter
    def color(self, value):
        self.__alpha = colorAttribute(value[:2])
        self.__blue = colorAttribute(value[2:4])
        self.__green = colorAttribute(value[4:6])
        self.__red = colorAttribute(value[6:8])
    
    @property
    def alpha(self):
        return self.__alpha

    @alpha.setter
    def alpha(self, value):
        self.__alpha = colorAttribute(value)

    @property
    def red(self):
        return self.__red

    @red.setter
    def red(self, value):
        self.__red = colorAttribute(value)

    @property
    def green(self):
        return self.__green

    @green.setter
    def green(self, value):
        self.__green = colorAttribute(value)

    @property
    def blue(self):
        return self.__blue

    @blue.setter
    def blue(self, value):
        self.__blue = colorAttribute(value)

    def __str__(self):
        return str(self.__alpha) + str(self.__blue) + str(self.__green) + str(self.__red)

class KMLDateTime(object):
    """
    Date/Time object for handling Date.Time formatting for TimeSpan and TimeStamp
    
    Usage:
    
        x = KMLDateTime('2006-05-01', 'gDate')                  # returns '2006-05-01'
        x = KMLDateTime('2006-05-01', 'gYearMonth')             # returns '2006-05'
        x = KMLDateTime('2006-05-01', 'gYear')                  # returns '2006'
        x = KMLDateTime('2006', 'gDate')                        # returns '2006-01-01'
        x = KMLDateTime('2006', 'gYearMonth')                   # returns '2006-01'
        x = KMLDateTime('2006-05-01T23:59:59Z', 'gDateTime')    # returns '2006-05-01T23:59:59Z'
        x = KMLDateTime('2006-05-01T23:59:59Z', 'UTC')          # returns '2006-05-01T23:59:59+10:00' (local time zone)
        x = KMLDateTime('2006', 'UTC')                          # returns '2006-01-01T00:00:00+10:00' (local time zone)
    """
    #
    # Extends      :
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained By : TimeSpan, TimeStamp
    #

    def __init__(self, value=datetime.now()):
        self.__value = None
        self.__format = None
        self.value = value
        self.__precision = 4

    @property
    def value(self):
        """
        Returns the portion of Date/Time as specified in format.
        
        When setting a value: 
            if only the year is given, the date will default to Jan 01.
            if only the year and month is given, the date will default to the 1st.
        
        
        Time strings must conform to KML standard as per:
            https://developers.google.com/kml/documentation/kmlreference#timestamp
            
        """
        if self.__format in ['Y', 'gYear']:
            return '{:04}'.format(self.__value.year)
        if self.__format in ['YM', 'gYearMonth']:
            return '{:04}-{:02}'.format(self.__value.year, self.__value.month)
        if self.__format in ['YMD', 'date']:
            return '{:04}-{:02}-{:02}'.format(self.__value.year, self.__value.month, self.__value.day)
        if self.__format in ['Z', 'dateTime']:  
            return self.__value.isoformat().split('.')[0] + 'Z'
        if self.__format in ['UTC']:  # TODO: Is there a name for this format in the XML Schema?
            d = datetime.now() - datetime.utcnow()
            t = d.seconds + round(d.microseconds / 1000000)
            return '{}{:+03}:{:02}'.format(self.__value.isoformat().split('.')[0], divmod(t, 3600)[0], divmod(t, 3600)[1])

    @value.setter
    def value(self, value):
        if value is not None:
            if type(value) is str:
                self.format = self.__getFormat(value)
                # Convert strings to date based in value of format
                if self.format == 'gYear':
                    # Check the Year to make sure it is are valid numbers.  If so, reasemble and convert
                    if number.isInt(value.split('-')[0]):
                        # NOTE: XML Schema 2.0 allows for 5 digit years.  Although this code will manipulate a 5 digit year,
                        #       strptime does not support it so we are stuck with a 4 digit year for now.
                        value = datetime.strptime('{:04}'.format(int(value.split('-')[0])) + '0101', '%Y%m%d')
                    else:
                        raise ValueError('Invalid year {}'.format(value[:4]))
                elif self.format == 'gYearMonth':
                    # Check the Year and Month part to make sure they are valid numbers.  If so, reasemble and convert. Default to 1st of the month
                    dateparts = value[:7].split('-')
                    if number.isInt(dateparts[0]) and number.isInt(dateparts[1]):
                        value = datetime.strptime(dateparts[0] + dateparts[1] + '01', '%Y%m%d')
                        logging.debug(value)
                    else:
                        raise ValueError('Invalid year-month {}'.format(value[:7]))
                elif self.format == 'date':
                    # Check each Year, Day and Month part to make sure they are valid numbers.  If so, reasemble and convert
                    dateparts = value[:10].split('-')
                    if number.isInt(dateparts[0]) and number.isInt(dateparts[1]) and number.isInt(dateparts[2]):
                        value = datetime.strptime(dateparts[0] + dateparts[1] + dateparts[2], '%Y%m%d')
                    else:
                        raise ValueError('Invalid year-month-day {}'.format(value[:10]))
                elif self.format ==  'dateTime':
                    # Provide strptime the formatting and convert. Straight forward
                    try:
                        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
                    except:
                        raise  # Raise what ever error gets thrown if it doesnt work
                elif self.format == 'UTC':
                    # Strip the ':' out of the timezone part and use strptime to convert the string to a datetime
                    try:
                        value = datetime.strptime(value[:len(value) - 6] + value[len(value) - 6:].replace(':', ''), '%Y-%m-%dT%H:%M:%S%z')
                    except:
                        raise  # Raise what ever error gets thrown if it doesnt work
            if type(value) is not datetime:
                raise TypeError('Failed to convert {} into Datetime'.format(type(value)))
        self.__value = value

    @property
    def format(self):
        return self.__format
    
    @format.setter
    def format(self, value):
        if value not in ['gYear',             # Year only
                         'gYearMonth',        # Year and Month
                         'date',              # Year, Month and Day
                         'dateTime',          # Full Date/Time UTC
                         'UTC']:              # Full Date/Time with UTC conversion
            raise ValueError('Format pattern does not match')
        self.__format = value
    
    def __getFormat(self, value):
        # Attempt to determine how much of the date we were given and adjust the format appropiately
        if value is None:
            return None
        datepart = None
        timepart = None
        if 'T' in value:
            datepart, timepart = value.split('T')
        else:
            datepart = value
        
        if timepart is None:
            if len(datepart) == 4:                                     # Assume just the year is given
                return 'gYear'
            elif 6 <= len(datepart) <= 7:                                # Assume year and month in either '2004-06' or '200406'
                return 'gYearMonth'
            elif 8 <= len(datepart) <= 10:                               # Assume single date in either '2004-06-12' or '20040612'
                return 'date'
        else:
            if 'Z' in timepart:                    # Assume full date time
                return 'dateTime'
            elif '+' in timepart or '-' in timepart:  # Assume UTC with time zone offset
                return 'UTC'
        raise ValueError('format not set and unable to determine format from {}'.format(value)) 
    
    def __str__(self):
        return self.value

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

class viewerOptionEnum(Enum):
    streetview = 0
    historicalimagery = 1
    sunlight = 2
    
    def __str__(self):
        return self.name

class KMLObject(object):

    def __init__(self, permittedAttributes):
        self.__depth = 0
        self.__permittedAttributes = ['id','depth','indent'] + permittedAttributes
        logging.debug('{} created'.format(self.__class__.__name__))
    
    @property
    def indent(self):
        return ' ' * self.__depth
    
    @property
    def depth(self):
        return self.__depth
    
    @depth.setter
    def depth(self, value):
        self.__depth = value
        for a in self.__dict__.items():
            if hasattr(a, 'depth'):
                setattr(a, 'depth', self.depth + 1)

    def __getattribute__(self, name):
        # Pass all inbuilt functions and private attributes up to super()
        if '__' in name:        return super().__getattribute__(name)
        
        # Exclude anything thats not in the permitted list
        if name not in self.__permittedAttributes:
            raise AttributeError('Attribute {} not supported by object {}'.format(name, self.__class__.__name__))

        # Treat id as a special case
        if name == 'id':
            if 'id' in self.__dict__:
                return ' id="{}"'.format(self.__dict__[name])   # format and return it
            else:
                return ''
        
        return super().__getattribute__(name)
    
    def __setattr__(self, name, value):
        if '__' in name:
            super().__setattr__(name, value)
            return
        
        if name not in self.__permittedAttributes:
            raise AttributeError('Attribute {} not supported by object {}'.format(name, self.__class__.__name__))
        
        if name not in attributeTypes:
            raise RuntimeError('Type for attribute {} not defined'.format(name))

        # Check if value is already of the correct type
        if type(value) is attributeTypes[name]:
            super().__setattr__(name, value)
            logger.debug('Attribute {} of type {} appended to {}'.format(name, type(value).__name__, self.__class__.__name__))                          
            if hasattr(value, 'depth'):
                value.depth = self.__depth + 1
            return

        # See if the attribute expects an Enum
        if Enum in getmro(attributeTypes[name]):
            logger.debug('Attribute type of Enum')
            if number.isInt(value):
                super().__setattr__(name, attributeTypes[name](int(value)))    # Set Enum by integer value                        
            else: 
                super().__setattr__(name, attributeTypes[name](value))         # Set the enum by name
            return
        
        # if we make it this far, then create a new instance using value as an init argument
        tmpobj = attributeTypes[name](value)
        if hasattr(tmpobj, 'depth'):
            tmpobj.depth = self.__depth + 1
        super().__setattr__(name, tmpobj)                                 # Create an instance of the type passing the value to the init
    
    def __str__(self):
        tmp = ''
        for a in self.__permittedAttributes:        # Cycle through the attributes in order
            if a == 'id': continue
            if a in self.__dict__:
                if self.__dict__[a] is not None:
                    if KMLObject in getmro(self.__dict__[a].__class__):              # Output the attribute if it has been set
                        # Objects handle their own code formatting and indentation
                        tmp += str(self.__dict__[a])
                    else:
                        # Simple attributes and be easily formatted
                        # All enums should know how to return the proper value when requested.  See the __str__() of the respective enum.
                        tmp += self.indent + ' <{}>{}</{}>\n'.format(a,self.__dict__[a],a)
        return tmp

class KMLFeature(KMLObject):
    def __init__(self):
        super().__init__(['name', 'description', 'visibility', 'open', 'atom_link', 'atom_author', 'address', 'xal_AddressDetails', 'phoneNumber', 'Snippet', 'time'])
    
    def __str__(self):
        return super().__str__()

class ATOMLink(KMLObject):
    # atom:link is a special case.  It has the link value inside the tag.  No other attributes permitted
    def __init__(self, value):
        super().__init__(['link'])
        self.link = value
    
    def __str__(self):
        return self.indent + '<atom:link href="{}" />\n'.format(self.link)
    
class ATOMAuthor(KMLObject):
    def __init__(self, name):
        super().__init__(['name'])
        self.name = name
    
    def __str__(self):
        tmp = self.indent + '<atom:author>\n'
        tmp += super().__str__()
        tmp += self.indent + '</atom:author>\n'
        return tmp

class XALAddress(KMLObject):
    def __init__(self, address):
        super().__init__(['adress'])
        self.address = address
    
    def __str__(self):
        return self.indent + '<xal:AddressDetails>{}</xal:AddressDetails>\n'.format(self.address)

class Snippet(KMLObject):
    def __init__(self, value, maxLines = None):
        super().__init__(['details','maxLines'])
        self.maxLines = maxLines
        self.details = value
    
    def __str__(self):
        tmp = self.indent + '<Snippet'
        if self.maxLines is not None:
            tmp += ' maxLines="{}"'.format(self.maxLines)
        tmp += '>{}</Snippet>\n'.format(self.details)
        return tmp
        
class TimePrimitive(KMLObject):
    """
    Abstract class that returns a TimeStamp or TimeSpan object depending on the number of values given.
    
    If one value is given, a TimeStamp object is returned.
    If two (or more) values are given, a TimeSpan object is returned.  The first value will be 'begin' and
    the second value will be 'end'
    
    Options can be passed as a string (for one option), list or tuple (for two or more)
    
    Only the first two values will be used.  Any other values in the list or tuple will be ignored.
    
    All values must be valid DateTime values.
    
    Usage:
    
        x = TimePrimitive('2006')             # returns TimeStamp with <when> = '2006'
        x = TimePrimitive(['2006','2007'])    # returns TimeSpan with <begin> = '2006' and <end> = '2007'
        x = TimePrimitive(['2006',None])      # returns TimeSpan with <begin> = '2006' and no <end>
    
        f = KMLFeature()
        f.time = '2006'                       # f.time is TimeStamp with <when> = '2006'
        f.time = '2006', '2007'               # f.time is TimeSpan with <begin> = '2006' and <end> = '2007'
    """
    def __new__(self, arg):
        if type(arg) in [TimeSpan,TimeStamp]:
            return arg
        if type(arg) is str:
            return TimeStamp(arg)
        if type(arg) is list:
            arg = tuple(arg)
        if len(arg) == 1:
            return TimeStamp(arg[0])
        if len(arg) >= 2:
            return TimeSpan(arg[0], arg[1])

class TimeStamp(KMLObject):
    def __init__(self, value = None):
        super().__init__(['when'])
        if value is not None:
            self.when = value
    
    def __str__(self):
        tmp = self.indent + '<TimeStamp{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</TimeStamp>\n'
        return tmp

class TimeSpan(KMLObject):
    def __init__(self, begin = None, end = None):
        super().__init__(['begin', 'end'])
        if begin is not None:
            self.begin = begin
        if end is not None:
            self.end = end
    
    def __str__(self):
        tmp = self.indent + '<TimeSpan{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</TimeSpan>\n'
        return tmp

class Coordinate(KMLObject):
    def __init__(self, lon = None, lat = None, alt = None):
        super().__init__(['longitude', 'latitude', 'altitude'])
        self.longitude = lon
        self.latitude = lat
        if alt is not None:
            self.altitude = alt

    def __str__(self):
        if hasattr(self, 'altitude'):
            return '{},{},{}'.format(self.longitude, self.latitude, self.altitude)
        else:
            return '{},{}'.format(self.longitude, self.latitude)

class Container(KMLObject, deque):
    def __init__(self, attributes, types):
        # Add the class attributes we need for the deque object
        super().__init__(attributes + ['append','appendleft','clear','count','insert','pop','popleft',
                                       'reverse','rotate'])
        self.__validTypes = types
        
    def append(self, value):
        if type(value) not in self.__validTypes:
            raise TypeError('Type {} invalid for container {}'.format(value.__class__.__name__, self.__class__.__name__))
        value.depth = self.depth + 1
        super().append(value)

    def appendleft(self, value):
        if type(value) not in self.__validTypes:
            raise TypeError('Type {} invalid for container {}'.format(value.__class__.__name__, self.__class__.__name__))
        value.depth = self.depth + 1
        super().appendleft(value)

    def insert(self, index, value):
        if type(value) not in self.__validTypes:
            raise TypeError('Type {} invalid for container {}'.format(value.__class__.__name__, self.__class__.__name__))
        value.depth = self.depth + 1
        super().insert(index, value)
        
class Coordinates(Container):
    def __init__(self):
        super().__init__([],[Coordinate])
    
    # Coordinates container will only accept coordinate objects, so override append, appendleft and insert to check data types
    
    def __str__(self):
        if len(self) == 0: return ''
        tmp = '<coordinates>'
        if len(self) == 1:
            tmp += str(self[0]) + '</coordinates>\n'
        else:
            tmp += '\n'
            for c in range(len(self)):
                tmp += self.indent + ' ' + str(self[c]) + '\n'
            tmp += self.indent + '</coordinates>\n'
        return tmp

class GXViewerOptions(KMLObject):
    def __init__(self):
        super().__init__(['gx_optionName','enabled'])
    
    def __str__(self):
        tmp = '<gx:ViewerOptions>\n'
        
        



















attributeTypes = {
    # Attribute name        : Data type
    'id'                    : str,
    'depth'                 : int,
    'latitude'              : angle90,
    'longitude'             : angle180,
    'altitude'              : number,
    'visibility'            : booleanEnum,
    'name'                  : str,
    'description'           : str,
    'open'                  : booleanEnum,
    'atom_link'             : ATOMLink,
    'link'                  : str,
    'atom_author'           : ATOMAuthor,
    'address'               : str,
    'xal_AddressDetails'    : str,
    'phoneNumber'           : str,
    'Snippet'               : Snippet,
    'maxLines'              : number,
    #'View'                  : KMLView,
    'begin'                 : KMLDateTime,
    'end'                   : KMLDateTime,
    'when'                  : KMLDateTime,
    'time'                  : TimePrimitive,
    'viewerOptions'         : GXViewerOptions,
    'gx_optionName'         : viewerOptionEnum,
    'enabled'               : booleanEnum,
}
