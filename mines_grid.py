from itertools import chain

import gi

from ai.minesweeper.common import Content
from ai.minesweeper.game_engine import GameEngine
from ai.minesweeper.solver import MinesweeperSolver

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk


class MinesGrid(Gtk.Grid):
    def __init__(self, game=None, **properties):
        Gtk.Grid.__init__(self, **properties)
        self.engine = GameEngine(game)
        self.engine.update_event.add(self.on_cell_update)
        self.engine.game_over_event.add(self.on_game_over)
        self.game_in_progress = True
        self.solver = MinesweeperSolver(self.engine)

        self.buttons = []
        for ri in range(self.engine.rows):
            row = []
            self.buttons.append(row)
            for ci in range(self.engine.cols):
                button = Gtk.ToggleButton()
                row.append(button)
                button.connect('button-release-event', self.on_button_release_event, (ri, ci))
                button.connect('button-press-event', self.on_button_press_event, (ri, ci))
                button.connect('toggled', self.on_button_toggled, (ri, ci))
                button.set_size_request(35, 35)
                self.attach(button, ci, ri, 1, 1)

    def new_game(self):
        self.game_in_progress = True
        self.engine.generate_minefield()
        for grid_button in chain(*self.buttons):
            grid_button.set_sensitive(True)
            grid_button.set_label('')
            grid_button.set_active(False)

    def end_game(self):
        if self.game_in_progress:
            self.game_in_progress = False
            for grid_button in chain(*self.buttons):
                grid_button.set_sensitive(False)

    def on_cell_update(self, r, c):
        value = self.engine.minefield[r][c]
        button = self.buttons[r][c]
        button.set_active(not self.engine.is_unknown(r, c) and value != Content.Flag)
        if value == Content.Mine:
            button.set_label('*')
        elif value == Content.BlownMine:
            button.set_label('*')
            self.end_game()
        elif value > Content.NoMine:
            button.set_label(str(int(value)))
        elif value == Content.Flag:
            button.set_label('F')
        elif value == Content.QuestionMark:
            button.set_label('?')
        elif value == Content.Unknown:
            button.set_label('')

    def on_button_toggled(self, button, position):
        button.set_active(Content.Unknown != self.engine.minefield[position[0]][position[1]] != Content.Flag)

    def on_button_release_event(self, button, event_button, position):
        if event_button.button == 1:
            self.engine.dig(*position)
        elif event_button.button == 3:
            self.engine.toggle_flag(*position)

    def on_button_press_event(self, button, event_button: Gdk.EventButton, position):
        r, c = position
        if (event_button.button == 1 and event_button.type == Gdk.EventType._2BUTTON_PRESS and
                    self.engine.minefield[r][c] == sum((self.engine.minefield[ri][ci] == Content.Flag)
                                                       for ri, ci in self.engine.cells_surrounding(r, c))):
            for ri, ci in self.engine.cells_surrounding(r, c):
                self.engine.dig(ri, ci)

    def on_game_over(self, result):
        self.end_game()
