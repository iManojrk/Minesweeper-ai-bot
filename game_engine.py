from random import randrange

from ai.minesweeper.common import Event, Result, Content


class GameEngine:
    def __init__(self, game=None):
        self.update_event = Event()
        self.flags_changed_event = Event()
        self.game_over_event = Event()
        self.result = Result.OK
        if isinstance(game, int):
            self.rows, self.cols, self.mine_count = [[8, 8, 10], [16, 16, 40], [16, 30, 99]][game]
        else:
            self.rows, self.cols, self.mine_count = (int(s) for s in input().split())
        self._flags = 0
        self._mines = None
        self.minefield = None
        self.generate_minefield()

    @property
    def flags(self):
        return self._flags

    @flags.setter
    def flags(self, value):
        self._flags = value
        self.flags_changed_event.notify()

    def generate_minefield(self):
        self._mines = [[0 for ci in range(self.cols)] for ri in range(self.rows)]
        self.minefield = [[Content.Unknown for ci in range(self.cols)] for ri in range(self.rows)]
        self.flags = 0
        self.result = Result.OK

        mi = self.mine_count
        while mi:
            ri = randrange(self.rows)
            ci = randrange(self.cols)
            if self._mines[ri][ci] >= 0:
                self._mines[ri][ci] = -10
                for rj, cj in self.cells_surrounding(ri, ci):
                    self._mines[rj][cj] += 1
                mi -= 1  # decrement only when a mine is placed

    def dig(self, r, c):
        if not self.is_unknown(r, c):
            return Result.OK
        if self._mines[r][c] < 0:
            self.minefield[r][c] = Content.BlownMine
            self.update_event.notify(r, c)
            for ri, ci in self.all_indices():
                if (ri != r or ci != c) and self._mines[ri][ci] < 0 and self.minefield[ri][ci] != Content.Flag:
                    self.minefield[ri][ci] = Content.Mine
                    self.update_event.notify(ri, ci)
            self.result = Result.Loss
            self.game_over_event.notify(Result.Loss)
            return Result.Loss

        explore_stack = [(r, c)]
        while explore_stack:
            r, c = explore_stack.pop()
            if not self.is_unknown(r, c):
                continue
            if self._mines[r][c] == 0:
                explore_stack.extend(self.cells_surrounding(r, c))
            self.minefield[r][c] = self._mines[r][c]
            self.update_event.notify(r, c)

        self.result = Result.Win if self._is_win() else Result.OK
        if self.result != Result.OK:
            self.game_over_event.notify(self.result)
        return self.result

    def _is_win(self):
        for ri, ci in self.all_indices():
            if 0 <= self._mines[ri][ci] != self.minefield[ri][ci]:
                return False
        return True

    def toggle_flag(self, r, c):
        if self.minefield[r][c] == Content.Unknown:
            self.minefield[r][c] = Content.Flag
            self.flags += 1
        elif self.minefield[r][c] == Content.Flag:
            self.minefield[r][c] = Content.QuestionMark
            self.flags -= 1
        elif self.minefield[r][c] == Content.QuestionMark:
            self.minefield[r][c] = Content.Unknown
        self.update_event.notify(r, c)

    def set_flag(self, r, c, content):
        if (self.minefield[r][c] != content and
                (self.minefield[r][c] == Content.Flag or self.is_unknown(r, c)) and
                (content == Content.Unknown or content == Content.QuestionMark or content == Content.Flag)):
            self.minefield[r][c] = content
            if content == Content.Flag:
                self.flags += 1
            elif self.minefield[r][c] == Content.Flag:
                self.flags -= 1
            self.update_event.notify(r, c)

    def all_indices(self):
        for r, c in ((r, c) for r in range(self.rows) for c in range(self.cols)):
            yield r, c

    def cells_surrounding(self, r, c):
        for ri, ci in ((ri, ci)
                       for ri in range(r - 1, r + 2) if 0 <= ri < self.rows
                       for ci in range(c - 1, c + 2) if 0 <= ci < self.cols and (ri != r or ci != c)):
            yield ri, ci

    def is_unknown(self, r, c):
        return Content.Unknown == self.minefield[r][c] or self.minefield[r][c] == Content.QuestionMark
