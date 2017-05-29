from enum import Enum

class altitudeModeEnum(Enum):
    clampToGround = 0
    relativeToGround = 1
    absolute = 2

class gx_altitudeMode(Enum):
    clampToSeaFloor = 0
    relativeToSeaFloor = 1


class KMLObject(object):
    # Base class for primitive KML Object.  Creates and manages the parent and depth properties
    def __init__(self, parent = None):
        self.parent = parent
        self.depth = 0

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent):
        validParent = False
        if parent is not None:
            for base in parent.__class__.__bases__:
                if base is KMLContainer:
                    validParent = True
                    break
        if not validParent and parent is not None:
            raise TypeError('Parent object must be of type KMLContainer or NoneType')
        if parent is not None:
            self.__parent = parent
            self.depth = parent.depth + 1
        else:
            self.__parent = None
            self.depth = 0


class Snippet(KMLObject):
    # Snippet object - Optionally used in any Container object
    def __init__(self, content = None, maxLines = 1, parent = None):
        super(Snippet, self).__init(parent)
        self.content = '' if content is None else content
        self.maxLines = maxLines

    def __str__(self):
        return = (' ' * self.depth) + '<Snippet maxLines="{}">{}</Snippet>'.format(self.maxLines, self.content)


class TimePrimitive(KMLObject):
    # Base class for time objects.  Created the ID property
    def __init__(self, id = None, parent = None):
        super(TimePrimitive, self).__init(parent)
        self.id = id


class TimeSpan(TimePrimitive):
    # Timespan object
    def __init__(self, begin, end, id = None, parent = None):
        super(TimeSpan, self).__init(id, parent)
        self.begin = begin
        self.end = end

    def __str__(self):
        tmp = (' ' * self.depth) + '<TimeSpan'
        if id is not None:
            tmp += ' id="{}"'.format(self.id)
        tmp+='>\n'
        tmp += (' ' * self.depth) + ' <begin>{}</begin>\n'.format(self.begin)
        tmp += (' ' * self.depth) + ' <end>{}</end>\n'.format(self.end)
        tmp += (' ' * self.depth) + '</TimeSpan>\n'.format(self.begin)
        return tmp


class TimeStamp(TimePrimitive):
    # Timestamp object
    def __init__(self, when, id = None, parent = None):
        super(TimeSpan, self).__init(id, parent)
        self.when = when

    def __str__(self):
        tmp = (' ' * self.depth) + '<TimeStamp'
        if id is not None:
            tmp += ' id="{}"'.format(self.id)
        tmp+='>\n'
        tmp += (' ' * self.depth) + ' <when>{}</when>\n'.format(self.when)
        tmp += (' ' * self.depth) + '</TimeStamp>\n'
        return tmp

class KMLContainer(KMLObject):
    # Base class for primitive Container objects.  Manages a list (collection) of child objects.
    # Overrides the parent and depth properties.
    # Creates the many properties associated with a KML Feature object
    def __init__(self, parent = None, **kwargs):
        self.__children = []
        super(KMLContainer, self).__init__(parent)
        # Set the following properties to None.  KML Code will only be genreated if they are set
        for p in ['name', 'desc', 'visibility', 'open', 'snippet', 'address', 'phoneNumber', 'view', 'time', 'styleUrl', 'styleSelector', 'region', 'extendedData']
            setattr(self, p, None)
        # Update any properties passed in via kwargs
        for k in kwargs:
            if k in ['name', 'desc', 'visibility', 'open', 'snippet', 'address', 'phoneNumber', 'view', 'time', 'styleUrl', 'styleSelector', 'region', 'extendedData', 'parent']
                setattr(self, k, kwargs[k])

    def __str__(self):
        # This will be overridden by derived classes
        # Call another function to create KML code for any set parameters
        return self.__get_kml_parameters()

    def __get_kml_parameters(self):
        tmp = ''
        for p in ['name', 'desc', 'visibility', 'open', 'address', 'phoneNumber', 'styleUrl']
        if getattr(self, p) is not None:
            tmp += (' ' * self.depth) + ' <{}>{}</{}>\n'.format(p, getattr(self, p), p)
        if self.snippet is not None:
            tmp += (' ' * self.depth) + str(self.snippet)
        if self.view is not None:
            tmp += (' ' * self.depth) + str(self.view)
        if self.time is not None:
            tmp += (' ' * self.depth) + str(self.time)
        if self.styleSelector is not None:
            tmp += (' ' * self.depth) + str(self.styleSelector)
        if self.region is not None:
            tmp += (' ' * self.depth) + str(self.region)
        if self.extendedData is not None:
            tmp += (' ' * self.depth) + str(self.extendedData)

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent):
        if parent is not None:
            self.__parent = parent
            self.depth = parent.depth + 1
        else:
            self.__parent = None
            self.depth = 0
        for child in self.__children:
            child.depth = self.depth + 1

    @property
    def depth(self):
        return self.__depth

    @depth.setter
    def depth(self, d):
        self.__depth = d
        for child in self.__children:
            child.depth = self.__depth + 1

    def append(self, item):
        if type(item) is Document:
            raise TypeError('Document objects cannot be child objects')
        if item is not None:
            item.parent = self
        self.__children.append(item)

    def remove(self, item):
        self.__children.remove(item)

    def insert(self, position, item):
        if item is not None:
            item.parent = self
        self.__children.insert(position, item)

    def __len__(self):
        return len(self.__children)

    def __contains__(self, x):
        return x in self.__children

    def __iter__(self):
        for x in self.__children:
            yield x

    def __getitem__(self, index):
        return self.__children[index]

    def pop(self, index = 0):
        if len(self.__children) > 0:
            self.__children.pop(index)

#    def __next__(self):
#        self.__iter_counter +=1
#        if self.__iter_counter > len(self.__children):
#            raise StopIteration
#        yield self.__childrem[self.__iter_counter]



class Point(KMLObject):

    def __init__(self, lat, lon, alt = None, parent = None):
        super(Point, self).__init__(parent)
        if lat is None:
            raise ValueError('Latitude must not be None')
        if lon is None:
            raise ValueError('Longitude must not be None')
        if type(lat) not in [int, float]:
            raise TypeError('Latitude must be of type float or int, not {}'.format(type(lat).__name__))
        if type(lon) not in [int, float]:
            raise TypeError('Latitude must be of type float or int, not {}'.format(type(lon).__name__))
        if alt is not None:
            if type(alt) not in [int, float]:
                raise TypeError('Altitude must be None, of type float or int, not {}'.format(type(alt).__name__))
        self.lat = lat
        self.lon = lon
        self.alt = alt

    def __str__(self):
        tmp = (' ' * self.depth) + '<Point>\n'
        tmp += (' ' * self.depth) + ' <coordinates>{},{},{}</coordinates>\n'.format(self.lat, self.lon, 0 if self.alt is None else self.alt)
        tmp += (' ' * self.depth) + '</Point>\n'
        return tmp

    def __eq__(self, p):
        if self.lat == p.lat and \
           self.lon == p.lon and \
           self.alt == p.alt:
            return True
        return False

    def __ne__(self, p):
        if self.lat == p.lat and \
           self.lon == p.lon and \
           self.alt == p.alt:
            return False
        return True


class Folder(KMLContainer):

    def __init__(self, name, desc = None, ):
        super(Folder, self).__init__(name, desc)

    def __str__(self):
        tmp = (' ' * self.depth) + '<Folder>\n'
        tmp += self.__get_kml_parameters()
        for child in self:
            tmp = (' ' * self.depth) + str(child)
        tmp += (' ' * self.depth + '</Folder>\n'


class Document(KMLContainer):

    def __init__(self, name, desc):
        super(Document, self).__init__(name, desc)

    def __str__(self):
        tmp = (' ' * self.depth) + '<Document>\n'
        tmp += self.__get_kml_parameters()
        for child in self:
            tmp = (' ' * self.depth) + str(child)
        tmp += (' ' * self.depth + '</Document>\n'


class Placemark(KMLContainer):

    def __init__(self, name, desc = None, point = None, parent = None):
        super(Placemark, self).__init__(parent)

        self.append(point)

    def __str__(self):
        if self.point is None:
            raise ValueError('Point has not been set for Placemarker {}'.format(self.name))
        tmp = (' ' * self.depth) + '<Placemark>\n'
        tmp += self.__get_kml_parameters()
        tmp += (' ' * self.depth) + str(self.point)
        tmp += (' ' * self.depth) + '</Placemark>\n'
        return tmp

    def __eq__(self, p):
        return self.__point == p.point

    def __ne__(self, p):
        return self.__point != p.point

    def __bool__(self):
        if self.point is not None:
            return True
        return False

    @property
    def point(self):
        return self[0]

    @point.setter
    def point(self, point):
        self.pop()
        self.append(point)
        if self[0] is not None:
            self[0].parent = self


class LatLonBox(KMLObject):

    def __init__(self, north, south, east, west, rotation = 0, parent = None):
        super(LatLonBox, self).__init__(parent)
        if north > 90.0 or north < -90.0:
            raise ValueError('North out of bounds')
        if south > 90.0 or south < -90.0:
            raise ValueError('South out of bounds')
        if east > 180.0 or east < -180.0:
            raise ValueError('East out of bounds')
        if west > 180.0 or west < -180.0:
            raise ValueError('West out of bounds')
        if rotation > 0:                          # Counterclockwise rotation
            rotation = rotation % 360.0           # Remove full rotations (if any)
            if rotation > 180.0:                  # Check for greater than a semi-rotation
                rotation = rotation % -180.0      # reverse direction o rotation
        else:                                     # Clockwise rotation
            rotation = rotation % -360.0          # Remove full rotations (if any)
            if rotation < 180.0:                  # Check for greater than a semi-rotation
                rotation = rotation % 180.0       # Reverse direction of rotation
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.rotation = rotation

    def __contains__(self, p):
        return self.__check_lat_lon(p)

    def __check_lat_lon(self, p):
        inside_lon = False
        if self.north > self.south:
            if p.lon <= self.north and p.lon >= self.south:
                inside_lon = True
        else:
            if p.lon >= self.north and p.lon <= self.south:
                inside_lon = True
        inside_lat = False
        if self.east > self.west:
            if p.lat <= self.east and p.lat >= self.west:
                inside_lat = True
        else:
            if p.lat >= self.east and p.lat <= self.west:
                inside_lat = True
        return (inside_lon and inside_lat)

    def __str__(self):
        tmp = (' ' * self.depth) + '<LatLonBox>\n'
        tmp += (' ' * self.depth) + ' <north>{}</north>\n'.format(self.north)
        tmp += (' ' * self.depth) + ' <south>{}</south>\n'.format(self.south)
        tmp += (' ' * self.depth) + ' <east>{}</east>\n'.format(self.east)
        tmp += (' ' * self.depth) + ' <west>{}</west>\n'.format(self.west)
        tmp += (' ' * self.depth) + ' <rotation>{}</rotation>\n'.format(self.rotation)
        tmp += (' ' * self.depth) + '</LatLonBox>\n'

class LatLonAltBox(LatLonBox):

    def __init__(self, north, south, east, west, rotation = 0, minAlt = 0, maxAlt = 0, altMode = None, parent = None):
        super(LatLonAltBox, self).__init__(north, south, east, west, rotation, parent)
        self.minAlt = minAlt
        self.maxAlt = maxAlt
        if altMode is not None:
            if type(altMode) in [altitudeModeEnum, gx_altitudeMode]:
                self.altMode = altMode
            else:
                raise TypeError('altMode must be of type altModeEnum, gx_altMode or NoneType')
        else:
            self.altMode = None

    def __contains__(self, p):
        latlon = self.__check_lat_lon
        alt = False
        if self.minAlt == self.maxAlt == 0:
            alt = True
        else:
            if p.alt > self.minAlt and p.alt < self.maxAlt:
                alt = True
        return (latlon and alt)

class KMLFile(KMLContainer):

    def __init__(self):
        super(KMLFile, self).__init__(None)

    def __str__(self):
        tmp = '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        for child in self:
            tmp += str(child)
        tmp+='</kml>\n'
        return tmp

#    @KMLContainer.parent.setter
#    def parent(self, parent):
        # Document objects are the root object and cannot have a parent
#        pass

