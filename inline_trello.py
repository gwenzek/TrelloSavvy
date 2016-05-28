from codecs import open

LIST_SEP = '################'
CARD_SEP = '----------------'
INDENT = 2

def render_board(board, file):
    with open(file, 'w', 'utf-8') as o:

        level = 0
        def print_lines(x):
            for line in x:
                if line == '':
                    o.write('\n')
                else:
                    o.write(' ' * (level * INDENT))
                    o.write(line)
                    o.write('\n')

        for l in board.lists:
            level = 0
            print_lines(render_list_title(l))

            if len(l.cards) == 0:
                print_lines([''])

            for card in l.cards:
                level = 1
                print_lines(render_card_title(card))
                level = 2
                print_lines(render_card_details(card))
                print_lines([''])


def render_card_title(card):
    print('rendering', card)
    yield '<%s>' % card._id
    name = card.name.replace('\n', ' ')
    yield name

def render_card_details(card):
    details = []

    if card.desc is not None:
        details.append('≡')

    n_comments = len(card.comments())
    if n_comments > 0:
        details.append('%d 💬' % n_comments)

    n_attachments = len(card.attachments())
    if n_attachments > 0:
        details.append('%d 📎' % n_attachments)

    for m in card.members:
        details.append('@' + get_initials(m.fullname))

    for label in card.labels:
        print(label['name'])
        details.append(render_label(label))

    yield ", ".join(details)

def render_list_title(l):
    yield LIST_SEP
    title = l.name.replace('\n', ' ')
    yield title
    yield '%d cards' % len(l.cards)
    yield LIST_SEP
    yield ''

CACHE_INITIALS = {}
def get_initials(fullname):

    if fullname in CACHE_INITIALS:
        return CACHE_INITIALS[fullname]

    if len(fullname) <= 3:
        res = fullname
    else:
        parts = fullname.split()
        if len(parts) > 1:
            res = '.'.join(map(lambda p: p[0], parts))
        else:
            res = fullname[:3]

    print('renamed %s to %s' % (fullname, res))
    CACHE_INITIALS[fullname] = res
    return res


CACHE_LABELS = {}
def render_label(label):
    name = label['name']
    color = label['color']

    if name in CACHE_LABELS:
        return CACHE_LABELS[name]

    symbol = {'pink': '%', 'red': '!', 'green': '*', 'blue': '?', 'black': '#', 'yellow': '~', 'sky': '@', 'purple': '$', 'orange': '§'}

    res = '<{s} {name} {s}>'.format(name = name, s=symbol[color])
    CACHE_LABELS[name] = res

    return res


def load_cache():
    pass
