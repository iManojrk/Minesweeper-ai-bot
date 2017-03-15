from random import randrange

from common import Result, Content
from game_engine import GameEngine


class MinesweeperSolver:
    def __init__(self, game_engine: GameEngine):
        self.engine = game_engine
        self.engine.update_event.add(self.on_cell_update)
        self.explore_stack = []

    def on_cell_update(self, r, c):
        value = self.engine.minefield[r][c]
        if value > Content.NoMine or value == Content.Flag:
            self.explore_stack.extend((rj, cj) for rj, cj in self.engine.cells_surrounding(r, c)
                                      if self.engine.minefield[rj][cj] > Content.NoMine)
            if len(self.explore_stack) > 3 * self.engine.rows * self.engine.cols:
                self.explore_stack = list(set(self.explore_stack))
        if value > Content.NoMine:
            self.explore_stack.append((r, c))

    def solve(self):
        if not self.explore_stack or not self.simple_explore():
            self._explore_random_index()

    def simple_explore(self):
        while self.explore_stack:
            r, c = self.explore_stack.pop()
            if self.engine.minefield[r][c] <= Content.NoMine:
                continue

            unknowns = sum(self.engine.is_unknown(ri, ci)
                           for ri, ci in self.engine.cells_surrounding(r, c))
            if not unknowns:  # skip if there are no unknowns
                continue
            flags = sum(self.engine.minefield[ri][ci] == Content.Flag
                        for ri, ci in self.engine.cells_surrounding(r, c))
            if flags == self.engine.minefield[r][c]:
                for position in (position for position in self.engine.cells_surrounding(r, c)
                                 if self.engine.is_unknown(*position)):
                    self.engine.dig(*position)
                return True
            if flags + unknowns == self.engine.minefield[r][c]:
                for position in (position for position in self.engine.cells_surrounding(r, c)
                                 if self.engine.is_unknown(*position)):
                    self.engine.set_flag(*position, Content.Flag)
                return True
        return False

    def _explore_random_index(self):
        if not self.explore_stack and self.engine.result == Result.OK:
            while True:
                r = randrange(self.engine.rows)
                c = randrange(self.engine.cols)
                if self.engine.is_unknown(r, c):
                    return self.engine.dig(r, c)
