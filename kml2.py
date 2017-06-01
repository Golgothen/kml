import logging
logger = logging.getLogger()
# Remove after testing
f = logging.Formatter('%(levelname)-8s:%(funcName)-20s %(lineno)-5s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(f)
logger.addHandler(h)
logger.setLevel(logging.DEBUG)

from types import *
from abstracts import *

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








