class KMLObject(object):
    # Base class for primitive KML Object.  Creates and manages the parent and depth properties
    # Introduces the ID attribute
    def __init__(self, parent = None):
        logging.debug('KMLObject created')
        self.depth = 0
        self.__parent = None
        self.parent = parent
        self.__id = None

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

    def __init__(self, parent = None):
        self.__elements = []
        super().__init__(parent)
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


class KMLFeature(KMLContainer):

    # KML Feature object.
    def __init__(self, **kwargs):
        # parent can be passed in kwargs.  Declare the super with None for the parent for now
        super().__init__(None)
        self.__attributes = {}
        self.set(**kwargs)
        logging.debug('KMLFeature created')

    def set(self, **kwargs):
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
            if k in ['name', 'description', 'phoneNumber', 'xal:AddressDetails','atom:author', 'atom:link', 'snippet', 'view$
                self.__attributes[k] = kwargs[k]
            logging.debug('KMLFeature attribute {} set to {}'.format(k, kwargs[k]))

    def get(self, attr):
        return self.__attributes[attr]

    def append(self, item):

        # Override superclass append method

        #if type(item) is Document: TODO: Uncomment this later
        #    raise TypeError('Document objects cannot be child objects')
        if item is not None:
            if type(item).name in ['Snippet']: #, 'Camera', 'time', 'styleSelector', 'region', 'extendedData']:
                self.__attributes[type(item).name.lower] = item
                logging.debug('KMLFeature adding {} to collection'.format(type(item).name))
            elif item in ['name', 'description', 'phoneNumber', 'xal:AddressDetails','atom:author', 'atom:link', 'visibility$
                self.__attributes[type(item).name.lower] = item
                logging.debug('KMLFeature adding {} to collection'.format(type(item).name))
            else:
                super().append(item)

    def insert(self, position, item):
        if item is not None:
            if type(item).name in ['Snippet']: #, 'Camera', 'time', 'styleSelector', 'region', 'extendedData']:
                pass #self.__attributes[type(item).name.lower] = item
            elif item in ['name', 'description', 'phoneNumber', 'xal:AddressDetails','atom:author', 'atom:link', 'visibility$
                pass #self.__attributes[type(item).name.lower] = item
            else:
                super().insert(position, item)

    def remove(self, item):
        if item is not None:
            if type(item).name in ['Snippet']: #, 'Camera', 'time', 'styleSelector', 'region', 'extendedData']:
                pass #self.__attributes[type(item).name.lower] = item
            elif item in ['name', 'description', 'phoneNumber', 'xal:AddressDetails','atom:author', 'atom:link', 'visibility$
                pass #self.__attributes[type(item).name.lower] = item
            else:
                super().remove(item)

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

