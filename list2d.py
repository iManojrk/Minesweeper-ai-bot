from position import Position


class List2D(list):
    def __getitem__(self, item):
        if isinstance(item, (Position, tuple, list)):
            return super().__getitem__(item[0])[item[1]]

        if (isinstance(item, int)
            or (hasattr(item, 'start')
                and isinstance(getattr(item, 'start'), int))):
            return super().__getitem__(item)
        # self.get_from_slice(item)

    def get_from_slice(self, item):
        start = self.apply_bounds(item.start)
        if item.stop is None:
            stop = start
            start = Position(0, 0)
        else:
            stop = self.apply_bounds(item.stop)
        step = item.step
        if item.step is None:
            step = Position(1, 1)
        raise NotImplemented

    def __setitem__(self, key, value):
        if isinstance(key, int):
            super().__setitem__(key, value)
        else:
            super().__getitem__(key[0])[key[1]] = value

    def size(self):
        return Position(len(self), len(self[0]))

    def apply_bounds(self, position):
        size = self.size()
        if 0 <= position[0] < size.row and 0 <= position[1] < size.col:
            return Position.cast(position)
        return Position(max(0, min(position[0], size.row)),
                        max(0, min(position[1], size.col)))

    def range(self, begin, end):
        return (
            position
            for position in Position.range(self.apply_bounds(begin),
                                           self.apply_bounds(end))
        )

    def positions_around(self, position):
        size = self.size()
        position = Position.cast(position)
        return (
            Position(ri, ci)
            for ri in range(max(0, position.row - 1),
                            min(size.row, position.row + 2))
            for ci in range(max(0, position.col - 1),
                            min(size.col, position.col + 2))
            if ri != position.row or ci != position.col
        )

    def contents_around(self, position):
        return (
            self[position_i]
            for position_i in self.positions_around(position)
        )


class View2D:
    """ Encapsulates List2D object and offers a defined window of view into 
    the List2D object - like a subsection of the List2D"""
    def __init__(self, list2d, lower, upper):
        self.list2d = list2d
        self.lower = Position.cast(lower)
        self.upper = Position.cast(upper)

    def __getitem__(self, item):
        return self.list2d[item]

    def __setitem__(self, key, value):
        self.list2d[key] = value

    def __getattr__(self, item):
        return getattr(self.list2d, item)

    def __setattr__(self, key, value):
        if key != 'list2d' and 'lower' != key != 'upper':
            setattr(self.list2d, key, value)
        else:
            self.__dict__[key] = value

    def positions_around(self, position):
        position = Position.cast(position)
        return (
            Position(ri, ci)
            for ri in range(max(self.lower.row, position.row - 1),
                            min(self.upper.row, position.row + 2))
            for ci in range(max(self.lower.col, position.col - 1),
                            min(self.upper.col, position.col + 2))
            if ri != position.row or ci != position.col
        )

    def apply_bounds(self, position):
        if Position.check_bounds(position, self.lower, self.upper):
            return Position.cast(position)
        return Position(max(self.lower.row, min(position[0], self.upper.row)),
                        max(self.lower.col, min(position[1], self.upper.col)))

    def all_positions(self):
        return Position.range(self.lower, self.upper)

    range = List2D.range
    contents_around = List2D.contents_around
