import numpy

class Var(object):
    def __init__(self, name, vtype):
        self.name = name
        self.type = vtype
        self.storage = numpy.zeros(1, dtype=vtype)

    def reset(self):
        self.storage[0] = -999

    def fill(self, val):
        self.storage[0] = val

    def add(self, val):
        self.storage[0] += val

    def __str__(self):
        return 'Var: name={}, vtype={}, val={:.2f}'.format(self.name, self.type, self.storage[0])
