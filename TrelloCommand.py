import sublime
import sublime_plugin

from .lib.trollolop import TrelloConnection


class TsavvyOpenBoardCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.setup_data_from_settings()

        if not self.token:
            self.help_text()
            return

        self.api = TrelloConnection(self.key, self.token)
        print(self.api.get_member("me").boards)

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
