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
    Subclass of the float data type.
    
    Performs validation on assignment.  Accepts Float and Int.
    
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
    Represents a single color attribute.
    
    Syntax:
    
        x = colorAttribute(value)
    
    Args:
    
        value           : (int or hex) Integer value between 0 and 255
                                       HEX value between '00' and 'FF'

    Errors:
    
        TypeError       : value is not int or str
        ValueError      : value is below 0 or above 255
        ValueError      : Invalid literal
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
    Represents a percentage value between 0.0 and 1.0

    Syntax:
    
        x = NumberPercent(value)
    
    Args:
    
        value           : (float) Float value between 0.0 and 1.0
    
    Errors:
    
        ValueError      : value is below 0.0 or above 1.0
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
    Represents an angle from -90.0 and below 90.0.
    
    Syntax:
    
        x = angle90(value)
    
    Args:
    
        value           : (float) Float value from -90.0 and below 90.0

    Errors:
    
        TypeError       : value is not int or float
        ValueError      : value is below -90.0 or not below 90.0
    """
    def __init__(self, value):
        if not (-90.0 <= value < 90.0):
            raise ValueError('Value out of range')

class anglepos90(number):
    """
    Represents an angle from 0.0 and 90.0.
    
    Syntax:
    
        x = anglepos90(value)
    
    Args:
    
        value           : (float) Float value from 0.0 and 90.0

    Errors:
    
        TypeError       : value is not int or float
        ValueError      : value is below 0.0 or above 90.0
    """
    def __init__(self, value):
        if not (0.0 <= value <= 90.0):
            raise ValueError('Value out of range')

class angle180(number):
    """
    Represents an angle from -180.0 and below 180.0.
    
    Syntax:
    
        x = angle180(value)
    
    Args:
    
        value           : (float) Float value from -180.0 and below 180.0

    Errors:
    
        TypeError       : value is not int or float
        ValueError      : value is below -180.0 or not below 180.0
    """
    def __init__(self, value):
        if not (-180.0 <= value < 180.0):
            raise ValueError('Value out of range')

class angle360(number):
    """
    Represents an angle from 0.0 and below 360.0.
    
    Syntax:
    
        x = angle360(value)
    
    Args:
    
        value           : (float) Float value from 0.0 and below 360.0

    Errors:
    
        TypeError       : value is not int or float
        ValueError      : value is below 0.0 or not below 360.0
    """
    def __init__(self, value):
        if not (0.0 <= value < 360.0):
            raise ValueError('Value out of range')

class Color(object):
    """
    Represents a color as a complete attribute with alpha, red, green and blue.
    
    Color attribute can be expressed as an 8 byte value in the format of aabbggrr:
    
        aa = Alpha
        bb = Blue
        gg = Green
        rr = Red

    Syntax:
    
        x = Color('FF0000FF')                # gives RED
        x = Color(255, 0, 0, 255')           # gives RED
        x = Color('FF', '00', '00', 'FF')    # gives RED
    
    Color can also be expressed as four integer or hex values, in the order of a, b, g, r:
    
    All attributes can be modified using decimal values or hex strings.
    
        x.red = 255
        x.green = 'A0'
        x.alpha = '80'
    
    Errors:
    
        RuntimeError    : Incorrect number of arguments
        ValueError      : Incorrect length of string color argument
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
    
    #def __str__(self):
        
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
    
    def __bool__(self):
        if self.value == 1: return True
        return False

class colorModeEnum(Enum):
    normal = 0
    random = 1
    
    def __str__(self):
        return self.name

class displayModeEnum(Enum):
    default = 0
    hide = 1
    
    def __str__(self):
        return self.name

class hotspotUnitsEnum(Enum):
    fraction = 0
    pixels = 1
    insetPixels = 2
    
    def __str__(self):
        return self.name

class styleMapEnum(Enum):
    normal = 0
    highlighted = 1
    
    def __str__(self):
        return self.name

class listItemTypeEnum(Enum):
    check = 0
    checkOffOnly = 1
    checkHiddenChildren = 2
    radioFolder = 3
    
    def __str__(self):
        return self.name

class itemIconModeEnum(Enum):
    open = 0
    closed = 1
    error = 2
    fetching0 = 3
    fetching1 = 4
    fetching2 = 5
    
    def __str__(self):
        return self.name

class viewerOptionEnum(Enum):
    streetview = 0
    historicalimagery = 1
    sunlight = 2
    
    def __str__(self):
        return self.name

class refreshModeEnum(Enum):
    onChange = 0
    onInterval = 1
    onExpire = 2
    
    def __str__(self):
        return self.name

class schemaTypeEnum(Enum):
    string = 0
    float = 1
    int = 2
    double = 3
    uint = 4
    short = 5
    bool = 6
    str = 0
    booleanEnum = 6
    
    def __str__(self):
        return self.name

################################################################################################
#                                                                                              #
#   KML Abstract Object definitions (base classes)                                             #
#                                                                                              #
################################################################################################

class KMLObject(object):

    def __init__(self, permittedAttributes):
        self.__depth = 0
        self.__permittedAttributes = ['id','depth','indent','_set_depth'] + permittedAttributes
        logging.debug('{} created'.format(self.__class__.__name__))
    
    @property
    def indent(self):
        return ' ' * self.__depth

    @property    
    def depth(self, value = None):
        return self.__depth
    
    @depth.setter
    def depth(self, value):
        self._set_depth(value)
    
    def _set_depth(self, value):
        self.__depth = value
        for a in self.__dict__:
            if hasattr(self.__dict__[a], 'depth'):
                setattr(self.__dict__[a], 'depth', self.__depth + 1)

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
            logger.debug('Attribute {} of type {} with value {} appended to {}'.format(name, type(value).__name__,value,  self.__class__.__name__))                          
            if hasattr(value, 'depth'):
                value.depth = self.__depth + 1
            return
        
        # See if the attribute expects an Enum
        if Enum in getmro(attributeTypes[name]):
            logger.debug('Attribute {} of type {} appended to {}'.format(name, type(attributeTypes[name]).__name__, self.__class__.__name__))                          
            if number.isInt(value):
                super().__setattr__(name, attributeTypes[name](int(value)))    # Set Enum by integer value                        
            else: 
                super().__setattr__(name, attributeTypes[name][value])         # Set the enum by name
            return
        
        # Check if we have an object of the wrong type
        #if type(value) not in [str, int, float]:
        #    if KMLObject in getmro(value.__class__):
        #        raise TypeError('Attribute {} must be of type {}, not {}'.format(name, attributeTypes[name].__name__, type(value).__name__))
        
        # if we make it this far, then create a new instance using value as an init argument
        tmpobj = attributeTypes[name](value)
        logger.debug('Attribute {} of type {} appended to {}'.format(name, tmpobj.__class__.__name__, self.__class__.__name__))                          
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
                        if a[:3] == 'gx_':
                            tmp += self.indent + ' <{}>{}</{}>\n'.format(a.replace('_',':'),self.__dict__[a],a.replace('_',':'))
                        else:
                            tmp += self.indent + ' <{}>{}</{}>\n'.format(a,self.__dict__[a],a)
        return tmp

class altitudeMode(KMLObject):
    def __init__(self, value):
        super().__init__(['altitudeModeEnum'])
        self.altitudeModeEnum = altitudeModeEnum[value]
    
    def __str__(self):
        if self.altitudeModeEnum.value < 3:
            return self.indent + '<altitudeMode>{}</altitudeMode>\n'.format(self.altitudeModeEnum.name)
        else:
            return self.indent + '<gx:altitudeMode>{}</gx:altitudeMode>\n'.format(self.altitudeModeEnum.name)
        
class KMLFeature(KMLObject):
    def __init__(self, *args):
        self.__permittedAttributes = ['name', 'description', 'visibility', 'open', 'atom_link', 
                                      'atom_author', 'address', 'xal_AddressDetails', 'phoneNumber',
                                      'Snippet', 'time', 'view', 'styleUrl', 'styleSelector',
                                      'Region', 'Metadata', 'ExtendedData']

        super().__init__(self.__permittedAttributes)
        
        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a], args[a])
                
    
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
        super().__init__(['text','maxLines'])
        self.maxLines = maxLines
        self.text = value
    
    def __str__(self):
        tmp = self.indent + '<Snippet'
        if self.maxLines is not None:
            tmp += ' maxLines="{}"'.format(self.maxLines)
        tmp += '>{}</Snippet>\n'.format(self.text)
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
    def __init__(self, value):
        super().__init__(['when'])
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
    """
    Coordinate object.
    
    Syntax:
    
        x = Coordinate(lon, lat, [alt])
    
    Args:
    
        lon             : (angle180) Longitude
        lat             : (angle90) Latitude
        alt             : (number) Altitude (optional)
        
    """
    def __init__(self, lon, lat, alt = None):
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

    def __eq__(self, x):
        if type(x) != type(self):         return False
        if self.latitude != x.latitude:   return FalSe
        if self.longitude != x.longitude: return FalSe
        if hasattr(self, 'altitude') and hasattr(x, 'altitude'):
            if self.altitude != x.altitude : return False
        return True
           
class Container(KMLObject, deque):
    """
    Creates a collection of objects.
    
    Usage:
    
        x = Container(attributes, types, [unique])
        
    Args:
    
        attributes      : (list) List of additional attributes permitted on this object
        types           : (list) List of data types permitted in this collection.
                                 Parse an empty list for no restrictions.
        unique          : (bool) Control if duplicate objects are permitted.
                                 Objects are compared via == (__eq__) method.
                                 Optional - default is False (duplicates permitted)
    """
    
    def __init__(self, attributes, types, unique = False):
        # Add the class attributes we need for the deque object
        super().__init__(attributes + ['append', 'appendleft', 'clear', 'count', 'index',
                                       'insert', 'pop', 'popleft', 'reverse', 'rotate'])
        # List of data types permitted in this collection
        self.__restrictTypes = False
        if len(types) > 0:
            self.__validTypes = types
            self.__restrictTypes = True
        # Flag to permit duplicate entries.  Objects should override __eq__ to control comparison between objects
        self.__unique = unique
    
    def _set_depth(self, value):
        super()._set_depth(value)
        for a in range(len(self)):
            self[a].depth = self.depth + 1
    
    def append(self, value):
        if self.__restrictTypes:
            if type(value) not in self.__validTypes:
                raise TypeError('Type {} invalid for container {}'.format(value.__class__.__name__, self.__class__.__name__))
        if self.__unique:
            for i in range(len(self)):
                if value == self[i]:
                    raise ValueError('Cannot duplicate {} when container {} unique is True'.format(value.__class__.__name__, self.__class__.__name__))
        value.depth = self.depth + 1
        super().append(value)

    def appendleft(self, value):
        if self.__restrictTypes:
            if type(value) not in self.__validTypes:
                raise TypeError('Type {} invalid for container {}'.format(value.__class__.__name__, self.__class__.__name__))
        if self.__unique:
            for i in range(len(self)):
                if value == self[i]:
                    raise ValueError('Cannot duplicate {} when container {} unique is True'.format(value.__class__.__name__, self.__class__.__name__))
        value.depth = self.depth + 1
        super().appendleft(value)

    def insert(self, index, value):
        if self.__restrictTypes:
            if type(value) not in self.__validTypes:
                raise TypeError('Type {} invalid for container {}'.format(value.__class__.__name__, self.__class__.__name__))
        if self.__unique:
            for i in range(len(self)):
                if value == self[i]:
                    raise ValueError('Cannot duplicate {} when container {} unique is True'.format(value.__class__.__name__, self.__class__.__name__))
        value.depth = self.depth + 1
        super().insert(index, value)
    
    def __str__(self):
        tmp = ''
        tmp += super().__str__()
        for i in range(len(self)):
            tmp += str(self[i])
        return tmp

class Coordinates(Container):
    def __init__(self):
        super().__init__([],[Coordinate])
    
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

class GXViewerOption(KMLObject):
    """
    Represents a singe gx:ViewerOptions choice entry
    
    Syntax:
    
        x = GXViewerOption(name, enabled)
    
    Args:
    
        name            : (viewerOptionEnum) Option name
        enabled         : (boolEnum) Enabled (optional) default 1
    
    Comparing GXViewerOption will only compare by name, not value. 
    """ 
    def __init__(self, name, value = 1):
        super().__init__(['gx_optionName','enabled'])
        self.gx_optionName = name
        self.enabled = value
    
    def __str__(self):
        return self.indent + '<gx:option name="{}" enabled={}/>\n'.format(self.gx_optionName, self.enabled)
    
    def __eq__(self, x):
        if type(x) is str:
            return self.gx_optionName == x
        else:
            return self.gx_optionName == x.gx_optionName
        
class GXViewerOptions(Container):
    """
    Collection of GXViewerOption objects
    
    Syntax:
    
        x = GXViewerOptions()
        x.append(GXViewerOption(...))
    """
    def __init__(self):
        super().__init__(['seek'], [GXViewerOption], True)

    def __str__(self):
        tmp = self.indent + '<gx:ViewerOptions>\n'
        tmp += super().__str__()
        tmp += self.indent + '</gx:ViewerOptions>\n'
        return tmp

    def seek(self, item):
        """
        returns reference to a GXViewerOption object by name
        
        Syntax:
        
            x = GXViewerOptions()
            x.seek('streetview')
        
        Can be used to modify attributes:

            x.seek('streetview').enabled = 'yes'
        """
        try:
            return self[self.index(GXViewerOption(item))]
        except ValueError:
            raise ValueError('GXViewerOption {} not found in GXViewerOptions'.format(item))
            
class Camera(KMLObject):
    def __init__(self):
        self.__permittedAttributes = ['longitude', 'latitude', 'altitude', 'heading', 'tilt',
                                      'roll', 'altitudeMode','time','viewerOptions', ]

        super().__init__(self.__permittedAttributes)
        self.viewerOptions = GXViewerOptions()
        
        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a], args[a])
                
    def __str__(self):
        tmp = self.indent + '<Camera{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</Camera{}>\n'.format(self.id)
        return tmp
                
class LookAt(KMLObject):
    def __init__(self):
        self.__permittedAttributes = ['longitude', 'latitude', 'altitude', 'heading', 'tilt',
                                      'range', 'altitudeMode', 'time','viewerOptions']
        super().__init__(self.__permittedAttributes)
        self.viewerOptions = GXViewerOptions()
        
        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a], args[a])
                
    def __str__(self):
        tmp = self.indent + '<LookAt{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</LookAt{}>\n'.format(self.id)
        return tmp
        
class KMLView(KMLObject):
    def __new__(self, viewertype):
        if type(viewertype) is str:
            if viewertype.lower() == 'camera': return Camera()
            if viewertype.lower() == 'lookat': return LookAt()
        logger.debug(getmro(viewertype.__class__))
        if Camera in getmro(viewertype.__class__): return viewertype
        if LookAt in getmro(viewertype.__class__): return viewertype
        raise TypeError('View object must be Camera or LookAt, not {}'.format(viewertype))

class Icon(KMLObject):
    def __init__(self, href, *args):
        self.__permittedAttributes = ['href', 'gx_x', 'gx_y', 'gx_w', 'gx_h',
                                      'refreshMode', 'refreshInterval',
                                      'viewBoundScale', 'viewFormat',
                                      'httpQuery'] 

        super().__init__(self.__permittedAttributes)
        self.href = href
        
        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a + 1], args[a])
                
    def __str__(self):
        tmp = self.indent + '<Icon{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</Icon>\n'
        return tmp

class HotSpot(KMLObject):
    def __init__(self, x, y, xunits, yunits):
        super().__init__(['x', 'y', 'xunits', 'yunits'])
        self.x = x
        self.y = y
        self.xunits = xunits
        self.yunits = yunits
        
    def __str__(self):
        return self.indent + '<hotSpot x="{}" y="{}" xunits="{}" yunits="{}"/>\n'.format(self.x, self.y, self.xunits, self.yunits)
 
class IconStyle(KMLObject):
    def __init__(self, *args):
        
        self.__permittedAttributes = ['color', 'colorMode', 'scale', 'heading', 'icon', 'hotSpot']
        super().__init__(self.__permittedAttributes)
        
        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a], args[a])
                

    def __str__(self):
        tmp = self.indent + '<IconStyle{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</IconStyle>\n'
        return tmp

class LabelStyle(KMLObject):
    def __init__(self, *args):
        
        self.__permittedAttributes = ['color', 'colorMode', 'scale']
        super().__init__(self.__permittedAttributes)
        
        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a], args[a])
                

    def __str__(self):
        tmp = self.indent + '<LabelStyle{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</LabelStyle>\n'
        return tmp

class LineStyle(KMLObject):
    def __init__(self, *args):
        
        self.__permittedAttributes = ['color', 'colorMode', 'width', 'gx_outerColor', 'gx_outerWidth',
                                      'gx_physicalWidth', 'gx_labelVisibility']
        super().__init__(self.__permittedAttributes)
        
        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a], args[a])
                

    def __str__(self):
        tmp = self.indent + '<LineStyle{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</LineStyle>\n'
        return tmp

class PolyStyle(KMLObject):
    def __init__(self, *args):
        
        self.__permittedAttributes = ['color', 'colorMode', 'fill', 'outline']
        super().__init__(self.__permittedAttributes)
        
        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a], args[a])
                

    def __str__(self):
        tmp = self.indent + '<PolyStyle{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</PolyStyle>\n'
        return tmp

class BalloonStyle(KMLObject):
    def __init__(self, *args):
        
        self.__permittedAttributes = ['bgColor', 'textColor', 'text', 'displayMode']
        super().__init__(self.__permittedAttributes)
        
        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a], args[a])
                

    def __str__(self):
        tmp = self.indent + '<BalloonStyle{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</BalloonStyle>\n'
        return tmp

class ItemIcon(KMLObject):
    def __init__(self, state, href):
        super().__init__(['state', 'href'])
        self.state = state
        self.href = href
    
    def __str__(self):
        tmp = self.indent + '<ItemIcon>\n'
        tmp += super().__str__()
        tmp += self.indent + '</ItemIcon>\n'
        return tmp
    
    def __eq__(self, x):
        if type(x) is str:
            return self.state == x
        else:
            return self.state == x.state

class ListStyle(Container):
    def __init__(self, listItemType = None, bgColor = None):
        super().__init__(['listItemType', 'bgColor'],[ItemIcon], True)
        if listItemType is not None: self.listItemType = listItemType
        if bgColor is not None: self.bgColor = bgColor
        
    def __str__(self):
        if len(self) == 0: return ''
        tmp = self.indent + '<ListStyle{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</ListStyle>\n'
        return tmp
    
    def append(self, *args):
        if len(args) > 1:
            tmp = ItemIcon(args[0], args[1])
        super().append(tmp)

class Style(KMLObject):
    def __init__(self, *args):
        self.__permittedAttributes = ['IconStyle', 'LabelStyle', 'LineStyle',
                                      'PolyStyle', 'BalloonStyle', 'ListStyle']

        super().__init__(self.__permittedAttributes)
        self.ListStyle = ListStyle()
        
        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a], args[a])
                
def __str__(self):
        tmp = self.indent + '<Style{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</Style>\n'
        return tmp
    
class StyleMapPair(KMLObject):
    """
    Represents a singe StyleMap Key Value pair
    
    Syntax:
    
        x = StyleMapPair(key, styleUrl)
    
    Args:
    
        key             : (viewerOptionEnum) Option name
        styleUrl        : (str) URL to the style
    
    Comparing StyleMapPair will only compare by key, not value. 
    """ 
    def __init__(self, key, styleUrl = ''):
        super().__init__(['key','styleUrl'])
        self.key = key
        self.styleUrl = styleUrl
        
    def __str__(self):
        tmp = self.indent + '<Pair>\n'
        tmp += super().__str__()
        tmp += self.indent + '</Pair>\n'
        return tmp
    
    def __eq__(self, x):
        if type(x) is str:
            return self.key == x
        else:
            return self.key == x.key

class StyleMap(Container):
    def __init__(self):
        super().__init__([], [StyleMapPair], True)
    
    def __str__(self):
        tmp = self.indent + '<StyleMap{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</StileMap>\n'
        return tmp

    def seek(self, item):
        """
        returns reference to a StyleMapPair object by key
        
        Syntax:
        
            x = StyleMap()
            x.seek('normal')
        
        Can be used to modify attributes:

            x.seek('normal').styleUrl = '#MyStyle'
        """
        try:
            return self[self.index(StyleMapPair(item))]
        except ValueError:
            raise ValueError('StyleMapPair {} not found in StyleMap'.format(item))
            
class StyleSelector(KMLObject):
    def __new__(self, obj):
        if obj.__class__ in [Style, StyleMap]: return obj
        raise TypeError('StyleSelector must be of type Style or StyleMap, not {}'.format(obj.__class__.__name__))

class LatLonAltBox(KMLObject):
    def __init__(self, north, south, east, west, *args):
        self.__permittedAttributes = ['north', 'south', 'east', 'west', 'minAltitude', 'maxAltitude', 'altitudeMode']
        super().__init__(self.__permittedAttributes)

        self.north = north
        self.south = south
        self.east = east
        self.west = west

        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a+4], args[a])

    def __str__(self):
        tmp = self.indent + '<LatLonAltBox>\n'
        tmp += super().__str__()
        tmp += self.indent + '</LatLonAltBox>\n'
        return tmp
    
class Lod(KMLObject):
    def __init__(self, minLodPixels = 256, maxLodPixels = -1, minFadeExtent = 0, maxFadeExtent = 0):
        super().__init__(['minLodPixels', 'maxLodPixels', 'minFadeExtent', 'maxFadeExtent'])
        self.minLodPixels = minLodPixels
        self.maxLodPixels = maxLodPixels
        self.minFadeExtent = minFadeExtent
        self.maxFadeExtent = maxFadeExtent
    
    def __str__(self):
        tmp = self.indent + '<Lod>\n'
        tmp += super().__str__()
        tmp += self.indent + '</Lod>\n'
        return tmp
    
class Region(KMLObject):
    def __init__(self, LatLonAltBox = None, Lod = None):
        super().__init__(['LatLonAltBox', 'Lod'])
        if LatLonAltBox is not None:    self.LatLonAltBox = LatLonAltBox
        if Lod is not None:             self.Lod = Lod
        
    def __str__(self):
        tmp = self.indent + '<Region{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</Region>\n'
        return tmp

class SimpleField(KMLObject):
    def __init__(self, name, t, displayName = None):
        self.__permittedAttributes = ['name', 'type', 'displayName']
        super().__init__(self.__permittedAttributes)

        self.name = name
        self.type = t
        if displayName is not None: self.displayName = displayName
    
    def __str__(self):
        tmp = self.indent + '<SimpleField type="{}" name="{}">\n'.format(self.type, self.name)
        if self.displayName is not None:
            tmp += self.indent + ' <displayName>{}</displayName>\n'.format(self.displayName)
        tmp += self.indent + '</SimpleField>\n'
        return tmp

class Schema(Container):
    def __init__(self, name, id):
        super().__init__(['name'], [SimpleField], True)
        self.name = name
        self.id = id
        
    def __str__(self):
        tmp = self.indent + '<Schema name="{}"{}>\n'.format(self.name, self.id)
        tmp += super().__str__()
        tmp += self.indent + '</Schema>\n'
        return tmp
        



############################################################################
#
# Template class
#
############################################################################

class Template(KMLObject):
    def __init__(self, req_args, *args):
        self.__req_args = 1
        self.__permittedAttributes = ['north', 'south', 'east', 'west', 'minAltitude', 'maxAltitude', 'altitudeMode']
        super().__init__(self.__permittedAttributes)

        self.reg_arg = req_args

        for a in range(len(args)):
            if args[a] is not None:
                setattr(self, self.__permittedAttributes[a + self.__req_args], args[a])

    def __str__(self):
        tmp = self.indent + '<Template{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + '</Template>\n'
        return tmp
    







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
    'view'                  : KMLView,
    'begin'                 : KMLDateTime,
    'end'                   : KMLDateTime,
    'when'                  : KMLDateTime,
    'time'                  : TimePrimitive,
    'viewerOptions'         : GXViewerOptions,
    'gx_optionName'         : viewerOptionEnum,
    'enabled'               : booleanEnum,
    'heading'               : angle360,
    'tilt'                  : angle180,
    'roll'                  : angle180,
    'altitudeMode'          : altitudeMode,
    'altitudeModeEnum'      : altitudeModeEnum,
    'range'                 : number,
    'styleUrl'              : str,
    'color'                 : Color,
    'colorMode'             : colorModeEnum,
    'href'                  : str,
    'icon'                  : Icon,
    'x'                     : number,
    'y'                     : number,
    'xunits'                : hotspotUnitsEnum,
    'yunits'                : hotspotUnitsEnum,
    'hotSpot'               : HotSpot,
    'scale'                 : number,
    'key'                   : styleMapEnum,
    'width'                 : number,
    'gx_outerColor'         : Color,
    'gx_outerWidth'         : number,
    'gx_physicalWidth'      : number,
    'gx_labelVisibility'    : booleanEnum,
    'fill'                  : booleanEnum,
    'outline'               : booleanEnum,
    'bgColor'               : Color,
    'textColor'             : Color,
    'text'                  : str,
    'displayMode'           : displayModeEnum,
    'state'                 : itemIconModeEnum,
    'listItemType'          : listItemTypeEnum,
    'IconStyle'             : IconStyle,
    'LabelStyle'            : LabelStyle,
    'LineStyle'             : LineStyle,
    'PolyStyle'             : PolyStyle,
    'BalloonStyle'          : BalloonStyle,
    'ListStyle'             : ListStyle,
    'styleSelector'         : StyleSelector,
    'LatLonAltBox'          : LatLonAltBox,
    'Lod'                   : Lod,
    'north'                 : angle90,
    'south'                 : angle90,
    'east'                  : angle180,
    'west'                  : angle180,
    'minAltitude'           : number,
    'maxAltitude'           : number,
    'minLodPixels'          : number,
    'maxLodPixels'          : number,
    'minFadeExtent'         : number,
    'maxFadeExtent'         : number,
    'Region'                : Region,
    'Lod'                   : Lod,
    'gx_x'                  : int,
    'gx_y'                  : int,
    'gx_h'                  : int,
    'gx_w'                  : int,
    'refreshMode'           : refreshModeEnum,
    'refreshInterval'       : number,
    'viewBoundScale'        : number,
    'viewFormat'            : str,
    'httpQuery'             : str,
    'type'                  : schemaTypeEnum,
    'displayName'           : str,
    
    
}
