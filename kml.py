class Point(object):
    def __init__(self, lat, lon, alt, parent = None):
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
        self.__parent = parent
        if self.__parent is not None:
            self.depth = self.__parent.depth + 1
        else:
            self.depth = 0

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent):
        self.__parent = parent
        if self.__parent is not None:
            self.depth = self.__parent.depth + 1
        else:
            self.depth = 0

    def __str__(self):
        tmp = (' ' * self.depth) + '<Point>\n'
        tmp += (' ' * self.depth) + '  <coordinates>{},{},{}</coordinates>\n'.format(self.lat, self.lon, 0 if self.alt is None else self.alt)
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

class Placemark(object):
    def __init__(self, name, desc = None, point = None, parent = None):
        if name is None:
            raise ValueError('Name must not be None')
        if name == '':
            raise ValueError('Name must contain a value')
        self.name = name
        self.desc = '' if desc is None else desc
        self.__parent = parent
        if self.__parent is None:
            self.__depth = 0
        else:
            self.__depth = self.__parent.depth + 1
        self.__point = point

    def __str__(self):
        if self.point is None:
            raise ValueError('Point value has not been set for Placemarker {}'.format(self.name))
        tmp = (' ' * self.__depth) + '<Placemark>\n'
        tmp += (' ' * self.__depth) + ' <name>{}</name>\n'.format(self.name)
        tmp += (' ' * self.__depth) + ' <description>{}</description>\n'.format(self.desc)
        tmp += (' ' * self.__depth) + str(self.__point)
        tmp += (' ' * self.__depth) + '</Placemark>\n'
        return tmp

    def __eq__(self, p):
        return self.__point == p.point

    def __ne__(self, p):
        return self.__point != p.point

    @property
    def depth(self):
        return self.__depth

    @depth.setter
    def depth(self, depth):
        self.__depth = depth
        if self.__point is not None:
            self.__point.depth = self.__depth + 1

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent):
        self.__parent = parent
        if self.__parent is not None:
            self.depth = self.__parent.depth + 1
        else:
            self.depth = 0

    @property
    def point(self):
        return self.__point

    @point.setter
    def point(self, point):
        self.__point = point
        if self.__point is not None:
            self.__point.depth = self.__depth + 1

class LatLonBox(object):
    def __init__(self, north, south, east, west, rotation = None, parent = None):
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
        if parent is not None:
            self.__parent = parent
            self.depth = self.__parent.depth + 1

    def __contains__(self, p):
        inside_lon = False
        if self.north > self.south:
            if p.lon < self.north and p.lon > self.south:
                inside_lon = True
        else:
            if p.lon > self.north and p.lon < self.south:
                inside_lon = True
        inside_lat = False
        if self.east > self.west:
            if p.lat < self.east and p.lat > self.west:
                inside_lat = True
        else:
            if p.lat > self.east and p.lat < self.west:
                inside_lat = True
        return (inside_lon and inside_lat)

class Document(object):
    def __init__(self):
        self.__list = []
        self.depth = 0

    def append(self, item):
        item.parent = self
        self.__list.append(item)

    def remove(self, item):
        self.__list.remove(item)

    def insert(self, position, item):
        item.parent = self
        self.__list.insert(position, item)

    def __len__(self):
        return len(self.__list)

    def __contains__(self, x):
        return x in self.__list

    def __iter__(self):
        self.__iter_counter = 0
        for x in self.__list:
            yield x #self.__list[self.__iter_counter]

    def __getitem__(self, index):
        return self.__list[index]

#    def __next__(self):
#        self.__iter_counter +=1
#        if self.__iter_counter > len(self.__list):
#            raise StopIteration
#        yield self.__list[self.__iter_counter]

    def __str__(self):
        tmp = '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        for l in self.__list:
            tmp += str(l)
        tmp+='</kml>\n'
        return tmp

