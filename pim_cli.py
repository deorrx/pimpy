#!/usr/bin/env python3

from os import listdir
from os.path import isfile, join

import readline
import subprocess

EDITOR = 'vipe'


def get_editor_input(greeting=None, initial_text=None):
    """:type text: str|None"""
    # TODO use greeting parameter and set default value
    with subprocess.Popen([EDITOR], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE) as process:
        return process.stdout.read()


def get_line_input(greeting=None, initial_text=None):
    """:type text: str|None"""
    if initial_text is not None:
        readline.set_startup_hook(lambda: readline.insert_text(initial_text))
        try:
            if greeting is None:
                return input()
            else:
                return input(greeting)
        finally:
            readline.set_startup_hook()
    else:
        if greeting is None:
            return input()
        else:
            return input(greeting)


class Cmd(object):
    def __init__(self, line):
        self.line = line
        self.terms = line.strip().split()

    def term(self, i):
        return self.terms[i]

    def tail(self, n):
        return ' '.join(self.line.lstrip().split()[n])

    def n_terms(self):
        return len(self.terms)


class Form(object):
    def __init__(self, fields):
        self.fields = fields

    def run(self):
        # TODO implement it more clean
        r = {}
        for field in self.fields:
            if field[1] == int:
                print(field[0], ":")
                r[field[0]] = int(get_line_input())
                continue
            if field[1] == str:
                print(field[0], ":")
                if len(field) > 2 and field[2] == 'text':
                    r[field[0]] = get_editor_input()
                    continue
                else:
                    r[field[0]] = get_line_input()
                    continue
            if field[1] == 'choice':
                r[field[0]] = get_line_input(field[0])
                continue
            raise TypeError("unknown type in form")

        return r


class Notes(object):
    def __init__(self, db):
        self.db = db

    def __call__(self, cmd):
        """:type cmd: Cmd"""
        if cmd.n_terms() < 2:
            print("Not enough arguments")
        cc = cmd.term(1)
        if cc in ['+', 'a', 'add']:
            self.add(cmd)
        elif cc in ['-', 'r', 'rm']:
            self.rm(cmd)
        elif cc in ['e', 'ed', 'edit']:
            self.ed(cmd)
        elif cc in ['l', 'ls', 'list']:
            self.ls(cmd)
        elif cc in ['f', 'filter']:
            self.filter(cmd)
        else:
            print('unknown command', cc)

    def add(self, cmd):
        """:type cmd: Cmd"""
        print('add')
        s = get_editor_input()
        self.db.append(('Note', s))
        print('new note\n%s\n-----' % s)

    def rm(self, cmd):
        """:type cmd: Cmd"""
        n = int(cmd.tail(2))
        self.db.delete(n)
        print('rm', n)

    def ed(self, cmd):
        """:type cmd: Cmd"""
        n = int(cmd.tail(2))
        # TODO implement
        print('ed', n)

    def ls(self, cmd):
        """:type cmd: Cmd"""
        # TODO implement
        print('ls')

    def filter(self, cmd):
        """:type cmd: Cmd"""
        # TODO implement
        print('filter')


class Tasks(object):
    def __init__(self, db):
        self.db = db

    def __call__(self, cmd):
        """:type cmd: Cmd"""
        if cmd.n_terms() < 2:
            print("Not enough arguments")
        cc = cmd.term(1)
        if cc in ['+', 'a', 'add']:
            self.add(cmd)
        elif cc in ['-', 'r', 'rm']:
            self.rm(cmd)
        elif cc in ['e', 'ed', 'edit']:
            self.ed(cmd)
        elif cc in ['d', 'done']:
            self.ed(cmd)
        elif cc in ['l', 'ls', 'list']:
            self.ls(cmd)
        elif cc in ['f', 'filter']:
            self.filter(cmd)
        else:
            print('unknown command', cc)

    def add(self, cmd):
        """:type cmd: Cmd"""
        # TODO implement
        print('add')

    def rm(self, cmd):
        """:type cmd: Cmd"""
        # TODO implement
        print('rm')

    def ed(self, cmd):
        """:type cmd: Cmd"""
        # TODO implement
        print('ed')

    def done(self, cmd):
        """:type cmd: Cmd"""
        # TODO implement
        print('done')

    def ls(self, cmd):
        """:type cmd: Cmd"""
        # TODO implement
        print('ls')

    def filter(self, cmd):
        """:type cmd: Cmd"""
        # TODO implement
        print('filter')


class App(object):
    def __init__(self, db, **kwargs):
        """:type db: DB"""
        self.db = db
        self.classes = kwargs

    def run(self, quit_cmd):
        """:type quit_cmd: str|list(str)"""
        while True:
            try:
                line = input("> ")
            except EOFError:
                print()
                break
            if line.strip() == "":
                continue
            elif isinstance(quit_cmd, str) and line.strip() == quit_cmd:
                break
            elif isinstance(quit_cmd, list) and line.strip() in quit_cmd:
                break
            else:
                cmd = Cmd(line)
                c = cmd.term(0)
                if c in self.classes:
                    self.classes[c](self.db)(cmd)
                else:
                    continue


def main():
    db = DB('data')
    # for t in DBIterator(db, odd=True):
    #     print(t)

    s = get_line_input("a>")
    print("a=", s)
    s = get_line_input("b>", s)
    print("b=", s)
    s = get_line_input("c>")
    print("c=", s)

    # form = Form([('s', str), ('t', str, 'text'), ('n', int)])
    # print(form.run())

    app = App(db, t=Tasks, n=Notes)
    return app.run(['q', 'x', 'quit', 'exit'])


if __name__ == '__main__':
    main()
