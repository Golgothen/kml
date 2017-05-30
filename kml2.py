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
            tmp += (' ' * self.depth) + str(e)
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
        #if type(item) is Document:
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

    def find(self, x):
        for e in self.__elements:
            if x.__class__.__name__ == e.__class__.__name__ == 'Attribute':
                # Compare attributes by name to find the right one
                if e.name == x.name:
                    return e
            else:
                if x.__class__.__name__ == e.__class__.__name__:
                    return e

    def replace(self, item):
        self[self.index(self.find(item))] = item

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

#    def pop(self, index = 0):
        # Used to delete an element by index
#        if len(self.__elements) > 0:
#            self.__elements.pop(index)


class Attribute(KMLObject):

    def __init__(self, name, value, parent = None):
        super(Attribute, self).__init__(parent)
        self.name = name
        self.value = value
        logging.debug('Element created'.format(name))

    def __str__(self):
        return (' ' * self.depth) + '<{}>{}</{}>\n'.format(self.name, self.value, self.name)

#    def __eq__(self, x):
        # When comparing attributes, compare by name rather than value
#        if self.__class__.__name__ != x.__class__.__name__:
#            return False
#        logger.debug('Attribute compare result {}'.format(self.name == x.name))
#        return self.name == x.name

class AtomLink(Attribute):
    def __init__(self, url, parent = None):
        super(Attribute, self).__init__('atom:link', url, parent)

    def __str__(self):
        # Overload the output format of the atom:link attribute
        return (' ' * self.depth) + '<{} href="{}"/>\n'.format(self.name, self.value)

class AtomAuthor(Attribute):
    def __init__(self, value, parent = None):
        super(Attribute, self).__init__('atom:author', value, parent)

    def __str__(self):
        # Overload the output format of the atom:author attribute
        # TODO: According to KML documentation, atom:author does not have a close tag.
        #       Not sure if this is correct or a typo in the documentation.
        # As per documentation:
        return (' ' * self.depth) + '<{}>{}<{}>\n'.format(self.name, self.value, self.name)

class Snippet(KMLObject):
    # Snippet object - Optionally used in any Container object
    def __init__(self, content = None, maxLines = 1, parent = None):
        super(Snippet, self).__init(parent)
        self.content = '' if content is None else content
        self.maxLines = maxLines

    def __str__(self):
        return (' ' * self.depth) + '<Snippet maxLines="{}">{}</Snippet>'.format(self.maxLines, self.content)


class KMLFeature(KMLContainer):

    # KML Feature object.
    def __init__(self, **kwargs):
        # parent is passed in kwargs.  Declare the super with None for the parent for now
        super(KMLFeature, self).__init__(None)
        self.setAttribute(**kwargs)

        for k in kwargs:
            # Check for parent
            if k == 'parent':
                self.parent = k['parent']
            # check string types
            if k in ['name', 'description', 'phoneNumber', 'xal:AddressDetails']:
                self.append(Attribute(k, kwargs[k], self))
            # Check boolean types
            if k in ['visibility', 'open']:
                # '0' values are concidered false, all other values concidered true
                if str(kwargs[k]) == '0':
                    self.append(Attribute(k, '0', self))
                else:
                    self.append(Attribute(k, '1', self))
            # Check object types
            if k in ['atom:author', 'atom:link', 'snippet', 'view', 'time', 'styleSelector', 'region', 'extendedData']:
                # Append objects directly to the collection
                self.append(kwarks[k])

    def setAttribute(self, **kwargs):
        for k in kwargs:
            # Check for parent
            if k == 'parent':
                self.parent = k['parent']
            # check string types
            if k in ['name', 'description', 'phoneNumber', 'xal:AddressDetails']:
                tempObj = Attribute(k, kwargs[k], self)
            # Check boolean types
            if k in ['visibility', 'open']:
                # '0' values are concidered false, all other values concidered true
                if str(kwargs[k]) == '0':
                     tempObj = Attribute(k, '0', self)
                else:
                     tempObj = Attribute(k, '1', self)
            # Check object types
            if k in ['atom:author', 'atom:link', 'snippet', 'view', 'time', 'styleSelector', 'region', 'extendedData']:
                # Append objects directly to the collection
                 tempObj = kwarks[k]
            
