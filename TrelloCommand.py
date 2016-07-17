import sublime
import sublime_plugin

from .lib.trollolop import TrelloConnection
from .src import inline_ui as ui
from os import path
from codecs import open


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
        self.indent = user_settings.get("indent", 2)
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

        view = self.window.open_file(board_path)
        view.set_syntax_file('Packages/TrelloSavvy/trello.sublime-syntax')

        sublime.set_timeout_async(lambda: self.edit_board_file(view, b), 0)

    def edit_board_file(self, view, board):

        file = view.file_name()
        cards = {}
        with open(file, 'w', 'utf-8') as o:

            level = 0
            indent = self.indent
            def print_lines(x):
                for line in x:
                    if line == '':
                        o.write('\n')
                    else:
                        o.write(' ' * (level * indent))
                        o.write(line)
                        o.write('\n')

            for l in board.lists:
                level = 0
                print_lines(ui.render_list_title(l))

                if len(l.cards) == 0:
                    print_lines([''])

                for card in l.cards:
                    level = 1
                    print_lines(ui.render_card_title(card))
                    level = 2
                    # print_lines(ui.render_card_details(card))
                    cards[card._id] = card
                    print_lines(['refreshing ' + card._id])
                    print_lines([''])

        view = self.window.open_file(file)
        details_indent = ' ' * (self.indent * 2)
        i = 0
        refreshing_regex = r'^%srefreshing [a-z0-9]+$' % details_indent
        region = view.find(refreshing_regex, 0)
        while region is not None and region.a > -1:
            id = view.substr(region).split()[-1]
            details = list(ui.render_card_details(cards[id]))
            if len(details) > 0:
                details = '\n'.join(map(lambda d: details_indent + d, details))
                print('calling ts_replace_region')
                view.run_command('ts_replace_region', args=dict(text=details, begin=region.begin(), end=region.end()))

            region = view.find(refreshing_regex, region.end())

        sublime.set_timeout_async(lambda: view.run_command('save'), 1000)


def extract_id(view, region):
    row, col = view.rowcol(region.begin())
    return view.substr(view.line(view.text_point(row - 1, col))).strip()[1:-1]


class TsReplaceRegionCommand(sublime_plugin.TextCommand):

    """
    Replace the contents of a region within the view with the provided text.
    """

    def run(self, edit, text, begin, end):
        is_read_only = self.view.is_read_only()
        self.view.set_read_only(False)
        self.view.replace(edit, sublime.Region(begin, end), text)
        self.view.set_read_only(is_read_only)
