#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
from os import path, mkdir

LIST_SEP = '----------------'
INDENT = 2

def write_board_file(board, file, render_cards=False):
    print('printing at', file)
    card_path = path.join(path.dirname(file), 'cards')
    if not path.exists(card_path):
        mkdir(card_path)

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
                if render_cards:
                    write_card_file(path.join(card_path, '%s.txt' % card._id))

                level = 1
                print_lines(render_card_title(card))
                level = 2
                print_lines(render_card_details(card))
                print_lines([''])

def write_card_file(card, file):
    with open(file, 'w') as c:
        for line in render_full_card_details(card):
            c.write(line)
            c.write('\n')

def render_card_title(card):
    print('rendering', card)
    yield '<%s>' % card._id
    name = card.name.replace('\n', ' ')
    yield name


def render_card_details(card, condensed=False):

    members = map(lambda m: '@' + get_initials(m.fullname), card.members)
    labels = map(lambda label: render_label(label, short=condensed), card.labels)

    details = []
    if card.desc is not None:
        details.append('≡')

    n_comments = len(card.comments())
    if n_comments > 0:
        details.append('%d 💬' % n_comments)

    n_attachments = len(card.attachments())
    if n_attachments > 0:
        details.append('%d 📎' % n_attachments)

    for checklist in card.checklists:
        done = 0
        total = 0
        for item in checklist.checkItems:
            done += item.checked
            total += 1

        details.append('[%s] %d/%d' % ('✔' if done == total else '✓', done, total))

    if condensed:
        yield ', '.join(details + members + labels)
    else:
        if len(card.labels) > 0:
            yield ', '.join(labels)
        if len(card.members) > 0:
            yield ', '.join(members)
        yield ', '.join(details)


def render_full_card_details(card):

    yield from render_card_title(card)
    yield ''

    members = map(lambda m: m.fullname, card.members)
    yield '@ Members: ' + ', '.join(members)

    labels = map(lambda label: render_label(label, short=False), card.labels)
    yield 'Labels: ' + ', '.join(labels)

    if card.desc is not None:
        yield ''
        yield '≡ Description:'
        yield from card.desc.split('\n')

    for checklist in card.checklists:
        yield ''
        yield 'Checklist:'
        for item in checklist.checkItems:
            yield '[%s] %s' % ('✓' if item.checked else ' ', item.name)

    attachments = card.attachments()
    if len(attachments) > 0:
        yield ''
        yield 'Attachments:'
        for attachment in attachments:
            yield '📎: %s' % attachment['url']

    comments = card.comments()
    if len(comments) > 0:
        yield ''
        yield 'Comments'
        for comment in comments:
            yield('💬 %s: % s' % (comment['username'], comment['text']))


def render_list_title(l):
    yield LIST_SEP
    yield '<%s>' % l._id
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
CACHE_SHORT_LABELS = {}
SYMBOLS = {
    'pink': '%', 'red': '!', 'green': '*', 'blue': '?', 'black': '#',
    'yellow': '~', 'sky': '&', 'purple': '$', 'orange': '§'
}

def render_label(label, short=False):
    name = label['name']
    color = label['color']

    if short and name in CACHE_SHORT_LABELS:
        return CACHE_SHORT_LABELS[name]
    if not short and name in CACHE_LABELS:
        return CACHE_LABELS[name]

    if short:
        res = SYMBOLS[color] * 4
        CACHE_SHORT_LABELS[name] = res
    else:
        res = '<{s} {name} {s}>'.format(name = name, s=SYMBOLS[color])
        CACHE_LABELS[name] = res

    return res


def load_cache():
    pass
