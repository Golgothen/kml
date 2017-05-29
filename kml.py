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
        self.parent = parent
        if self.parent is not None:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

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

class Placemark(object):
    def __init__(self, name, desc = None, point = None, parent = None):
        if name is None:
            raise ValueError('Name must not be None')
        if name == '':
            raise ValueError('Name must contain a value')
        self.name = name
        self.desc = '' if desc is None else desc
        self.parent = parent
        if self.parent is None:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1
        self.point = point
        if self.point is not None:
            self.point.depth = self.depth + 1

    def __str__(self):
        if self.point is None:
            raise ValueError('Point value has not been set')
        tmp = (' ' * self.depth) + '<Placemark>\n'
        tmp += (' ' * self.depth) + ' <name>{}</name>\n'.format(self.name)
        tmp += (' ' * self.depth) + ' <description>{}</description>\n'.format(self.desc)
        tmp += (' ' * self.depth) + str(self.point)
        tmp += (' ' * self.depth) + '</Placemark>\n'
        return tmp

    def __eq__(self, p):
        return self.point == p.point

    def __ne__(self, p):
        return self.point != p.point

class Document(object):
    def __init__(self):
        self.__list = []

    def append(self, item):
        self.__list.append(item)

    def remove(self, item):
        self.__list.remove(item)

    def insert(self, position, item):
        self.__list.insert(position, item)

    def __len__(self):
        return len(self.__list)

    def __contains__(self, x):
        return x in self.__list

    def __iter__(self):
        self.__iter_counter = 0
        return self.__list[self.__iter_counter]

    def __next__(self):
        self.__iter_counter +=1
        if self.__iter_counter > len(self.__list):
            raise StopIteration
        return self.__list[self.__iter_counter]
