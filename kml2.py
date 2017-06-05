import logging
from builtins import str
from mako.runtime import _kwargs_for_callable
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
    # Contained By : LabelStyle, IconStyle
    # 

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
    # Contained By : Coords
    # 

    def __init__(self, value):
        if not (-90.0 <= value < 90.0):
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
    # Contained By :
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
    # Contained By : IconStyle
    # 

    def __init__(self, value):
        if not (0.0 <= value < 360.0):
            raise ValueError('Value out of range')

class boolean(int):
    """
    Subclass of int class.  Used to represent a boolean.  Holds a value of 1 for true, 0 for false.
    NOTE: ALL non-false values are considered True
    
    Can be created in several ways:
    
        x = boolean('1')   (returns 1 - True)
        x = boolean(1)     (returns 1 - True)
        x = boolean('0')   (returns 0 - True)
        x = boolean(0)     (returns 0 - True)
        x = boolean(False) (returns 0 - True)
        x = boolean('No')  (returns 0 - True)
        x = boolean('Off') (returns 0 - True)
    """

    #
    # Extends      : int
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained By : gx_ViewerOptions, LineStyle
    # 

    # ANY value that is not 0 or boolean False is considered True
    def __new__(self, value):
        if str(value) == '0' or str(value) == 'False' or str(value.lower()) == 'no' or str(value.lower()) == 'off':
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
    """
    This is an abstract base class and cannot be used directly in a KML file. It 
    provides the id attribute, which allows unique identification of a KML element,
    and the targetId attribute, which is used to reference objects that have
    already been loaded into Google Earth. The id attribute must be assigned if the
    <Update> mechanism is to be used.
    """
    #
    # Extends:
    #
    # Extended by  : KMLContailer, , KMLFeature, KMLView, Snippet, gx_ViewerOptions, Coords, TimeSpan, TimeStamp, ColorStyle, Style,
    #
    # Contains     :
    #
    # Contained By :
    # 

    # Creates and manages the parent and depth properties
    # Introduces the ID attribute
    def __init__(self, **kwargs):
        logging.debug('KMLObject created')
        self.depth = 0
        self.__parent = None
        self.__id = None
        self.set(**kwargs)

    def set(self, **kwargs):
        """
        Sets any properties or attributes for this object via keywords.
        If the object does not contain a property matching the keyword,
        it is ignored.
        
        All object attributes should be wrapped by properties.  This
        allows for grated control and data validation when assigning
        values.
        
        Keywords and properties/attributes are case sensitive.
        """
        for k in kwargs:
            if hasattr(self, k):
                setattr(self, k, kwargs[k])
            else:
                pass
                # raise AttributeError('Invalid attribute {}'.format(k)

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent):
        self._set_parent(parent)

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

    def _set_parent(self, parent):
        """
        Setting the parent property creates an object hierarchy.  This allows proper
        indentation of tags when outputting kml tags to file.
        
        The parent property is simply assigned:
        
            x.parent = self
        """
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
        """
        Returns a given number of spaces for the objects level in the object tree
        """
        return ' ' * self.depth

class KMLContainer(KMLObject):
    """
    Abstract class that manages a collection of child objects.
    
    Any object can be added to a collection using the append or insert methods.
    
    """
    
    #
    # Extends      : KMLObkect
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained By :
    # 

    # Manages a list (collection) of child objects.
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
        """
        depth attribute is wrapped using properties in order to cascade updates to 
        child objects when updated.
        """
        return self.__depth

    @depth.setter
    def depth(self, d):
        self.__depth = d
        logging.debug('KMLContainer updating child depths')
        for child in self.__elements:
            child.depth = self.__depth + 1

    def remove(self, item):
        """
        Remove an item from the collection by reference.
        
        Example:
            c = KMLCollection()
            o = KMLObject
            
            * o references the object
            
            c.remove(o)
        
        See also: find
        """
        logging.debug('KMLContainer removing {} from collection'.format(str(item)))
        self.__elements.remove(item)

    def append(self, item):
        """
        Append an object to the end of the collection.
        """
        # if type(item) is Document: TODO: Uncomment this later
        #    raise TypeError('Document objects cannot be child objects')
        if item is not None:
            if item.parent is not self:  # Stop recursive calls
                item.parent = self
            if item not in self.__elements:
                self.__elements.append(item)
                logging.debug('KMLContainer adding {} to collection'.format(item.__class__.__name__))

    def insert(self, position, item):
        """
        Insert an object at a specific index of the collection.
        """
        if item is not None:
            if item.parent is not self:
                item.parent = self  # This triggers an append
                self.__elements.remove(item)  # Remove it from the end
                logging.debug('KMLContainer inserting {} to collection at {}'.format(str(item), position))
                self.__elements.insert(position, item)  # Insert it where we want it
            if item not in self.__elements:
                logging.debug('KMLContainer inserting {} to collection at {}'.format(str(item), position))
                self.__elements.insert(position, item)

    def find(self, id):
        """
        Return reference to an object in the collection by ID.  If the ID is not
        found, a ValueError is raised.
        """
        # Return reference to an element by id
        # Raises ValueError exception if ID is not found
        for e in self.__elements:
            if e.id == id:
                return e
        raise ValueError('{} is not in elements'.format(id))

    def __len__(self):
        return len(self.__elements)

    def __contains__(self, x):
        """
        Allows the 'in' opperator to be used to check for the existance of an element
        """
        return x in self.__elements

    def __iter__(self):
        """
        Allows itteration over elements
        """
        for x in self.__elements:
            yield x

    def __getitem__(self, index):
        """
        Return an element by index
        """
        return self.__elements[index]

    def __setitem__(self, index, item):
        """
        Set an element by index
        """
        self.__elements[index] = item

    def index(self, item):
        return self.__elements.index(item)

    def pop(self, index=0):
        # Used to delete an element by index
        if len(self.__elements) > 0:
            self.__elements.pop(index)

class KMLFeature(KMLObject):
    """
    This is an abstract element and cannot be used directly in a KML file.
    The following diagram shows how some of a Feature's elements appear in Google Earth.
    """
    #
    # Extends      : KMLObject
    #
    # Extended by  :
    #
    # Contains     : Snippet, Camera/LookAt, TimeStamp/TimeSpan, Style, Region
    #
    # Contained By :
    # 

    # KML Feature object.
    def __init__(self, **kwargs):
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
            if type(value) not in [TimeStamp, TimeSpan]:
                raise ValueError('time must be of type TimeStamp or TimeSpan, not {}'.format(type(value)))
        self.__time = value

    @property
    def styleSelector(self):
        return self.__styleSelector

    @styleSelector.setter
    def styleSelector(self, value):
        if value is not None:
            if type(value) not in [Style, StyleMap]:  # TODO: Write Style, StyleMap, IconStyle,  LabelStyle, LineStyle, PolyStyle, BaloonStyle, ListStyle, ColorStyle
                raise ValueError('styleSelector must be of type IconStyle,  LabelStyle, LineStyle, PolyStyle, BaloonStyle, ListStyle or ColorStyle, not {}'.format(type(value)))
        self.__styleSelector = value

    @property
    def styleURL(self):
        return self.__styleURL

    @styleURL.setter
    def styleURL(self, value):
        if value is not None:
            if type(value) not in [Style, StyleMap]:  # TODO: Write Style, StyleMap
                raise ValueError('styleURL must be of type Style or StyleMap, not {}'.format(type(value)))
        self.__styleURL = value

    @property
    def region(self):
        return self.__region

    @region.setter
    def region(self, value):
        if value is not None:
            if type(value) not in [Region]:  # TODO: Write Region
                raise ValueError('region must be of type Region, not {}'.format(type(value)))
        self.__region = value

    @property
    def metadata(self):
        return self.__metadata

    @metadata.setter
    def metadata(self, value):
        if value is not None:
            if type(value) not in [Metadata]:  # TODO: Write Metadata
                raise ValueError('metadata must be of type MetaData, not {}'.format(type(value)))
        self.__metadata = value

    @property
    def extendedData(self):
        return self.__extendedData

    @extendedData.setter
    def extendedData(self, value):
        if value is not None:
            if type(value) not in [extendedData]:  # TODO: Write Style, StyleMap
                raise ValueError('extendedData must be of type ExtendedData, not {}'.format(type(value)))
        self.__extendedData = value

    def __str__(self):
        logging.debug('KMLFeature outputting child kml elements')
        tmp = ''
        # Output any value based attributes
        for a in ['name', 'description', 'visibility', 'open', 'phoneNumber', 'address']:
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
        for a in ['snippet', 'view', 'time', 'styleURL', 'styleSelector', 'region', 'metadata', 'extendedData']:
            tmp += str(getattr(self, a))
        return tmp

class KMLView(KMLObject):

    #
    # Extends      : KMLObject
    #
    # Extended by  : Camera, LookAt
    #
    # Contains     :
    #
    # Contained By : KMLFeatuyre
    # 

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
        self.__viewer = value

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, value):
        if value is not None:
            if type(value) not in [TimeStamp, TimeSpan]:
                raise TypeError('Time must be of type TimeSpan or TimeStamp, not {}'.format(type(value)))
            value.parent = self
        self.__time = value
        logging.debug('KLMView created')

    def __str__(self):
        tmp = ''
        if self.__viewer is not None:
            tmp += str(self.__viewer)
        if self.__time is not None:
            tmp += str(self.__time)
        return tmp

class KMLVec(KMLObject):
    """
    Specifies the position within the Icon that is "anchored" to the <Point>
    specified in the Placemark. The x and y values can be specified in three
    different ways: as pixels ("pixels"), as fractions of the icon ("fraction"),
    or as inset pixels ("insetPixels"), which is an offset in pixels from the upper
    right corner of the icon. The x and y positions can be specified in different
    ways—for example, x can be in pixels and y can be a fraction. The origin of the
    coordinate system is in the lower left corner of the icon.
    """
    #
    # Extends      : KMLObject
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained by : IconStyle
    #

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.__x = 0
        self.__y = 0
        self.__xUnits = None
        self.__yUnits = None
        self.set(**kwargs)
        logging.debug('KMLVec created')
    
    @property
    def x(self):
        """
        Either the number of pixels, a fractional component of the icon, or a pixel
        inset indicating the x component of a point on the icon.
        """
        return self.__x
    
    @x.setter
    def x(self, value):
        self.__x = number(value)
        
    @property
    def y(self):
        """
        Either the number of pixels, a fractional component of the icon, or a pixel
        inset indicating the y component of a point on the icon.
        """
        return self.__y
    
    @x.setter
    def y(self, value):
        self.__y = number(value)

    @property
    def xUnits(self):
        """
        Units in which the x value is specified. A value of fraction indicates the x
        value is a fraction of the icon. A value of pixels indicates the x value in
        pixels. A value of insetPixels indicates the indent from the right edge of the
        icon.
        """
        return self.__xUnits
    
    @x.setter
    def xUnits(self, value):
        if value is not None:
            if value not in ['fraction','pixels','insertPixels']:
                raise ValueError('Units must be fraction, pixels or insertPixels, not {}'.format(value))
        self.__xUnits = value
        
    @property
    def yUnits(self):
        """
        Units in which the y value is specified. A value of fraction indicates the y
        value is a fraction of the icon. A value of pixels indicates the y value in
        pixels. A value of insetPixels indicates the indent from the top edge of the
        icon.
        """
        return self.__yUnits
    
    @x.setter
    def yUnits(self, value):
        if value is not None:
            if value not in ['fraction','pixels','insertPixels']:
                raise ValueError('Units must be fraction, pixels or insertPixels, not {}'.format(value))
        self.__yUnits = value
    
    def __str__(self):
        tmp = '<hotSpot x="{}" y="{}"'.format(self.__x,self.__y)
        if self.__xUnits is not None:
            tmp += ' xunits="{}"'.format(self.__xUnits)
        if self.__yUnits is not None:
            tmp += ' yunits="{}"'.format(self.yUnits)
        tmp += '</hotSpot>\n'
        return tmp

################################################################################################
#                                                                                              #
#   KML Object definitions                                                                     #
#                                                                                              #
################################################################################################

class Snippet(KMLObject):

    #
    # Extends      : KMLObject
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained by : KMLFeature
    #

    # Introduces a maxLines property
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__content = ''
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

    #
    # Extends      : KMLObject
    #
    # Extended by  :
    #
    # Contains     : boolean
    #
    # Contained by : KMLView
    #

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
        self.__enabled = boolean(value)


    def __str__(self):
        tmp = self.indent + '<gx:ViewerOptions{}>\n'.format(self.id)
        tmp += self.indent + ' <gx:option name="{}" enabled={}/>\n'.format(self.__name, self.__enabled)
        tmp += self.indent + '</gx:ViewerOptions>\n'
        return tmp

class Coords(KMLObject):

    #
    # Extends      : KMLObject
    #
    # Extended by  : Heading
    #
    # Contains     :
    #
    # Contained by :
    #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__lat = angle90(0)
        self.__lon = angle180(0)
        self.__alt = None  # number(0)
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

    #
    # Extends      : Coords
    #
    # Extended by  : ViewCoords
    #
    # Contains     :
    #
    # Contained by :
    #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__heading = None  # angle360(0)
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

    #
    # Extends      : Heading
    #
    # Extended by  : CameraCoords, LookAtCoords
    #
    # Contains     :
    #
    # Contained by :
    #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__tilt = None  # angle180(0)
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

    #
    # Extends      : ViewCoords
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained by : Camera
    #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__roll = None  # angle180(roll)
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

    #
    # Extends      : ViewCoords
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained by : LookAt
    #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__range = None  # number(range)
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

    #
    # Extends      : KMLView
    #
    # Extended by  :
    #
    # Contains     : CameraCoords
    #
    # Contained by : KMLFeature
    #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coords = CameraCoords(**kwargs)
        self.coords.set(parent=self)
        logging.debug('Camera created')

    def __str__(self):
        tmp = '<Camera{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += str(self.coords)
        tmp += '</Camera>\n'
        return tmp

class LookAt(KMLView):

    #
    # Extends      :  KMLView
    #
    # Extended by  :
    #
    # Contains     : LookAtCoords
    #
    # Contained by : KMLFeature
    #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coords = LookAtCoords(**kwargs)
        self.coords.set(parent=self)
        logging.debug('LookAt created')

    def __str__(self):
        tmp = '<LookAt{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += str(self.coords)
        tmp += '</LookAt>\n'
        return tmp

class KMLDateTime(object):

    #
    # Extends      :
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained By : TimeSpan, TimeStamp
    #

    def __init__(self, value=datetime.now(), format='Z'):
        self.__value = None
        self.format = format
        self.value = value
        self.__precision = 4
        logging.debug('KMLDateTime created')

    @property
    def value(self):
        if self.__format in ['Y', 'gYear']:
            return '{:04}'.format(self.__value.year)
        if self.__format in ['YM', 'gYearMonth']:
            return '{:04}-{:02}'.format(self.__value.year, self.__value.month)
        if self.__format in ['YMD', 'dateTime']:
            return '{:04}-{:02}-{:02}'.format(self.__value.year, self.__value.month, self.__value.day)
        if self.__format in ['Z']:  # TODO: Is there a name for this format in the XML Schema?
            return self.__value.isoformat().split('.')[0] + 'Z'
        if self.__format in ['UTC']:  # TODO: Is there a name for this format in the XML Schema?
            d = datetime.now() - datetime.utcnow()
            t = d.seconds + round(d.microseconds / 1000000)
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
                        value = datetime.strptime(dateparts[0] + dateparts[1] + '01', '%Y%m%d')
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
                        raise  # Raise what ever error gets thrown if it doesnt work
                elif self.__format in ['UTC']:
                    # Strip the ':' out of the timezone part and use strptime to convert the string to a datetime
                    try:
                        value = datetime.strptime(value[:len(value) - 6] + value[len(value) - 6:].replace(':', ''), '%Y-%m-%dT%H:%M:%S%z')
                    except:
                        raise  # Raise what ever error gets thrown if it doesnt work
            if type(value) is not datetime:
                raise TypeError('Value must be of type datetime, not {}'.format(type(value)))
        self.__value = value

    @property
    def format(self):
        return self.__format

    @format.setter
    def format(self, value):
        if value not in ['Y', 'gYear',  # Year only
                         'YM', 'gYearMonth',  # Year and Month
                         'YMD', 'dateTime',  # Year, Month and Day
                         'Z',  # Full Date/Time UTC
                         'UTC']:  # Full Date/Time with UTC conversion
            raise ValueError('Format pattern does not match')
        self.__format = value

class TimeSpan(KMLObject):

    #
    # Extends      : KMLObject
    #
    # Extended by  :
    #
    # Contains     : KMLDateTime
    #
    # Contained by :
    #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__begin = None
        self.__end = None
        self.set(**kwargs)
        logging.debug('TimeSpan created')

    @property
    def begin(self):
        return self.__begin

    @begin.setter
    def begin(self, value):
        if value is not None:
            if type(value) is not KMLDateTime:
                raise TypeError('begin must be of type KMLDateTime, not {}'.format(type(value)))
        self.__begin = value

    @property
    def end(self):
        return self.__end

    @end.setter
    def end(self, value):
        if value is not None:
            if type(value) is not KMLDateTime:
                raise TypeError('end must be of type KMLDateTime, not {}'.format(type(value)))
        self.__end = value

    def __str__(self):
        tmp = self.indent + '<TimeSpan{}>\n'.format(self.id)
        if self.begin is not None:
            tmp += self.indent + ' <begin>{}</begin>\n'.format(self.begin.value)
        if self.end is not None:
            tmp += self.indent + ' <end>{}</end>\n'.format(self.end.value)
        tmp += self.indent + '</TimeSpan>\n'
        return tmp

class TimeStamp(KMLObject):

    #
    # Extends      : OMLObject
    #
    # Extended by  :
    #
    # Contains     : KMLDateTime
    #
    # Contained by :
    #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__when = None
        self.set(**kwargs)
        logging.debug('TimeStamp created')

    @property
    def when(self):
        return self.__when

    @when.setter
    def when(self, value):
        if type(value) is not KMLDateTime:
            raise TypeError('when must be of type KMLDateTime, not {}'.format(type(value)))
        self.__when = value

    def __str__(self):
        tmp = self.indent + '<TimeStamp{}>\n'.format(self.id)
        tmp += self.indent + ' <when>{}</when>\n'.format(self.when.value)
        tmp += self.indent + '</TimeStamp>\n'
        return tmp

class Color(object):

    #
    # Extends      :
    #
    # Extended by  :
    #
    # Contains     : colorAttribute
    #
    # Contained by : ColorStyle
    #

    def __init__(self, **kwargs):
        
        self.__alpha = colorAttribute(0)
        self.__red = colorAttribute(0)
        self.__green = colorAttribute(0)
        self.__blue = colorAttribute(0)
        self.__setup(**kwargs)
        logging.debug('Color created')

    def __setup(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])
    
    @property
    def color(selfself):
        return self.__str__()
    
    @color.setter
    def color(self, value):
        self.__alpha = colorAttribute(value[:2])
        self.__red = colorAttribute(value[2:4])
        self.__green = colorAttribute(value[4:6])
        self.__blue = colorAttribute(value[6:8])
    
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
        return str(self.__alpha) + str(self.__red) + str(self.__green) + str(self.__blue)

class KMLColorStyle(KMLObject):

    #
    # Extends      : KMLObject
    #
    # Extended by  : LineStyle, IconStyle, PolyStyle, LabelStyle
    #
    # Contains     : Color
    #
    # Contained by :
    #

    # Introduces color and colorMode properties

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__color = None
        self.__colorMode = None
        self.set(**kwargs)
        logging.debug('KMLColorStyle created')

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        if value is not None:
            if type(value) is not  Color:
                raise TypeError('color must be a Color object, not {}'.format(type(value)))
        self.__color = value

    @property
    def colorMode(self):
        return self.__colorMode

    @colorMode.setter
    def colorMode(self, value):
        if value is not None:
            if value not in ['normal', 'random']:
                raise ValueError('colorMode must be normal or random, not {}'.format(value))
        self.__colorMode = value

    def __str__(self):
        tmp = ''
        if self.__color is not None:
            tmp += self.indent + ' <color>{}</color>\n'.format(str(self.__color))
        if self.__colorMode is not None:
            tmp += self.indent + ' <colorMode>{}</colorMode>\n'.format(self.__colorMode)
        return tmp


class LineStyle(KMLColorStyle):

    #
    # Extends      : ColorStyle
    #
    # Extended by  :
    #
    # Contains     : Color, number, boolean, numberPercent
    #
    # Contained by : Style
    #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__width = None                         # Width of the line in pixels
        self.__outerColor = None                    # Color of the portion of the line defined by gx:outerWidth
        self.__outerWidth = None
        self.__physicalWidth = None
        self.__labelVisibility = None
        self.set(**kwargs)
        logging.debug('LineStyle created')

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        if value is not None:
            self.__width = number(value)
        else:
            self.__width = None

    @property
    def outerColor(self):
        """
        Color of the portion of the line defined by <gx:outerWidth>.
        Note that the <gx:outerColor> and <gx:outerWidth> elements are ignored when
        <LineStyle> is applied to <Polygon> and <LinearRing>.
        
        Example:
            x.outerColor = Color(red=255, green = 0, blue = 255, alpha = 0)
        
        Args:
            value: (:obj:`Color`): Color attributes of the outerColor
        
        Returns:
            obj:`Color`
        """
        return self.__outerColor

    @outerColor.setter
    def outerColor(self, value):
        if value is not None:
            if type(value) is not Color:
                raise TypeError('outerColor must be of type Color, not {}'.format(type(value)))
        self.__outerColor = value


    @property
    def outerWidth(self):
        """
        A value between 0.0 and 1.0 that specifies the proportion of the line that uses the <gx:outerColor>. 
        Only applies to lines setting width with <gx:physicalWidth>; it does not apply to lines using <width>.
        See also <gx:drawOrder> in <LineString>.
        A draw order value may be necessary if dual-colored lines are crossing each other—for example,
        for showing freeway interchanges.
        """
        return self.__outerWidth

    @outerWidth.setter
    def outerWidth(self, value):
        if value is not None:
            self.__outerWidth = numberPercent(value)
        else:
            self.__outerWidth = None

    @property
    def physicalWidth(self):
        return self.__physicalWidth

    @physicalWidth.setter
    def physicalWidth(self, value):
        if value is not None:
            self.__physicalWidth = number(value)
        else:
            self.__physicalWidth = None

    @property
    def labelVisibility(self):
        return self.__labelVisibility

    @labelVisibility.setter
    def labelVisibility(self, value):
        if value is not None:
            self.__labelVisibility = boolean(value)
        else:
            self.__labelVisibility = None

    def __str__(self):
        tmp = self.indent + '<LineStyle{}>\n'.format(self.id)
        tmp += super().__str__()
        if self.__width is not None:
            tmp += self.indent + ' <width>{}</width>\n'.format(self.__width)
        if self.__outerColor is not None:
            tmp += self.indent + ' <gx:outerColor>{}</gx:outerColor>\n'.format(str(self.__outerColor))
        if self.__outerWidth is not None:
            tmp += self.indent + ' <gx:outerWidth>{}</gx:outerWidth>\n'.format(str(self.__outerWidth))
        if self.__physicalWidth is not None:
            tmp += self.indent + ' <gx:physicalWidth>{}</gx:physicalWidth>\n'.format(str(self.__physicalWidth))
        if self.__labelVisibility is not None:
            tmp += self.indent + ' <gx:labelVisibility>{}</gx:labelVisibility>\n'.format(str(self.__labelVisibility))
        tmp += self.indent + '</LineStyle>\n'
        return tmp

class IconStyle(KMLColorStyle):
    """
    Specifies how icons for point Placemarks are drawn, both in the Places
    panel and in the 3D viewer of Google Earth. The <Icon> element specifies
    the icon image. The <scale> element specifies the x, y scaling of the
    icon. The color specified in the <color> element of <IconStyle> is blended
    with the color of the <Icon>.
    """
    #
    # Extends      : KMLColorStyle
    #
    # Extended by  :
    #
    # Contains     : KMLVec, angle360, number
    #
    # Contained by : Style
    #
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__scale = None
        self.__heading = None
        self.__icon = None
        self.__hotSpot = None
        self.set(**kwargs)
        logging.debug('IconStyle created')
    
    @property
    def scale(self):
        """Resizes the icon."""
        return self.__scale
    
    @scale.setter
    def scale(self, value):
        if value is not None:
            self.__scale = number(value)
        else:
            self.__scale = None
    
    @property
    def heading(self):
        """
        Direction (that is, North, South, East, West), in degrees.
        Default=0 (North). Values range from 0 to 360 degrees
        """
        return self.__heading
    
    @heading.setter
    def heading(self, value):
        if value is not None:
            self.__heading = angle360(value)
        else:
            self.__heading = None
    
    @property
    def icon(self):
        """
        A custom Icon. An HTTP address or a local file specification used to load an icon.
        """
        return self.__icon
    @icon.setter
    def icon(self,value):
        if type(value) is not str:
            raise TypeError('icon must be of type str, not {}'.format(type(value)))
        self.__icon = value
    
    @property
    def hotSpot(self):
        """ See help(KMLVec) for more information on hotSpot. """
        return self.__hotSpot
    
    @hotSpot.setter
    def hotSpot(self, value):
        if type(value) is not KMLVec:
            raise TypeError('hoySpot must be of type hotSpot, not {}'.format(type(value)))
        self.__hotSpot = value
        self.hotSpot.parent = self
    
    def __str__(self):
        tmp = self.indent + '<IconStyle{}>\n'.format(self.id)
        tmp += super().__str__()
        if self.__scale is not None:
            tmp += self.indent + ' <scale>{}</scale>\n'.format(self.__scale)
        if self.__heading is not None:
            tmp += self.indent + ' <heading>{}</heading>\n'.format(self.__heading)
        if self.__icon is not None:
            tmp += self.indent + ' <Icon>\n'
            tmp += self.indent + '  <href>{}</href>\n'.format(self.__icon)
            tmp += self.indent + ' </Icon>\n'
        if self.__hotSpot is not None:
            tmp += self.indent + ' ' + str(self.__hotSpot)
        tmp += self.indent + '</IconStyle>\n'
        return tmp

class LabelStyle(KMLColorStyle):
    """
    Specifies how the <name> of a Feature is drawn in the 3D viewer. A custom color,
    color mode, and scale for the label (name) can be specified.
    """
    #
    # Extends      : KMLColorStyle
    #
    # Extended by  :
    #
    # Contains     : number
    #
    # Contained by : Style
    #
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__scale = None
        self.set(**kwargs)
        logging.debug('LabelStyle created')
    
    @property
    def scale(self):
        """Resizes the label."""
        return self.__scale
    
    @scale.setter
    def scale(self, value):
        if value is not None:
            self.__scale = number(value)
        else:
            self.__scale = None

    def __str__(self):
        tmp = self.indent + '<LabelStyle{}>\n'.format(self.id)
        tmp += super().__str__()
        if self.__scale is not None:
            tmp += self.indent + ' <scale>{}</scale>\n'.format(self.__scale)
        tmp += self.indent + '</LabelStyle>\n'
        return tmp
   
class PolyStyle(KMLColorStyle):
    """
    Specifies the drawing style for all polygons, including polygon extrusions
    (which look like the walls of buildings) and line extrusions (which look
    like solid fences).
    """
    #
    # Extends      : KMLColorStyle
    #
    # Extended by  :
    #
    # Contains     : boolean
    #
    # Contained by : Style
    #
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__fill = None
        self.__outline = None
        self.set(**kwargs)
        logging.debug('PolyStyle created')
    
    @property
    def fill(self):
        """Boolean value. Specifies whether to fill the polygon."""
        return self.__fill
    
    @fill.setter
    def fill(self, value):
        if value is not None:
            self.__fill = boolean(value)
        else:
            self.__fill = None
   
    @property
    def outline(self):
        """Boolean value. Specifies whether to outline the polygon. Polygon outlines use the current LineStyle."""
        return self.__outline
    
    @outline.setter
    def outline(self, value):
        if value is not None:
            self.__outline = boolean(value)
        else:
            self.__outline = None
   
    def __str__(self):
        tmp = self.indent + '<PolyStyle{}>\n'.format(self.id)
        tmp += super().__str__()
        if self.__fill is not None:
            tmp += self.indent + ' <fill>{}</fill>\n'.format(self.__fill)
        if self.__outline is not None:
            tmp += self.indent + ' <outline>{}</outline>\n'.format(self.__outline)
        tmp += self.indent + '</PolyStyle>\n'
        return tmp

class ItemIcon(KMLObject):
    """
    Icon used in the List view that reflects the state of a Folder or Link fetch.
    Icons associated with the open and closed modes are used for Folders and
    Network Links. Icons associated with the error and fetching0, fetching1, and
    fetching2 modes are used for Network Links.
    """
    #
    # Extends      : KMLObject
    #
    # Extended by  :
    #
    # Contains     :
    #
    # Contained by : ListStyle
    #
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__state = None
        self.__href = None
        self.set(**kwargs)
        logger.debug('ItemIcon created')
    
    @property
    def state(self):
        """
        Specifies the current state of the NetworkLink or Folder. Possible values
        are open, closed, error, fetching0, fetching1, and fetching2. These values
        can be combined by inserting a space between two values (no comma).
        """
        return self.__state
    
    @state.setter
    def state(self, value):
        if value is not None:
            tmp = value.split(' ')
            for t in tmp:
                if t not in ['open','closed','error','fetching0','fetching1','fetching2']:
                    raise ValueError('state must be open, closed, error, fetching0, fetching1 or fetching2, not {}'.format(value))
        self.__state = value
    
    @property
    def href(self):
        """Specifies the URI of the image used in the List View for the Feature."""
        return self.__href
    
    @href.setter
    def href(self, value):
        if value is not None:
            if type(value) is not str:
                raise TypeError('href must be of type str, notm {}'.format(type(value)))
        self.__href = value
    
    def __str__(self):
        tmp = self.indent + '<ItemIcon>\n'
        if self.__state is not None:
            tmp += self.indent + ' <state>{}</state>\n'.format(self.__state)
        if self.__href is not None:
            tmp += self.indent + ' <href>{}</href>\n'.format(self.__href)
        tmp += self.indent + '</ItemIcon>\n'
        return tmp

class BalloonStyle(KMLObject):
    """
    Specifies how the description balloon for placemarks is drawn. The <bgColor>,
    if specified, is used as the background color of the balloon. See <Feature> for
    a diagram illustrating how the default description balloon appears in Google
    Earth.
    """
    #
    # Extends      : KMLObject
    #
    # Extended by  :
    #
    # Contains     : Color
    #
    # Contained by : ListStyle
    #
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__bgColor = None
        self.__textColor = None
        self.__text = None
        self.__displayMode = None
        self.set(**kwargs)
        logger.debug('BalloonStyle created')
    
    @property
    def bgColor(self):
        """
        Background color of the balloon (optional). Color and opacity (alpha) values
        are expressed in hexadecimal notation. The range of values for any one color
        is 0 to 255 (00 to ff). The order of expression is aabbggrr, where aa=alpha
        (00 to ff); bb=blue (00 to ff); gg=green (00 to ff); rr=red (00 to ff). For
        alpha, 00 is fully transparent and ff is fully opaque. For example, if you
        want to apply a blue color with 50 percent opacity to an overlay, you would
        specify the following: <bgColor>7fff0000</bgColor>, where alpha=0x7f,
        blue=0xff, green=0x00, and red=0x00. The default is opaque white (ffffffff).
        """
        return self.__bgColor
    
    @bgColor.setter
    def bgColor(self, value):
        if value is not None:
            if type(value) is not Color:
                raise TypeError('bgColor must be of type Color, not {}'.format(type(value)))
        self.__bgColor = value
    
    @property
    def textColor(self):
        """
        Foreground color for text. The default is black (ff000000).
        """
        return self.__textColor
    
    @textColor.setter
    def textColor(self, value):
        if value is not None:
            if type(value) is not Color:
                raise TypeError('textColor must be of type Color, not {}'.format(type(value)))
        self.__textColor = value
    
    @property
    def text(self):
        """
        Text displayed in the balloon. If no text is specified, Google Earth
        draws the default balloon (with the Feature <name> in boldface, the
        Feature <description>, links for driving directions, a white background,
        and a tail that is attached to the point coordinates of the Feature, if
        specified).
        
        You can add entities to the <text> tag using the following format to refer
        to a child element of Feature: $[name], $[description], $[address], $[id],
        $[Snippet]. Google Earth looks in the current Feature for the corresponding
        string entity and substitutes that information in the balloon. To include
        To here - From here driving directions in the balloon, use the
        $[geDirections] tag. To prevent the driving directions links from appearing
        in a balloon, include the <text> element with some content, or with
        $[description] to substitute the basic Feature <description>.
        
        For example, in the following KML excerpt, $[name] and $[description] fields
        will be replaced by the <name> and <description> fields found in the Feature
        elements that use this BalloonStyle:
        
            <text>This is $[name], whose description is:<br/>$[description]</text>
        """
        return self.__text
    
    @text.setter
    def text(self,value):
        if value is not None:
            if type(value) is not str:
                raise TypeError('text must be of type str, not{}'.format(type(value)))
        self.__text = value
    
    @property
    def displayMode(self):
        """
        If <displayMode> is default, Google Earth uses the information supplied in
        <text> to create a balloon . If <displayMode> is hide, Google Earth does not
        display the balloon. In Google Earth, clicking the List View icon for a
        Placemark whose balloon's <displayMode> is hide causes Google Earth to fly
        to the Placemark.
        """
        return self.__displayMode
    
    @displayMode.setter
    def displayMode(self, value):
        if value is not None:
            if value not in ['default','hide']:
                raise ValueError('displayMode must be default or hide, not {}'.format(value))
        self.__displayMode = value
    
    def __str__(self):
        tmp = self.indent + '<BalloonStyle{}>\n'.format(self.id)
        if self.__bgColor is not None:
            tmp += self.indent + ' <bgColor>{}</bgColor>\n'.format(str(self.__bgColor))
        if self.__textColor is not None:
            tmp += self.indent + ' <textColor>{}</textColor>\n'.format(str(self.__textColor))
        if self.__text is not None:
            tmp += self.indent + ' <text>{}</text>\n'.format(str(self.__text))
        if self.__displayMode is not None:
            tmp += self.indent + ' <displayMode>{}</displayMode>\n'.format(str(self.__displayMode))
        tmp += self.indent + '</BalloonStyle>\n'
        return tmp

class ListStyle(KMLContainer):
    """
    Specifies how a Feature is displayed in the list view. The list view is a
    hierarchy of containers and children; in Google Earth, this is the Places panel.
    """
    #
    # Extends      : KMLContainer
    #
    # Extended by  :
    #
    # Contains     : ItemIcon, Color
    #
    # Contained by : Style
    #
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__listItemType = None
        self.__bgColor = None
        self.set(**kwargs)
        logger.debug('ListStyle created')
        
    @property
    def listItemType(self):
        """
        Specifies how a Feature is displayed in the list view. Possible values are:
        
            check (default) - The Feature's visibility is tied to its item's 
            checkbox.
            
            radioFolder - When specified for a Container, only one of the
            Container's items is visible at a time
            
            checkOffOnly - When specified for a Container or Network Link, prevents
            all items from being made visible at once—that is, the user can turn
            everything in the Container or Network Link off but cannot turn
            everything on at the same time. This setting is useful for Containers
            or Network Links containing large amounts of data.
            
            checkHideChildren - Use a normal checkbox for visibility but do not
            display the Container or Network Link's children in the list view. A
            checkbox allows the user to toggle visibility of the child objects in
            the viewer.
        """
        return self.__listItemType
    
    @listItemType.setter
    def listItemType(self, value):
        if value is not None:
            if value not in ['check','radioFolder','checkOffOnly','checkHiddenChildren']:
                raise ValueError('listItemType must be check, radioFolder, checkOffOnly or checkHiddenChildren, not {}'.format(value))
        self.__listItemType = value
    
    @property
    def bgColor(self):
        """
        Background color for the Snippet. Color and opacity values are expressed in
        hexadecimal notation. The range of values for any one color is 0 to 255 (00
        to ff). For alpha, 00 is fully transparent and ff is fully opaque. The order
        of expression is aabbggrr, where aa=alpha (00 to ff); bb=blue (00 to ff);
        gg=green (00 to ff); rr=red (00 to ff). For example, if you want to apply a
        blue color with 50 percent opacity to an overlay, you would specify the
        following: <color>7fff0000</color>, where alpha=0x7f, blue=0xff, green=0x00,
        and red=0x00.
        """
        return self.__bgColor
    
    @bgColor.setter
    def bgColor(self, value):
        if value is not None:
            if type(value) is not Color:
                raise TypeError('bgColor must be of type Color, not {}'.format(type(value)))
        self.__bgColor = value
    
    def __str__(self):
        tmp = self.indent + '<ListStyle>\n'
        if self.__listItemType is not None:
            tmp += self.indent + ' <listItemType>{}</listItemType>\n'.format(self.__listItemType)
        if self.__bgColor is not None:
            tmp+= self.indent + ' <bgColor>{}</bgcolor>\n'.format(str(self.__bgColor))
        tmp += super().__str__()
        tmp += '</ListStyle>\n'
        return tmp

class Style(KMLObject):

    #
    # Extends      : KMLObject
    #
    # Extended by  :
    #
    # Contains     : IconStyle, LabelStyle, LineStyle, PolyStyle, LisSttyle, BalloonStyle
    #
    # Contained by : KMLFeature
    #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__icon = None
        self.__label = None
        self.__line = None
        self.__poly = None
        self.__balloon = None
        self.__list = None
        self.set(**kwargs)
        logger.debug('Style created')
    
    @property
    def iconStyle(self):
        return self.__icon
    
    @iconStyle.setter
    def iconStyle(self, value):
        if value is not None:
            if type(value) is not IconStyle:
                raise TypeError('iconStyle must be of type IconStyle, not {}'.format(type(value)))
            value.parent = self
        self.__icon = value
    
    @property
    def labelStyle(self):
        return self.__label
    
    @labelStyle.setter
    def labelStyle(self, value):
        if value is not None:
            if type(value) is not LabelStyle:
                raise TypeError('labelStyle must be of type LabelStyle, not {}'.format(type(value)))
            value.parent = self
        self.__label = value
    
    @property
    def lineStyle(self):
        return self.__line
    
    @lineStyle.setter
    def lineStyle(self, value):
        if value is not None:
            if type(value) is not LineStyle:
                raise TypeError('lineStyle must be of type LineStyle, not {}'.format(type(value)))
            value.parent = self
        self.__line = value
    
    @property
    def polyStyle(self):
        return self.__poly
    
    @polyStyle.setter
    def polyStyle(self, value):
        if value is not None:
            if type(value) is not PolyStyle:
                raise TypeError('polyStyle must be of type PolyStyle, not {}'.format(type(value)))
            value.parent = self
        self.__poly = value
    
    @property
    def balloonStyle(self):
        return self.__balloon
    
    @balloonStyle.setter
    def balloonStyle(self, value):
        if value is not None:
            if type(value) is not BalloonStyle:
                raise TypeError('balloonStyle must be of type BalloonStyle, not {}'.format(type(value)))
            value.parent = self
        self.__balloon = value
    
    @property
    def listStyle(self):
        return self.__list
    
    @listStyle.setter
    def listStyle(self, value):
        if value is not None:
            if type(value) is not ListStyle:
                raise TypeError('listStyle must be of type ListStyle, not {}'.format(type(value)))
            value.parent = self
        self.__list = value
    
    def __str__(self):
        tmp = self.indent + '<Style{}>\n'.format(self.id)
        if self.__icon is not None:
            tmp += str(self.__icon)
        if self.__line is not None:
            tmp += str(self.__line)
        if self.__poly is not None:
            tmp += str(self.__poly)
        if self.__label is not None:
            tmp += str(self.__label)
        if self.__balloon is not None:
            tmp += str(self.__balloon)
        if self.__list is not None:
            tmp += str(self.__list)
        tmp += self.indent + '</Style>'
        return tmp
        
    
    
    

