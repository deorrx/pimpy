#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import Treeview

# from typing import Iterable
from db import PIMDB, Note, Task, Category


def get_test_password():
    return 'kLF9AW8IA0H5WiLcoByZF9H3Yl7FXtBU'


class Interface(object):
    def __init__(self, db: PIMDB):
        self.db = db

        w,h, x, y = 200, 700, 0, 0
        self.taglist_windows = Tk()
        self.taglist_windows.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.listbox = Treeview(self.taglist_windows, )
        self.listbox.pack()

        tree = self.listbox
        tree["columns"] = ("one", "two")
        tree.column("one", width=100)
        tree.column("two", width=100)
        tree.heading("one", text="coulmn A")
        tree.heading("two", text="column B")

        tree.insert("", 0, text="Line 1", values=("1A", "1b"))

        id2 = tree.insert("", 1, "dir2", text="Dir 2")
        tree.insert(id2, "end", "dir 2", text="sub dir 2", values=("2A", "2B"))

        ##alternatively:
        tree.insert("", 3, "dir3", text="Dir 3")
        tree.insert("dir3", 3, text=" sub dir 3", values=("3A", " 3B"))

        self.root2 = Tk()

        self.listbox2 = Listbox(self.root2)
        self.listbox2.pack()

    def run(self):
        self.taglist_windows.mainloop()


def main():
    # FIXME ask password, create password getter
    db = PIMDB('test.data', get_test_password)
    ifc = Interface(db)
    ifc.run()


if __name__ == '__main__':
    main()
