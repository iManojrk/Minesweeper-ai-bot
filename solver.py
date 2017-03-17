from random import randrange

from common import Result, Content, UniqueStack
from game_engine import GameEngine


class MinesweeperSolver:
    def __init__(self, game_engine: GameEngine):
        self._engine = game_engine
        self._engine.update_event.add(self._on_cell_update)
        self._explore_stack = UniqueStack()

    def _on_cell_update(self, r, c):
        value = self._engine.minefield[r][c]
        if value > Content.NoMine or value == Content.Flag:
            # (self.engine.minefield[rj][cj] > Content.NoMine) equivalent to
            # check for numbers in the cell (rj,cj)
            self._explore_stack.push_all((rj, cj) for rj, cj
                                         in self._engine.cells_around(r, c)
                                         if (self._engine.minefield[rj][cj] >
                                             Content.NoMine))
            if value > Content.NoMine:
                self._explore_stack.push((r, c))

    def solve(self):
        if not self._explore_stack or not self._simple_explore():
            self._explore_random_index()

    def _simple_explore(self):
        while self._explore_stack:
            r, c = self._explore_stack.pop()
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
        return False

    def _explore_random_index(self):
        if not self._explore_stack and self._engine.result == Result.OK:
            while True:
                r = randrange(self._engine.rows)
                c = randrange(self._engine.cols)
                if self._engine.is_unknown(r, c):
                    return self._engine.dig(r, c)
