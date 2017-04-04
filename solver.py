from itertools import compress
from random import randrange

from common import Result, Content, UniqueStack
from game_engine import GameEngine
from list2d import View2D
from position import Position


class MinesweeperSolver:
    def __init__(self, game_engine: GameEngine):
        self._engine = game_engine
        self._engine.update_event.add(self._on_cell_update)
        self._explore_stack = UniqueStack()
        self._enum_stack = UniqueStack()
        self._count_simple = 0
        self._count_enum = 0
        self._count_random = 0
        self._loss_by = ''

    def _on_cell_update(self, r, c):
        position = Position(r, c)
        value = self._engine.minefield[position]
        if value.is_number() or value == Content.Flag:
            self._explore_stack.push_all(
                position_i for position_i
                in self._engine.minefield.positions_around(position)
                if (self._engine.minefield[position_i].is_number())
            )
            if value > Content.NoMine:
                self._explore_stack.push(position)

    def reset(self):
        self._explore_stack.clear()
        self._enum_stack.clear()
        self._count_simple = 0
        self._count_enum = 0
        self._count_random = 0
        self._loss_by = ''

    def solve(self):
        if self._explore_stack and self._simple_explore():
            self._count_simple += 1
            if self._engine.result == Result.Loss:
                self._loss_by = 'Simple Explore'
        elif self._enum_stack and self._enumerate_models():
            self._count_enum += 1
            if self._engine.result == Result.Loss:
                self._loss_by = 'Model Enumeration'
        else:
            self._explore_random_index()
            self._count_random += 1
            if self._engine.result == Result.Loss:
                self._loss_by = 'Random Explore'
        if self._engine.result != Result.OK:
            print('Counts:')
            print('Simple Explore:', self._count_simple)
            print('Model Enumeration:', self._count_enum)
            print('Random Explore:', self._count_random)
            if self._loss_by:
                print('Loss By:', self._loss_by)
            with open('minesweeper-stats.csv', 'a') as file:
                print(self._count_simple, self._count_enum,
                      self._count_random, self._loss_by, sep=',', file=file)

    def _simple_explore(self):
        while self._explore_stack:
            current_position = self._explore_stack.pop()
            r, c = current_position
            if self._engine.minefield[r][c] <= Content.NoMine:
                continue

            unknowns = sum(self._engine.is_unknown(ri, ci) for ri, ci
                           in self._engine.cells_around(r, c))
            if not unknowns:  # skip if there are no unknowns
                continue
            flags = sum(self._engine.minefield[ri][ci] == Content.Flag
                        for ri, ci in self._engine.cells_around(r, c))
            if flags == self._engine.minefield[r][c]:
                for position in (position for position
                                 in self._engine.cells_around(r, c)
                                 if self._engine.is_unknown(*position)):
                    self._engine.dig(*position)
                return True
            if flags + unknowns == self._engine.minefield[r][c]:
                for position in (position for position
                                 in self._engine.cells_around(r, c)
                                 if self._engine.is_unknown(*position)):
                    self._engine.set_flag(*position, Content.Flag)
                return True
            self._enum_stack.push(current_position)
        return False

    def _explore_random_index(self):
        if self._engine.result == Result.OK:
            while True:
                r = randrange(self._engine.rows)
                c = randrange(self._engine.cols)
                if self._engine.is_unknown(r, c):
                    return self._engine.dig(r, c)

    def _enumerate_models(self):
        while self._enum_stack:
            position = self._enum_stack.pop()
            if not self._engine.minefield[position].is_open():
                continue
            unknowns = sum(
                self._engine.minefield[position_i].is_unknown()
                for position_i in self._engine.cells_around(*position)
            )
            # skip if there are no unknown cells
            # or if there are no known cells around
            if unknowns == 0:
                continue

            # Extracting the contents in the 5x5 area around the current cell
            position_start = self._engine.minefield.apply_bounds(
                position - (2, 2))

            position_end = self._engine.minefield.apply_bounds(
                position + (3, 3))

            mines, non_mines = self.get_mines_nonmines(
                View2D(self._engine.minefield, position_start, position_end),
                position
            )
            if mines or non_mines:
                for position_i in mines:
                    self._engine.set_flag(*position_i, Content.Flag)
                for position_i in non_mines:
                    self._engine.dig(*position_i)
                return True
        return False

    @classmethod
    def get_mines_nonmines(cls, view, position_i):
        interior_start = view.apply_bounds(position_i - (1, 1))
        interior_end = view.apply_bounds(position_i + (2, 2))

        # gets interior positions to be enumerated
        interior_positions = [
            position_i
            for position_i in view.range(interior_start, interior_end)
            if view[position_i] == Content.Unknown
        ]

        exterior_positions = [
            position_i
            for position_i in view.all_positions()
            if (view[position_i] == Content.Unknown
                and not position_i.check_bounds(interior_start, interior_end))
        ]
        cls._add_check_cells(exterior_positions, view)

        flags = sum(content == Content.Flag
                    for content in view.contents_around(position_i))
        totals = [0 for _ in interior_positions]
        count = 0
        for interior_model in cls._get_interior_models(
                view, view[position_i] - flags, interior_positions):
            if (cls.is_model_valid(interior_model,
                                   interior_start, interior_end)
                and cls._has_exterior_model(
                    interior_model, exterior_positions,
                    interior_start, interior_end)):
                count += 1
                for i, position_i in enumerate(interior_positions):
                    if interior_model[position_i] == Content.Flag:
                        totals[i] += 1
                if all(i != count for i in totals) and all(totals):
                    for position_i in interior_positions:
                        view[position_i] = Content.Unknown
                    return False, False
        for position_i in interior_positions:
            view[position_i] = Content.Unknown
        return (
            list(compress(interior_positions, (i == count for i in totals))),
            list(compress(interior_positions, (i == 0 for i in totals)))
        )

    @staticmethod
    def is_model_valid(view, interior_start, interior_end):
        grid = view.list2d
        for pos_i in view.all_positions():
            if grid[pos_i].is_number():
                flags_around_i = sum(
                    grid[pos_j] == Content.Flag
                    for pos_j in grid.range(pos_i - (1, 1), pos_i + (2, 2))
                )
                if flags_around_i > grid[pos_i]:
                    return False
                if flags_around_i == grid[pos_i]:
                    continue
                unknowns_around_i = sum(
                    grid[pos_j].is_unknown()
                    for pos_j in grid.range(pos_i - (1, 1),
                                            pos_i + (2, 2))
                    if not pos_j.check_bounds(interior_start,
                                              interior_end)
                )
                if flags_around_i + unknowns_around_i < grid[pos_i]:
                    return False
        return True

    @classmethod
    def _get_interior_models(cls, grid, flag_count, cells, cell_index=0):
        if cell_index == len(cells):
            yield grid
            return
        if flag_count == 0:
            for position in cells[cell_index:]:
                grid[position] = Content.Unknown
            yield grid
            return

        if len(cells) - cell_index > flag_count:
            grid[cells[cell_index]] = Content.Unknown
            yield from cls._get_interior_models(
                grid, flag_count, cells, cell_index + 1)

        grid[cells[cell_index]] = Content.Flag
        yield from cls._get_interior_models(
            grid, flag_count - 1, cells, cell_index + 1)

    @classmethod
    def _has_exterior_model(cls, view, cells, interior_start, interior_end):
        result = cls._has_exterior_model_impl(
            view, cells, interior_start, interior_end, 0
        )
        for position, check_cells in cells:
            view[position] = Content.Unknown
        return result

    @classmethod
    def _has_exterior_model_impl(cls, view, cells, interior_start,
                                 interior_end, index):
        if index == len(cells):
            return True
        if (cls._apply_and_validate(Content.Unknown, view, cells,
                                    interior_start, interior_end, index)
            and cls._has_exterior_model_impl(view, cells, interior_start,
                                             interior_end, index + 1)):
            return True
        if cls._apply_and_validate(Content.Flag, view, cells, interior_start,
                                   interior_end, index):
            return cls._has_exterior_model_impl(
                view, cells, interior_start, interior_end, index + 1
            )

    @staticmethod
    def _apply_and_validate(content, view, cells, interior_start, interior_end,
                            index):
        grid = view.list2d
        cell, check_cells = cells[index]
        grid[cell] = content
        for check_cell in check_cells:
            flag_count = sum(
                grid[position] == Content.Flag
                for position in grid.positions_around(check_cell)
            )
            if check_cell.check_bounds(interior_start, interior_end):
                if flag_count != grid[check_cell]:
                    return False
            else:
                if flag_count > grid[check_cell]:
                    return False
                if flag_count == grid[check_cell]:
                    continue
                unknowns = sum(
                    grid[pos_i].is_unknown()
                    for pos_i in grid.range(check_cell - (1, 1),
                                            check_cell + (2, 2))
                    if not pos_i.check_bounds(view.lower,
                                              view.upper)
                )
                if flag_count + unknowns < grid[check_cell]:
                    return False
        return True

    """ Adds all cells that need to be checked when a cell is marked or
    unmarked. It does by checking all cells that need to be checked for the
    last cell to be updated and ignoring those cells from being checked when
    any other cell is updated. This is done iteratively.
    """

    @staticmethod
    def _add_check_cells(cells, grid):
        ignore_cells = set()
        current_cells = set()
        for i in range(len(cells) - 1, -1, -1):
            current_cells.clear()
            current_cells.update(
                cell_j
                for cell_j in grid.positions_around(cells[i])
                if grid[cell_j].is_number()
            )
            if current_cells:
                current_cells -= ignore_cells
                cells[i] = cells[i], list(current_cells)
                ignore_cells |= current_cells
            else:
                del cells[i]
