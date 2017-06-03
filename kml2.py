import logging
logger = logging.getLogger()
# Remove after testing
f = logging.Formatter('%(levelname)-8s:%(funcName)-20s %(lineno)-5s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(f)
logger.addHandler(h)
logger.setLevel(logging.DEBUG)

from datetime import datetime


################################################################################################
#                                                                                              #
#   KML Data Type definitions                                                                  #
#                                                                                              #
################################################################################################

class number(float):
    def __new__(self, value):
        if type(value) not in [float, int]:
            raise TypeError('Value must be a number, not {}'.format(type(value)))
        return float.__new__(self, value)

    def isInt(value):
        try:
            int(str(value))
            return True
        except ValueError:
            return False

    def isFloat(self, value):
        try:
            float(str(value))
            return True
        except ValueError:
            return False

class angle90(number):
    def __init__(self, value):
        if not (-90.0 <= value < 90.0):
            raise ValueError('Value out of range')


class angle180(number):
    def __init__(self, value):
        if not (-180.0 <= value < 180.0):
            raise ValueError('Value out of range')


class angle360(number):
    def __init__(self, value):
        if not (0.0 <= value < 360.0):
            raise ValueError('Value out of range')

class boolean(int):
    # ANY value that is not 0 or boolean False is concidered True
    def __new__(self, value):
        if str(value) == '0' or str(value) == 'False':
            return int.__new__(self, 0)
        else:
            return int.__new__(self, 1)

    def __bool__(self):
        if self == 0:
            return False
        return True

################################################################################################
#                                                                                              #
#   KML Abstract Object definitions (base classes)                                             #
#                                                                                              #
################################################################################################

class KMLObject(object):
    # Base class for primitive KML Object.  Creates and manages the parent and depth properties
    # Introduces the ID attribute
    def __init__(self, **kwargs):
        logging.debug('KMLObject created')
        self.depth = 0
        self.__parent = None
        self.__id = None
        self.set(**kwargs)

    def set(self, **kwargs):
        for k in kwargs:
            if hasattr(self, k):
                setattr(self, k, kwargs[k])
            else:
                pass
                #raise AttributeError('Invalid attribute {}'.format(k)

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent):
        self._set_parent(parent)

    @property
    def id(self):
        if self.__id is None:
            return ''
        else:
            return ' id="{}"'.format(self.__id)

    @id.setter
    def id(self, id):
        self.__id = id

    def _set_parent(self, parent):
        if parent is not None:
            self.__parent = parent
            self.depth = parent.depth + 1
            if hasattr(parent, 'append'):
                parent.append(self)
            logging.debug('KMLObject parent property set')
        else:
            if self.__parent is not None:
                if hasattr(parent, 'remove'):
                    logging.debug('KMLObject removing self from parent collection')
                    self.__parent.remove(self)
            self.__parent = None
            logging.debug('KMLObject parent property unset')
            self.depth = 0

    @property
    def indent(self):
        return ' ' * self.depth

class KMLContainer(KMLObject):

    # Base class for primitive Container objects.  Manages a list (collection) of child objects.
    # Overrides the parent and depth properties.

    def __init__(self, **kwargs):
        self.__elements = []
        self.__depth = 0
        super().__init__(**kwargs)
        logging.debug('KMLContainer created')

    def __str__(self):
        logging.debug('KMLContainer outputting child kml elements')
        tmp = ''
        for e in self.__elements:
            tmp += self.indent + str(e)
        return tmp

    @KMLObject.parent.setter
    def parent(self, parent):
        super()._set_parent(parent)
        # in addition, update the depth on all child elements
        logging.debug('KMLContainer updating child depths')
        for child in self.__elements:
            child.depth = self.depth + 1

    @property
    def depth(self):
        # Depth property is redefined in a container object to facilitate cascading of depth property to child elements
        return self.__depth

    @depth.setter
    def depth(self, d):
        # Depth property is redefined in a container object to facilitate cascading of depth property to child elements
        self.__depth = d
        logging.debug('KMLContainer updating child depths')
        for child in self.__elements:
            child.depth = self.__depth + 1

    def remove(self, item):
        logging.debug('KMLContainer removing {} from collection'.format(str(item)))
        self.__elements.remove(item)

    def append(self, item):
        #if type(item) is Document: TODO: Uncomment this later
        #    raise TypeError('Document objects cannot be child objects')
        if item is not None:
            if item.parent is not self:  # Stop recursive calls
                item.parent = self
            if item not in self.__elements:
                self.__elements.append(item)
                logging.debug('KMLContainer adding {} to collection'.format(item.__class__.__name__))

    def insert(self, position, item):
        if item is not None:
            if item.parent is not self:
                item.parent = self                     # This triggers an append
                self.__elements.remove(item)           # Remove it from the end
                logging.debug('KMLContainer inserting {} to collection at {}'.format(str(item), position))
                self.__elements.insert(position, item) # Insert it where we want it
            if item not in self.__elements:
                logging.debug('KMLContainer inserting {} to collection at {}'.format(str(item), position))
                self.__elements.insert(position, item)

    def find(self, id):
        # Return reference to an element by id
        # Raises ValueError exception if ID is not found
        for e in self.__elements:
            if e.id == id:
                return e
        raise ValueError('{} is not in elements'.format(id))

#    def replace(self, item):
#        self[self.index(self.find(item))] = item

    def __len__(self):
        return len(self.__elements)

    def __contains__(self, x):
        # Allows the 'in' opperator to be used to check for the existance of an element
        return x in self.__elements

    def __iter__(self):
        # Allows itteration over elements
        for x in self.__elements:
            yield x

    def __getitem__(self, index):
        # Return an element by index
        return self.__elements[index]

    def __setitem__(self, index, item):
        # Set an element by index
        self.__elements[index] = item

    def index(self, item):
        return self.__elements.index(item)

    def pop(self, index = 0):
        # Used to delete an element by index
        if len(self.__elements) > 0:
            self.__elements.pop(index)


class KMLFeature(KMLObject):

    # KML Feature object.
    def __init__(self, **kwargs):
        # parent can be passed in kwargs.  Declare the super with None for the parent for now
        super().__init__(**kwargs)
        self.__name = None
        self.__description = None
        self.__visibility = None
        self.__open = None
        self.__author = None
        self.__link = None
        self.__phoneNumber = None
        self.__addressDetails = None
        self.__address = None
        self.__snippet = None
        self.__view = None
        self.__time = None
        self.__style = None
        self.__styleSelector = None
        self.__region = None
        self.__metadata = None
        self.__extendedData = None

        self.set(**kwargs)
        logging.debug('KMLFeature created')

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if value is not None:
            if type(value) not in [str, int, float]:
                raise ValueError('name must be of type str, int or float, not {}'.format(type(value)))
        self.__name = value

    @property
    def description(self):
        return self.__decription

    @description.setter
    def description(self, value):
        if value is not None:
            if type(value) not in [str]:
                raise ValueError('description must be of type str, not {}'.format(type(value)))
        self.__description = value

    @property
    def visibility(self):
        return self.__visibility

    @visibility.setter
    def visibility(self, value):
        if value is not None:
            if type(value) not in [str, int, float]:
                raise ValueError('Invalid value for visibility {}'.format(repr(value)))
        self.__visibility = boolean(value)

    @property
    def open(self):
        return self.__open

    @open.setter
    def open(self, value):
        if value is not None:
            if type(value) not in [str, int, float]:
                raise ValueError('Invalid value for open {}'.format(repr(value)))
        self.__open = boolean(value)

    @property
    def author(self):
        return self.__author

    @author.setter
    def author(self, value):
        if value is not None:
            if type(value) not in [str]:
                raise ValueError('author must be of type str, not {}'.format(type(value)))
        self.__author = value

    @property
    def link(self):
        return self.__link

    @link.setter
    def link(self, value):
        if value is not None:
            if type(value) not in [str]:
                raise ValueError('link must be of type str, not {}'.format(type(value)))
        self.__link = value

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, value):
        if value is not None:
            if type(value) not in [str]:
                raise ValueError('address must be of type str, not {}'.format(type(value)))
        self.__address = value

    @property
    def phoneNumber(self):
        return self.__phoneNumber

    @phoneNumber.setter
    def phoneNumber(self, value):
        if value is not None:
            if type(value) not in [str]:
                raise ValueError('phoneNumber must be of type str, not {}'.format(type(value)))
        self.__phoneNumber = value

    @property
    def snippet(self):
        return self.__snippet

    @snippet.setter
    def snippet(self, value):
        if value is not None:
            if type(value) not in [Snippet]:
                raise ValueError('snippet must be of type Snippet, not {}'.format(type(value)))
        self.__snippet = value

    @property
    def view(self):
        return self.__view

    @view.setter
    def view(self, value):
        if value is not None:
            if type(value) not in [LookAt, Camera]:
                raise ValueError('view must be of type LookAt or Camera, not {}'.format(type(value)))
        self.__view = value

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, value):
        if value is not None:
            if type(value) not in [TimeStamp, TimeSpan]: # TODO: Write TimeStam and TimeSpan classes
                raise ValueError('time must be of type TimeStamp or TimeSpan, not {}'.format(type(value)))
        self.__time = value

    @property
    def styleSelector(self):
        return self.__styleSelector

    @styleSelector.setter
    def styleSelector(self, value):
        if value is not None:
            if type(value) not in [Style, StyleMap]: # TODO: Write Style, StyleMap, IconStyle,  LabelStyle, LineStyle, PolyStyle, BaloonStyle, ListStyle, ColorStyle
                raise ValueError('styleSelector must be of type IconStyle,  LabelStyle, LineStyle, PolyStyle, BaloonStyle, ListStyle or ColorStyle, not {}'.format(type(value)))
        self.__styleSelector = value

    @property
    def styleURL(self):
        return self.__styleURL

    @styleURL.setter
    def styleURL(self, value):
        if value is not None:
            if type(value) not in [Style, StyleMap]: # TODO: Write Style, StyleMap
                raise ValueError('styleURL must be of type Style or StyleMap, not {}'.format(type(value)))
        self.__styleURL = value

    @property
    def region(self):
        return self.__region

    @region.setter
    def region(self, value):
        if value is not None:
            if type(value) not in [Region]: # TODO: Write Region
                raise ValueError('region must be of type Region, not {}'.format(type(value)))
        self.__region = value

    @property
    def metadata(self):
        return self.__metadata

    @metadata.setter
    def metadata(self, value):
        if value is not None:
            if type(value) not in [Metadata]: # TODO: Write Metadata
                raise ValueError('metadata must be of type MetaData, not {}'.format(type(value)))
        self.__metadata = value

    @property
    def extendedData(self):
        return self.__extendedData

    @extendedData.setter
    def extendedData(self, value):
        if value is not None:
            if type(value) not in [extendedData]: # TODO: Write Style, StyleMap
                raise ValueError('extendedData must be of type ExtendedData, not {}'.format(type(value)))
        self.__extendedData = value




    def __str__(self):
        logging.debug('KMLFeature outputting child kml elements')
        tmp = ''
        # Output any value based attributes
        for a in ['name','description','visibility','open','phoneNumber','address']:
            if getattr(self, a) is not None:
                tmp += self.indent + ' <{}>{}</{}>\n'.format(a, getattr(self, a), a)
        # Output any special case attributes
        if self.link is not None:
            tmp += self.indent + ' <atom:link href="{}" />\n'.format(self.link)
        if self.addressDetails is not None:
            tmp += self.indent + ' <xal:AddressDetails>{}</xal:AddressDetails>\n'.format(a, getattr(self, a), a)
        if self.author is not None:
            tmp += self.indent + ' <atom:author>\n'
            tmp += self.indent + '  <atom:name>{}</atom:name>\n'.format(self.author)
            tmp += self.indent + ' </atom:author>\n'
        # Output any object based attributes
        for a in ['snippet','view','time','styleURL','styleSelector','region','metadata','extendedData']:
            tmp += str(getattr(self, a))
        return tmp

class KMLView(KMLObject):
    # Abstract class for View objects
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__viewer = None
        self.__time = None
        self.set(**kwargs)

    @property
    def viewer(self):
        return self.__viewer

    @viewer.setter
    def viewer(self, value):
        if value is not None:
            if type(value) not in [gx_ViewerOptions]:
                raise TypeError('viewer must be of type gx_ViewerOptions, not {}'.format(type(value)))
            value.parent = self
        self.viewer = view

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, value):
        if value is not None:
            if type(value) not in [TimeStamp, TimeSpan]:
                raise TypeError('Time must be of type TimeSpan or TimeStamp, not {}'.format(type(value)))
            value.parent = self
        self.time = time
        logging.debug('KLMView created')

    def __str__(self):
        tmp = ''
        if self.__viewer is not None:
            tmp += str(self.__view)
        if self.__time is not None:
            tmp += str(self.__time)
        return tmp


################################################################################################
#                                                                                              #
#   KML Object definitions                                                                     #
#                                                                                              #
################################################################################################

class Snippet(KMLObject):
    # Snippet object - Optionally used in any Container object
    # Introduces a maxLines property
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__content= ''
        self.__maxLines = 2
        self.set(**kwargs)
        logging.debug('Snippet created')

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, value):
        if type(value) not in [str, int, float]:
            raise ValueError('Invalid value for content {}'.format(value))
        self.__content = str(value)

    @property
    def maxLines(self):
        return self.__maxLines

    @maxLines.setter
    def maxLines(self, value):
        if type(value) not in [int]:
            raise TypeError('maxLines must be of type int, not {}'.format(type(value)))
        self.__maxLines = value

    def __str__(self):
        return self.indent + '<Snippet maxLines="{}">{}</Snippet>'.format(self.__maxLines, self.__content)


class gx_ViewerOptions(KMLObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__name = 'streetview'
        self.__enabled = boolean(1)
        self.set(**kwargs)
        logging.debug('gx:ViewerOptions created')

        @property
        def name(self):
            return self.__name

        @name.setter
        def name(self, value):
            if value not in ['streetview', 'historicalimagery', 'sunlight', 'groundnavigation']:
                raise ValueError('name must be streetview, historicalimagery, sunlight or  groundnavigation, not {}'.format(value))
            self.__name = value

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled=boolean(value)


    def __str__(self):
        tmp = self.indent + '<gx:ViewerOptions{}>\n'.format(self.id)
        tmp += self.indent + ' <gx:option name="{}" enabled={}/>\n'.format(self.__name, self.__enabled)
        tmp += self.indent + '</gx:ViewerOptions>\n'
        return tmp


class Coords(KMLObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__lat = angle90(0)
        self.__lon = angle180(0)
        self.__alt = None #number(0)
        self.set(**kwargs)
        logging.debug('Coords created')

    @property
    def alt(self):
        return self.__alt

    @alt.setter
    def alt(self, value):
        if value is not None:
            self.__alt = number(value)
        else:
            self.__alt = None

    @property
    def lat(self):
        return self.__lat

    @lat.setter
    def lat(self, value):
        self.__lat = angle90(value)

    @property
    def lon(self):
        return self.__lon

    @lon.setter
    def lon(self, value):
        self.__alt = angle180(value)


    def __str__(self):
        tmp = self.indent + '<latitude>{}</latitude>\n'.format(self.__lat)
        tmp += self.indent + '<longitude>{}</longitude>\n'.format(self.__lon)
        if self.__alt is not None:
            tmp += self.indent + '<altitude>{}</altitude>\n'.format(self.__alt)
        return tmp

class Heading(Coords):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__heading = None #angle360(0)
        self.set(**kwargs)
        logging.debug('Heading created')

    @property
    def heading(self):
        return self.__heading

    @heading.setter
    def heading(self, value):
        if value is not None:
            self.__heading = angle360(value)
        else:
            self.__heading = None

    def __str__(self):
        tmp = super().__str__()
        if self.__heading is not None:
            tmp += self.indent + '<heading>{}</heading>\n'.format(self.__heading)
        return tmp

class ViewCoords(Heading):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__tilt = None #angle180(0)
        self.set(**kwargs)
        logging.debug('ViewCoords created')

    @property
    def tilt(self):
        return self.__tilt

    @tilt.setter
    def tilt(self, value):
        if value is not None:
            self.__tilt = angle180(value)
        else:
            self.__tilt = None

    def __str__(self):
        tmp = super().__str__()
        if self.__tilt is not None:
            tmp += self.indent + '<tilt>{}</tilt>\n'.format(self.__tilt)
        return tmp

class CameraCoords(ViewCoords):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__roll = None #angle180(roll)
        self.set(**kwargs)

    @property
    def roll(self):
        return self.__roll

    @roll.setter
    def roll(self, value):
        if value is not None:
            self.__roll = angle180(value)
        else:
            self.__roll = None

    def __str__(self):
        tmp = super().__str__()
        if self.__roll is not None:
           tmp += self.indent + '<roll>{}</roll>\n'.format(self.__roll)
        return tmp

class LookAtCoords(ViewCoords):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__range = None #number(range)
        logging.debug('LookAtCoords created')

    @property
    def range(self):
        return self.__range

    @range.setter
    def range(self, value):
        if value is not None:
            self.__range = number(value)
        else:
            self.__range = None


    def __str__(self):
        tmp = ViewCoords.__str__(self)
        if self.__range is not None:
            tmp += self.indent + '<range>{}</range>\n'.format(self.__range)
        return tmp


class Camera(KMLView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coords = CameraCoords(**kwargs)
        self.coords.set(parent = self)
        logging.debug('Camera created')

    def __str__(self):
        tmp = '<Camera{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += str(self.coords)
        tmp += '</Camera>\n'
        return tmp

class LookAt(KMLView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coords = LookAtCoords(**kwargs)
        self.coords.set(parent = self)
        logging.debug('LookAt created')

    def __str__(self):
        tmp = '<LookAt{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += str(self.coords)
        tmp += '</LookAt>\n'
        return tmp

class KMLDateTime(object):
    def __init__(self, value, format = 'Z'):
        self.__value = None
        self.format = format
        self.value = value
        self.__precision = 4

    @property
    def value(self):
        if self.__format in ['Y', 'gYear']:
            return '{:04}'.format(self.__value.year)
        if self.__format in ['YM', 'gYearMonth']:
            return '{:04}-{:02}'.format(self.__value.year, self.__value.month)
        if self.__format in ['YMD', 'dateTime']:
            return '{:04}-{:02}-{:02}'.format(self.__value.year, self.__value.month, self.__value.day)
        if self.__format in ['Z']:    # TODO: Is there a name for this format in the XML Schema?
            return t = self.__value.isoformat().split('.')[0] + 'Z'
        if self.__format in ['UTC']:  # TODO: Is there a name for this format in the XML Schema?
            d = datetime.now() - datetime.utcnow()
            t = d.seconds + round(d.microseconds/1000000)
            return '{}{:+03}:{:02}'.format(self.__value.isoformat().split('.')[0], divmod(t, 3600)[0], divmod(t, 3600)[1])

    @value.setter
    def value(self, value):
        if value is not None:
            if type(value) is str:
                # Convert strings to date based in value of format
                if self.__format is None:
                    raise ValueError('Must specify a format when converting from str to KMLDateTime')
                elif self.__format in ['Y', 'gYear']:
                    # Check the Year to make sure it is are valid numbers.  If so, reasemble and convert
                    if number.isInt(value.split('-')[0]):
                        # NOTE: XML Schema 2.0 allows for 5 digit years.  Although this code will manipulate a 5 digit year,
                        #       strptime does not support it so we are stuck with a 4 digit year for now.
                        value = datetime.strptime('{:04}'.format(int(value.split('-')[0])) + '0101', '%Y%m%d')
                    else:
                        raise ValueError('Invalid year {}'.format(value[:4]))
                elif self.__format in ['YM', 'gYearMonth']:
                    # Check the Year and Month part to make sure they are valid numbers.  If so, reasemble and convert. Default to 1st of the month
                    dateparts = value[:7].split('-')
                    if number.isInt(dateparts[0]) and number.isInt(dateparts[1]):
                        value = datetime.strptime(datepart[0] + datepart[1] + '01', '%Y%m%d')
                    else:
                        raise ValueError('Invalid year-month {}'.format(value[:7]))
                elif self.__format in ['YMD', 'dateTime']:
                    # Check each Year, Day and Month part to make sure they are valid numbers.  If so, reasemble and convert
                    dateparts = value[:10].split('-')
                    if number.isInt(dateparts[0]) and number.isInt(dateparts[1]) and number.isInt(dateparts[2]):
                        value = datetime.strptime(dateparts[0] + dateparts[1] + dateparts[2], '%Y%m%d')
                    else:
                        raise ValueError('Invalid year-month-day {}'.format(value[:10]))
                elif self.__format in ['Z']:
                    # Provide strptime the formatting and convert. Straight forward
                    try:
                        value = datetime.strptime(value, '%Y-%m-%dThh:mm:ssZ')
                    except:
                        raise  #Raise what ever error gets thrown if it doesnt work
                elif self.__format in ['UTC']:
                    # Strip the ':' out of the timezone part and use strptime to convert the string to a datetime
                    try:
                        value = datetime.strptime(value[:len(value)-6] + value[len(value)-6:].replace(':',''),'%Y-%m-%dT%H:%M:%S%z')
                    except:
                        raise  #Raise what ever error gets thrown if it doesnt work
            if type(value) is not datetime:
                raise TypeError('Value must be of type datetime, not {}'.format(type(value)))
        self.__value = value

    @property
    def format(self):
        return self.__format

    @format.setter
    def format(self, value):
        if value not in ['Y', 'gYear',       # Year only
                         'YM', 'gYearMonth', # Year and Month
                         'YMD', 'dateTime',  # Year, Month and Day
                         'Z',                # Full Date/Time UTC
                         'UTC']:             # Full Date/Time with UTC conversion
            raise ValueError('Format pattern does not match')
        self.__format = value

#class TimeSpan(KMLObject):
#    def __init__(self, **kwargs):
#        super().__init__(**kwargs)
#        self.__begin = 
