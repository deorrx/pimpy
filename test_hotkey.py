import tkinter


def file_open(event):
    print('qwerty')


def close_window(event: tkinter.Event):
    assert isinstance(event.widget, tkinter.Tk)
    widget = event.widget
    assert isinstance(widget, tkinter.Tk)
    widget.destroy()


def make_menu(parent):
    top = tkinter.Menu(parent) 
    parent.config(menu=top)

    file = tkinter.Menu(top, tearoff=False)
    file.add_command(label='Open...', command=file_open, accelerator='ctrl+o')
    top.add_cascade(label='File', menu=file)


root = tkinter.Tk()


root.bind_all('<Control-Key-o>', file_open)
root.bind_all('<Control-Key-q>', close_window)

make_menu(root)

root.mainloop()
