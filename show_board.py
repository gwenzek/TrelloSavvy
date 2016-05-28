import json
import os

COLUMN_SIZE = 20
COLUMN_SEP = ' | '
WHITE_COLUMN = ' ' * COLUMN_SIZE
CARD_CACHE = {}
CARD_CACHE_FILE = 'card_cache.json'
LIST_CACHE = {}
LIST_CACHE_FILE = 'list_cache.json'
CARDS_LENGTH = {}


def get_list(l):
    if l._id not in LIST_CACHE:
        LIST_CACHE[l._id] = list(render_list(l))
    return LIST_CACHE[l._id]


def set_list(l, lines):
    LIST_CACHE[l._id] = lines


def render_list(l, column_size=COLUMN_SIZE):
    res = list(render_list_title(l, column_size))

    for card in l.cards:
        res += get_card(card)

    res.append(' ' * column_size)
    return res


def render_list_title(l, column_size=COLUMN_SIZE):
    yield "#" * column_size
    title = l.name.replace('\n', ' ')
    print('rendering', title)
    title_col = column_size - 4
    while len(title) > title_col:
        t, title = smart_split(title, title_col)
        yield '# ' + center(t, title_col) + ' #'

    yield '# ' + center(title, title_col) + ' #'
    yield "#" * column_size


def center(text, column_size):
    delta = int((column_size - len(text)) / 2)
    return (' ' * delta) + text + (' ' * (column_size - delta - len(text)))


def get_card(card):
    if card.url not in CARD_CACHE:
        CARD_CACHE[card.url] = list(render_card(card, COLUMN_SIZE))
    return CARD_CACHE[card.url]


def render_card(cards, column_size):
    name = cards.name.replace('\n', ' ')
    print('rendering', name)

    for line in render_long_str(name, column_size):
        yield line

    yield " " * column_size
    yield '%d comments' % len(cards.comments())
    if len(cards.members) > 0:
        members = ", ".join(map(lambda m: get_initials(m.fullname), cards.members))
        for line in render_long_str(members, column_size):
            yield line

    yield "-" * column_size


def get_initials(fullname):

    if len(fullname) <= 3:
        res = fullname
    else:
        parts = fullname.split()
        if len(parts) > 1:
            res = '.'.join(map(lambda p: p[0], parts))
        else:
            res = fullname[:3]

    print('renamed %s to %s' % (fullname, res))
    return res


def save_cache():
    with open(CARD_CACHE_FILE, 'w') as o:
        json.dump(CARD_CACHE, o)


def load_cache():
    if os.path.exists(CARD_CACHE_FILE):
        global CARD_CACHE
        with open(CARD_CACHE_FILE, 'r') as o:
            CARD_CACHE = json.load(o)


def render_long_str(long_str, column_size):
    while len(long_str) > column_size:
        t, long_str = smart_split(long_str, column_size)
        yield t
    yield long_str


def smart_split(s, column_size):
    i = s[:column_size].find('\n')
    if 0 <= i < column_size:
        return s[:i], s[i:]

    return s[:column_size], s[column_size:]


def print_list(l):
    lines = [20 * '#', '# ' + l['name'] + ' #', 20 * '#', '']

    for card in l['cards']:
        lines += print_card(card)
        lines.append('')

    return lines


def print_card(card):
    return [card['description'], 'by %s | %d comments' % (card['author'], len(card['comments']))]


def render_board(board, file):
    lists = [get_list(l) for l in board.lists]
    offsets = [0 for _ in lists]

    with open(file, 'w') as o:
        while not all([offsets[i] == len(lists[i]) for i in range(len(lists))]):
            n = len(lists)
            for i in range(n):
                if offsets[i] < len(lists[i]):
                    cell = lists[i][offsets[i]]
                    o.write(cell[:COLUMN_SIZE])
                    if len(cell) < COLUMN_SIZE:
                        o.write(' ' * (COLUMN_SIZE - len(cell)))
                    offsets[i] += 1
                else:
                    o.write(WHITE_COLUMN)
                o.write(COLUMN_SEP)
            o.write('\n')


def select_card(board, line, column):
    l = board.lists[int(column / COLUMN_SIZE)]

    off = 3
    card_off = -1
    card = None

    while off < line:
        card_off += 1
        card = l.cards[card_off]
        off += len(CARD_CACHE[card.url])

    return card


def insert_card(board, card, line, column):
    l = board.lists[int(column / COLUMN_SIZE)]
    card_to_insert = card

    off = 3
    card_off = -1
    card = None

    while off < line:
        card_off += 1
        card = l.cards[card_off]
        off += len(CARD_CACHE[card.url])

    lines = get_list(l)
    lines = lines[:off] + get_card(card_to_insert) + lines[off:]
    set_list(l, lines)


# if __name__ == '__main__':
#     lists = load("board.json")
#     printed = [list(l.render(COLUMN_SIZE)) for l in lists]
#     print(printed[0][1])

#     lines = render_lists(printed)

#     with open('board.txt', 'w') as o:
#         for line in lines:
#             o.write(line)
#             o.write('\n')
