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
        yield from (
            self[position_i]
            for position_i in self.positions_around(position)
        )
