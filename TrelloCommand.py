import sublime
import sublime_plugin

from .lib.trollolop import TrelloConnection
from .src import inline_ui as ui
from os import path


class TsavvyOpenBoardCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.setup_data_from_settings()

        if not self.token:
            self.help_text()
            return

        self.api = TrelloConnection(self.key, self.token)
        boards = self.api.get_member("me").boards
        print(boards)
        self.window.show_quick_panel(
            items = [board.name for board in boards],
            on_select = lambda i: self.select_entry(boards[i]),
            flags = sublime.KEEP_OPEN_ON_FOCUS_LOST
        )

    def setup_data_from_settings(self):
        user_settings = sublime.load_settings("TrelloSavvy.sublime-settings")

        self.key    = user_settings.get("key")
        self.secret = user_settings.get("secret")
        self.token  = user_settings.get("token")
        self.use_cache = user_settings.get("use_cache", True)
        self.renavigate = user_settings.get("keep_navigate_open_after_action", True)
        self.results_in_new_tab = user_settings.get("results_in_new_tab", True)
        self.card_delimiter = user_settings.get("card_delimiter", "<end>")
        self.syntax_file = user_settings.get("syntax_file")
        self.boards_directory = user_settings.get("boards_directory", "~/Desktop")

    def help_text(self):
        self.show_output_panel("No token found in the setting file.")

    def show_output_panel(self, text):
        self.output_view = self.window.get_output_panel("textarea")
        self.append_to_output_view(text)
        self.window.run_command("show_panel", { "panel": "output.textarea" })
        self.set_new_view_attributes(self.output_view)

    def append_to_output_view(self, text):
        self.output_view.set_read_only(False)
        self.output_view.run_command("append", { "characters": text })
        self.output_view.set_read_only(True)

    def set_new_view_attributes(self, view):
        # view.set_syntax_file(self.syntax_file)
        view.set_viewport_position((0, 0), True)

    def select_entry(self, board):
        print(board, board._id, board.name)
        b = self.api.get_board(board._id)
        board_path = path.join(self.boards_directory, b._id + '.trello')

        self.window.open_file(board_path)
        sublime.set_timeout_async(lambda: ui.write_board_file(b, board_path), 0)
