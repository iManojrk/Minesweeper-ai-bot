import gi

from common import Result
from mines_grid import MinesGrid

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib


class MinesweeperUI:
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file('Glade/Minesweeper-main-window.glade')

        self.on_window_delete_event = Gtk.main_quit
        self.on_quit_menuitem_activate = Gtk.main_quit
        builder.connect_signals(self)

        self.window = builder.get_object('MinesweeperMain')
        self.content_box = builder.get_object('content_box')
        self.flags_count_label = builder.get_object('flags_count_label')
        self.solve_button = builder.get_object('solve_toggle_button')
        self.step_button = builder.get_object('step_button')

        self.mines_grid = MinesGrid(2)
        self.content_box.pack_end(self.mines_grid, expand=True, fill=True,
                                  padding=0)
        self.mines_grid.engine.flags_changed_event.add(self._on_flags_changed)
        self._on_flags_changed()
        self.mines_grid.engine.game_over_event.add(self._on_game_over)
        self.solver_active = False

    # Event Handlers
    def _on_flags_changed(self):
        self.flags_count_label \
            .set_label("{}/{}".format(self.mines_grid.engine.flags,
                                      self.mines_grid.engine.mine_count))

    def on_new_game_menuitem_activate(self, *args):
        self.mines_grid.new_game()
        self.solve_button.set_sensitive(True)
        self.step_button.set_sensitive(True)

    def on_step_button_clicked(self, *args):
        self.solver_active = False
        self.solve_button.set_active(False)
        self.mines_grid.solver.solve()

    def on_solve_toggle_button_toggled(self, button):
        self.solver_active = self.solve_button.get_active()
        if self.solve_button.get_active():
            self.mines_grid.solver.solve()
            GLib.timeout_add(400, self.solve_timeout)

    def solve_timeout(self):
        if (not self.solver_active
                or self.mines_grid.engine.result != Result.OK):
            return False
        self.mines_grid.solver.solve()
        return True

    def _on_game_over(self, result):
        self.solve_button.set_sensitive(False)
        self.solve_button.set_active(False)
        self.step_button.set_sensitive(False)


ui = MinesweeperUI()
ui.window.show_all()
Gtk.main()
