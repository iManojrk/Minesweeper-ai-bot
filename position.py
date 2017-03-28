class Position:
    def __init__(self, row, col=None):
        if isinstance(row, (Position, tuple, list)):
            self.row = row[0]
            self.col = row[1]
        else:
            self.row = row
            self.col = col

    @classmethod
    def cast(cls, obj):
        if isinstance(obj, cls):
            return obj
        else:
            return cls(obj)

    # This function is implemented as a way to allow tuple unwrapping that
    # is used in existing content. Example: r, c = position
    def __iter__(self):
        yield self.row
        yield self.col

    # This function is implemented as a way to allow index accessing using
    # tuple that is used in existing content. Example: r = position[0]
    def __getitem__(self, item):
        if item == 1:
            return self.col
        elif item == 0:
            return self.row
        else:
            raise KeyError

    def __len__(self):
        return 2

    def __str__(self):
        return "{{{}, {}}}".format(self.row, self.col)

    def __repr__(self):
        return "{{{}, {}}}".format(self.row, self.col)

    """Adds another position or tuple and returns a new Position Object"""
    def __add__(self, other):
        return Position(self.row + other[0], self.col + other[1])

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return Position(self.row - other[0], self.col - other[1])

    def __hash__(self, *args, **kwargs):
        return self.row << 16 + self.col

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.row == other.row and self.col == other.col
        else:
            try:
                return self.row == other[0] and self.col == other[1]
            except TypeError:
                return False

    def check_bounds(self, lower, upper):
        return (lower[0] <= self[0] < upper[0]
                and lower[1] <= self[1] < upper[1])

    @staticmethod
    def range(start, end=None):
        if end is None:
            end = start
            start = 0, 0
        yield from (Position(r, c)
                    for r in range(start[0], end[0])
                    for c in range(start[1], end[1]))
