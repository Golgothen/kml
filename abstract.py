import logging
logger = logging.getLogger()
from inspect import getmro
from enum import Enum, EnumMeta

################################################################################################
#                                                                                              #
#   KML Abstract Object definitions (base classes)                                             #
#                                                                                              #
################################################################################################


class KMLObject(object):

    def __init__(self, permittedAttributes):
        logging.debug('KMLObject created')
        #self.__parent = None
        self.__id = None
        self.__attributes = {}
        self.__depth = 0
        self.__permittedAttributes = permittedAttributes
    
    @property
    def indent(self):
        return ' ' * self.depth
    
    @property
    def depth(self):
        return self.__depth
    
    @depth.setter
    def depth(self, value):
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
        if key in self.__permittedAttributes:
            if key not in attributeTypes:
                raise RuntimeError('Type for attribute {} not defined'.format(key))
            if EnumMeta in getmro(attributeTypes[key].__class__):
                logger.debug('Attribute type of Enum')
                # Enums are created slightly different than objects
                if number.isInt(value):
                    self.__attributes[key] = attributeTypes[key](int(value))
                else:
                    self.__attributes[key] = attributeTypes[key][str(value).lower()]
            elif KMLObject in getmro(attributeTypes[key].__class__):
                logger.debug('Attribute type of KMLObject')
                # Setting an object as an attribute increases is indentation
                self.__attributes[key] = attributeTypes[key](value)
                self.__attributes[key].depth = self.depth + 1
            else:
                logger.debug('Standard attribute type')
                self.__attributes[key] = attributeTypes[key](value)
        else:
            logging.debug('Attibute {} not permitted at {}'.format(key, self.__class__.__name__))
    def __delitem__(self, key):
        del self.__attributes[key]
    
    def __str__(self):
        tmp = ''
        for a in self.__attributes:
            if KMLObject in getmro(self.__attributes[a].__class__):
                # Objects handle their own code formatting and indentation
                tmp += str(self.__attributes[a])
            else:
                # Simple attributes and be easily formatted
                tmp += self.indent + ' <{}>{}</{}>\n'.format(a,str(self.__attributes[a]),a)
        return tmp

class KMLFeature(KMLObject):
    def __init__(self):
        super().__init__(['name','description','visibility','open','atom:link'])
    
    def __str__(self):
        return super().__str__()

class ATOMLink(KMLObject):
    # atom:link is a special case.  It has the link value inside the tag.  No other attributes permitted
    def __init__(self):
        self.link = None
        super().__init__()
    
    def __str__(self):
        return self.indent + '<atom:link href="{}" />\n'.format(self.link)
    
