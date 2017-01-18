#!/usr/bin/env python3

from tkinter import *

from json import dumps as json_dumps, loads as json_loads
from enum import Enum


class Interface(object):
    def __init__(self):
        self.taglist_windows = Tk()

        self.listbox = Listbox(self.taglist_windows)
        self.listbox.pack()

        self.listbox.insert(END, "a list entry")

        for item in ["one", "two", "three", "four"]:
            self.listbox.insert(END, item)

        self.root2 = Tk()

        self.listbox2 = Listbox(self.root2)
        self.listbox2.pack()

    def run(self):
        self.taglist_windows.mainloop()


def main():
    ifc = Interface()
    ifc.run()


if __name__ == '__main__':
    main()
