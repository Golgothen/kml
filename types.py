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

