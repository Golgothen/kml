import logging
logger = logging.getLogger()
# Remove after testing
f = logging.Formatter('%(levelname)-8s:%(funcName)-20s %(lineno)-5s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(f)
logger.addHandler(h)
logger.setLevel(logging.DEBUG)


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


class angle90(number):
    def __init__(self, value):
        if not (-90.0 <= value <= 90.0):
            raise ValueError('Value out of range')


class angle180(number):
    def __init__(self, value):
        if not (-180.0 <= value <= 180.0):
            raise ValueError('Value out of range')


class angle360(number):
    def __init__(self, value):
        if not (0.0 <= value < 360.0):
            raise ValueError('Value out of range')

class boolean(int):
    # ANY value that is not 0 is concidered True
    def __new__(self, value):
        if str(value) == '0':
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
                setattr(self, k, kwargs[k]
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
        if value is not None
            if type(value) not in [str, int, float]:
                raise ValueError('name must be of type str, int or float, not {}'.format(type(value)))
        self.__name = value

    @property
    def description(self):
        return self.__decription

    @description.setter
    def description(self, value):
        if value is not None
            if type(value) not in [str]:
                raise ValueError('description must be of type str, not {}'.format(type(value)))
        self.__description = value

    @property
    def visibility(self):
        return self.__visibility

    @visibility.setter
    def visibility(self, value):
        if value is not None
            if type(value) not in [str, int, float]:
                raise ValueError('Invalid value for visibility {}'.format(repr(value)))
        self.__visibility = boolean(value)

    @property
    def open(self):
        return self.__open

    @open.setter
    def open(self, value):
        if value is not None
            if type(value) not in [str, int, float]:
                raise ValueError('Invalid value for open {}'.format(repr(value)))
        self.__open = boolean(value)

    @property
    def author(self):
        return self.__author

    @author.setter
    def author(self, value):
        if value is not None
            if type(value) not in [str]:
                raise ValueError('author must be of type str, not {}'.format(type(value)))
        self.__author = value

    @property
    def link(self):
        return self.__link

    @link.setter
    def link(self, value):
        if value is not None
            if type(value) not in [str]:
                raise ValueError('link must be of type str, not {}'.format(type(value)))
        self.__author = value

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, value):
        if value is not None
            if type(value) not in [str]:
                raise ValueError('address must be of type str, not {}'.format(type(value)))
        self.__author = value

    @property
    def phoneNumber(self):
        return self.__phoneNumber

    @phoneNumber.setter
    def phoneNumber(self, value):
        if value is not None
            if type(value) not in [str]:
                raise ValueError('phoneNumber must be of type str, not {}'.format(type(value)))
        self.__author = value

	    @property

    def snippet(self):
        return self.__snippet

    @snippet.setter
    def snippet(self, value):
        if value is not None
            if type(value) not in [Snippet]:
                raise ValueError('snippet must be of type Snippet, not {}'.format(type(value)))
        self.__author = value

    def view(self):
        return self.__view

    @view.setter
    def view(self, value):
        if value is not None
            if type(value) not in [LookAt, Camera]:
                raise ValueError('view must be of type LookAt or Camera, not {}'.format(type(value)))
        self.__author = value




    def __str__(self):
        logging.debug('KMLFeature outputting child kml elements')
        tmp = ''
        for a in self.__attributes:
            if type(a) is str:    # Construct tag string for string (and boolean) attributes
                # Check the only two special case attributes
                if a == 'atom:author':
                    # TODO: According to KML documentation, atom:author does not have a close tag.
                    #       Not sure if this is correct or a typo in the documentation.
                    #       As per documentation:
                    tmp += self.indent + ' <{}>{}<{}>\n'.format(a, self.__attributes[a], a)
                elif a == 'atom:link':
                    # Link tag has a slightly different layout
                    tmp +=  self.indent + ' <{} href="{}"/>\n'.format(a, self.__attributes[a])
                else:
                    # all other attributes
                    tmp +=  self.indent + ' <{}>{}</{}>\n'.format(a, self.__attributes[a], a)
            else:
                # call __str__ for object types to get their tags
                tmp += str(self.__attributes[a])
        tmp += super().__str__()
        return tmp

class KMLView(KMLObject):
    # Abstract class for View objects
    def __init__(self, time = None, view = None, parent = None):
        super().__init__(parent)
        self.view = None
        self.time = None
        if view is not None:
            if view.__class__.__name__ not in ['gx_ViewerOptions']:
                raise TypeError('View must be of type gx_ViewerOptions or None, not {}'.format(type(view).name))
            self.viewer = view
            self.viewer.parent = self
        if time is not None:
            if time.__class__.__name__ not in ['TimeStamp', 'TimeSpan']:
                raise TypeError('Time must be of type TimeSpan, TimeStamp or None, not {}'.format(type(time).name))
            self.time = time
            self.time.parent = self
        logging.debug('KLMView created')

    def __str__(self):
        tmp = ''
        if self.view is not None:
            tmp += str(self.view)
        if self.time is not None:
            tmp += str(self.time)
        return tmp


################################################################################################
#                                                                                              #
#   KML Object definitions                                                                     #
#                                                                                              #
################################################################################################

class Snippet(KMLObject):
    # Snippet object - Optionally used in any Container object
    # Introduces a maxLines property
    def __init__(self, content = None, maxLines = 1, parent = None):
        super().__init__(parent)
        self.content = '' if content is None else content
        self.maxLines = maxLines
        logging.debug('Snippet created')

    def __str__(self):
        return self.indent + '<Snippet maxLines="{}">{}</Snippet>'.format(self.maxLines, self.content)


class gx_ViewerOptions(KMLObject):
    def __init__(self, name, enabled = '1', parent = None):
        super().__init__(parent)
        if name not in ['streetview', 'historicalimagery', 'sunlight', 'groundnavigation']:
            raise ValueError('name must be streetview, historicalimagery, sunlight or  groundnavigation')
        self.name = name
        if str(enabled) == '0':
            self.enabled = '0'
        else:
            self.enabled = '1'
        logging.debug('gx:ViewerOptions created')

    def __str__(self):
        tmp = self.indent + '<gx:ViewerOptions>\n'
        tmp = self.indent + ' <gx:option name="{}" enabled={}/>\n'.format(self.name, self.enabled)
        tmp = self.indent + '</gx:ViewerOptions>\n'
        return tmp


class Coords(KMLObject):
    def __init__(self, lat = 0, lon = 0, alt = 0, parent = None):
        super().__init__(parent)
        self.alt = number(alt)
        self.lat = angle90(lat)
        self.lon = angle180(lon)
        logging.debug('Coords created')

    def __str__(self):
        tmp = self.indent + '<latitude>{}</latitude>\n'.format(self.lat)
        tmp += self.indent + '<longitude>{}</longitude>\n'.format(self.lon)
        tmp += self.indent + '<altitude>{}</altitude>\n'.format(self.alt)
        return tmp

class Heading(Coords):
    def __init__(self, lat = 0, lon = 0, alt = 0, heading = 0, parent = None):
        super().__init__(lat, lon, alt, parent)
        self.heading = angle360(heading)
        logging.debug('Heading created')

    def __str__(self):
        tmp = super().__str__()
        tmp += self.indent + '<heading>{}</heading>\n'.format(self.heading)
        return tmp

class ViewCoords(Heading):
    def __init__(self, lat = 0, lon = 0, alt = 0, heading = 0, tilt = 0, parent = None):
        super().__init__(lat, lon, alt, heading, parent)
        self.tilt = angle180(tilt)
        logging.debug('ViewCoords created')

    def __str__(self):
        tmp = super().__str__()
        tmp += self.indent + '<tilt>{}</tilt>\n'.format(self.tilt)
        return tmp

class CameraCoords(ViewCoords):
    def __init__(self, lat = 0, lon = 0, alt = 0, heading = 0, tilt = 0, roll = 0, parent = None):
        super().__init__(lat, lon, alt, heading, tilt, parent)
        self.roll = angle180(roll)

    def __str__(self):
        tmp = super().__str__()
        tmp += self.indent + '<roll>{}</roll>\n'.format(self.roll)
        return tmp

class LookAtCoords(Heading):
    def __init__(self, lat = 0, lon = 0, alt = 0, heading = 0, tilt = 0, range = 0, parent = None):
        super().__init__(lat, lon, alt, heading, tilt, parent)
        self.range = number(range)
        logging.debug('LookAtCoords created')

    def __str__(self):
        tmp = ViewCoords.__str__(self)
        tmp += self.indent + '<roll>{}</roll>\n'.format(self.roll)
        return tmp


class Camera(KMLView):
    def __init__(self, lat = 0, lon = 0, alt = 0, heading = 0, tilt = 0, roll = 0, time = None, view = None, parent = None):
        super().__init__(time, view, parent)
        self.coords = CameraCoords(lat, lon, alt, heading, tilt, roll, self)
        logging.debug('Camera created')

    def __str__(self):
        tmp = '<Camera{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + str(self.coords)
        tmp += '</Camera>\n'
        return tmp

class LookAt(KMLView):
    def __init__(self, lat = 0, lon = 0, alt = 0, heading = 0, tilt = 0, range = 0, time = None, view = None, parent = None):
        super().__init__(time, view, parent)
        self.coords = LookAtCoords(lat, lon, alt, heading, tilt, range, self)
        logging.debug('LookAt created')

    def __str__(self):
        tmp = '<LookAt{}>\n'.format(self.id)
        tmp += super().__str__()
        tmp += self.indent + str(self.coords)
        tmp += '</CLookAt>\n'
        return tmp








