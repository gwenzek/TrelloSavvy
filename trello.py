from lib.trollop import TrelloConnection

# import show_board as ui
import inline_trello as ui


class Trello():

    def __init__(self):
        with open('trello_token.txt') as tok_file:
            self.token = tok_file.readline().split()[-1].strip()
            self.key = tok_file.readline().split()[-1].strip()
            self.secret = tok_file.readline().split()[-1].strip()

        self.api = TrelloConnection(self.key, self.token)


def main():
    t = Trello()
    board = t.api.get_board('YUYQoxaW')

    # notifications = t.api.me.notifications
    # print(notifications)
    # for n in notifications:
    #     print(n.type)
    #     print(n.date)
    # return

    print(board)
    print('lists:')
    print(board.lists)

    a_lire = board.lists[0]
    print(a_lire)
    print(a_lire.cards)


    ui.load_cache()
    ui.render_board(board, 'board.txt')

# print('opening file')
# with open('board.txt', 'w') as o:
#     for line in lines:
#         o.write(line)
#         o.write('\n')

# ui.save_cache()

# card = ui.select_card(board, 13, 0)
# print(card.name)
# ui.insert_card(board, card, 8, 51)

# ui.render_board(board, 'board.txt')

if __name__ == '__main__':
    main()
