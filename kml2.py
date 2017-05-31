import logging
logger = logging.getLogger()
# Remove after testing
f = logging.Formatter('%(levelname)-8s:%(funcName)-20s %(lineno)-5s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(f)
logger.addHandler(h)
logger.setLevel(logging.DEBUG)


class KMLObject(object):
    # Base class for primitive KML Object.  Creates and manages the parent and depth properties
    # Introduces the ID attribute
    def __init__(self, id = None, parent = None):
        logging.debug('KMLObject created')
        self.depth = 0
        self.__parent = None
        self.parent = parent
        self.id = id

    @property
    def parent(self):
        return self.__get_parent()

    def __get_parent(self):
        # Allows derived classes to override parent property methods
        return self.__parent

    @parent.setter
    def parent(self, parent):
        # Allows derived classes to override parent property methods
        self._set_parent(parent)

    def _set_parent(self, parent):
        if parent is not None:
            if not hasattr(parent, 'append'):
                raise TypeError('Parent object must be derived from KMLContainer or NoneType')
            self.__parent = parent
            parent.append(self)
            logging.debug('KMLObject parent property set')
            self.depth = parent.depth + 1
        else:
            if self.__parent is not None:
                logging.debug('KMLObject removing self from parent collection')
                self.__parent.remove(self)
            self.__parent = None
            logging.debug('KMLObject parent property unset')
            self.depth = 0

#    def __del__(self):
#        if self.__parent is not None:
#            logging.debug('KMLObject destroyed')
#            self.__parent.remove(self)

    def _get_id_str(self):
        # Returnds the ID string
        # Gets called by the sublasses
        if self.id is None:
            return ''
        else:
            return ' id="{}"'.format(self.id)

    @property
    def indent(self):
        return ' ' * self.depth


class KMLContainer(KMLObject):

    # Base class for primitive Container objects.  Manages a list (collection) of child objects.
    # Overrides the parent and depth properties.

    def __init__(self, parent = None):
        self.__elements = []
        super(KMLContainer, self).__init__(parent)
        logging.debug('KMLContainer created')

    def __str__(self):
        # This will be overridden by derived classes
        # Call another function to create KML code for any set parameters
        return self._get_kml_body()

    def _get_kml_body(self):
        logging.debug('KMLContainer outputting child kml elements')
        tmp = ''
        for e in self.__elements:
            tmp += self.indent + str(e)
        return tmp

    @KMLObject.parent.setter
    def parent(self, parent):
        self._set_parent(parent)
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

    def append(self, item):
        #if type(item) is Document: TODO: Uncomment this later
        #    raise TypeError('Document objects cannot be child objects')
        if item is not None:
            if item.parent is not self:  # Stop recursive calls
                item.parent = self
            if item not in self.__elements:
                self.__elements.append(item)
                logging.debug('KMLContainer adding {} to collection'.format(item.__class__.__name__))

    def remove(self, item):
        logging.debug('KMLContainer removing {} from collection'.format(str(item)))
        self.__elements.remove(item)

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


class KMLFeature(KMLContainer):

    # KML Feature object.
    def __init__(self, **kwargs):
        # parent is passed in kwargs.  Declare the super with None for the parent for now
        super(KMLFeature, self).__init__(None)
        self.setAttribute(**kwargs)
        self.__attributes = {}

    def setAttribute(self, **kwargs):
        for k in kwargs:
            # Check for parent
            if k == 'parent':
                self.parent = k['parent']
            # Validate boolean types
            if k in ['visibility', 'open']:
                # '0' values are considered false, all other values considered true
                if str(kwargs[k]) == '0':
                    kwargs[k] = '0'
                else:
                    kwargs[k] = '1'
            # check string types and object types
            if k in ['name', 'description', 'phoneNumber', 'xal:AddressDetails','atom:author', 'atom:link', 'snippet', 'view', 'time', 'styleSelector', 'region', 'extendedData','visibility', 'open']:
                self.__attributes[k] = kwargs[k]

    def getAttribute(self, attr):
        return self.__attributes[attr]

    def __str__(self):
        # Detived classes will override this nethod
        tmp = self._get_kml_attributes()
        tmp += self._get_kml_body()
        return tmp

    def _get_kml_attributes(self):
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
        return tmp

class Snippet(KMLObject):
    # Snippet object - Optionally used in any Container object
    # Introduces a maxLines property
    def __init__(self, content = None, maxLines = 1, parent = None):
        super(Snippet, self).__init(parent)
        self.content = '' if content is None else content
        self.maxLines = maxLines

    def __str__(self):
        return self.indent + '<Snippet maxLines="{}">{}</Snippet>'.format(self.maxLines, self.content)




class gx_ViewerOptions(KMLObject):
    def __init__(self, name, enabled = '1', parent = None):
        super(gx_ViewerOptions, self).__init__(parent)
        if name not in ['streetview', 'historicalimagery', 'sunlight', 'groundnavigation']:
            raise ValueError('name must be streetview, historicalimagery, sunlight or  groundnavigation')
        self.name = name
        if str(enabled) == '0':
            self.enabled = '0'
        else:
            self.enabled = '1'

    def __str__(self):
        tmp = self.indent + '<gx:ViewerOptions>\n'
        tmp = self.indent + ' <gx:option name="{}" enabled={}/>\n'.format(self.name, self.enabled)
        tmp = self.indent + '</gx:ViewerOptions>\n'
        return tmp

class Coords(KMLObject):
    def __init__(self, lat = 0, lon = 0, alt = 0, parent = None):
        super(Coords, self).__init__(parent)
        if type(alt) is not float:
            raise TypeError('Altitude must be a float')
        self.alt = alt
        if type(lat) is not float:
            raise TypeError('Latitude must be a float')
        else:
            if -90.0 <= lat <= 90.0:
                raise ValueError('Latitude out of range')
        self.lat = lat
        if type(lon) is not float:
            raise TypeError('Longitude must be a float')
        else:
            if -180.0 <= lat <= 180.0:
                raise ValueError('Longitude out of range')
        self.lon = lon

    def __str__(self):
        # This class can also be subclassed
        return _str_coords()

    def _str_coords(self):
        tmp = self.indent + '<longitude>{}</longitude>\n'.format(self.lon)
        tmp += self.indent + '<latitude>{}</latitude>\n'.format(self.lat)
        tmp += self.indent + '<altitude>{}</altitude>\n'.format(self.alt)

class Heading(Coords):
    def __init__(self, lat = 0, lon = 0, alt = 0, heading = 0, parent = None):
        super(Heading, self).__init__(lat, lon, alt, parent)
        if type(heading) is not float:
            raise TypeError('Heading must be a float')
        else:
            if 0.0 <= heading <= 360.0:
                raise ValueError('Heading out of range')
        self.lat = lat

    def __str__(self):
        tmp = self._str_coords()
        tmp += self.indent + '<heading>{}</heading>\n'.format(self.heading)


class KMLView(KMLObject):
    # Abstract class for View objects
    def __init__(self, time = None, viewerOptions = None, parent = None):
        super(KMLView, self).__init__(parent)
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


class Camera(KMLView, Heading):
    def __init__(self, lat = 0, lon = 0, alt = 0, heading = 0,tilt = 0, roll = 0, time = None, viewerOptions = None, parent = None):
        KMLView.__init__(time, viewerOptions, parent)
        Heading.__init__(lat, lon, alt, parent)
        if type(tilt) is not float:
            raise TypeError('Tilt must be a float')
        else:
            if -180.0 <= tilt <= 180.0:
                raise ValueError('Roll out of range')
        self.tilt = tilt
        if type(roll) is not float:
            raise TypeError('Roll must be a float')
        else:
            if -180.0 <= roll <= 180.0:
                raise ValueError('Roll out of range')
        self.roll = roll

    def __str__(self):
        tmp = self._str_coords()
        tmp += self.indent + '<heading>{}</heading>\n'.format(self.heading)










"""
class A(object):
    def __init__(self, a = 0):
        self.a = a

class B(object):
    def __init__(self, b = 0):
        self.b = b

class C(A,B):
    def __init__(self, a = 0, b = 0, c = 0):
        A.__init__(a)
        B.__init__(b)
        self.c = c

"""
