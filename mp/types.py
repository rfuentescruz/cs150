class RSObject(object):
    TYPE = 'UNKNOWN'

    def __init__(self, value):
        self._value = None
        self.set_value(value)

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def del_value(self):
        del self._value

    value = property(set_value, get_value, del_value, 'Object value')

    def add(self, other):
        raise NotImplementedError()

    def sub(self, other):
        raise NotImplementedError()

    def get_index(self, index):
        raise NotImplementedError()

    def set_index(self, index, value):
        raise NotImplementedError()

class Integer(RSObject):
    TYPE = 'INTEGER'

    def set_value(self, value):
        self._value = int(value)

    def add(self, other):
        if not isinstance(other, Integer):
            return other.add(self)

        return Integer(self.value + other.value)


class Float(RSObject):
    TYPE = 'FLOAT'

    def set_value(self, value):
        self._value = float(value)

    def add(self, other):
        if not isinstance(other, Float):
            return other.add(self)

        return Float(self.value + other.value)


class List(RSObject):
    TYPE = 'LIST'

    def set_value(self, value):
        self._value = list(value)

    def add(self, other):
        if not isinstance(other, List):
            raise TypeError(
                'Addition not supported for %s and %s' % (self.TYPE, other.TYPE)
            )

        return List(self.value + other.value)

    def get_index(self, index):
        if not isinstance(index, Integer):
            raise TypeError('Only %s can be used as index' % Integer.TYPE)

        i = index.value

        if isinstance
        if i < 0:
            raise ValueError(
                'Negative indexes (%d) not supported for %s' % (i, self.TYPE)
            )

        return self.value[index]

    def set_index(self, index, value):
        self.value[index] = value


class String(List):
    TYPE = 'STRING'

    def set_value(self, value):
        value = list(value)
        for c in value:
            if not isinstance(c, str):
                raise ValueError(
                    'Strings can only be a list of characters / strings'
                )

        return self._value = value
