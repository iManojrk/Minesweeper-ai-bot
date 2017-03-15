import gi

from mines_grid import MinesGrid

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


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
        self.solve_button = builder.get_object('solve_button')

        self.mines_grid = MinesGrid(1)
        self.content_box.pack_end(self.mines_grid, expand=True, fill=True, padding=0)
        self.mines_grid.engine.flags_changed_event.add(self.on_flags_changed)
        self.on_flags_changed()
        self.mines_grid.engine.game_over_event.add(self.on_game_over)

    # Event Handlers
    def on_flags_changed(self):
        self.flags_count_label.set_label("{}/{}".format(self.mines_grid.engine.flags,
                                                        self.mines_grid.engine.mine_count))

    def on_new_game_menuitem_activate(self, *args):
        self.mines_grid.new_game()
        self.solve_button.set_sensitive(True)

    def on_solve_button_clicked(self, *args):
        self.mines_grid.solver.solve()

    def on_game_over(self, result):
        self.solve_button.set_sensitive(False)


ui = MinesweeperUI()
ui.window.connect('delete-event', Gtk.main_quit)
ui.window.show_all()
Gtk.main()
