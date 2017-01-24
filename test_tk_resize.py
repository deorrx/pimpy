import tkinter as tk

root = tk.Tk()
scrollbar = tk.Scrollbar(root, orient="vertical")
scrollbar2 = tk.Scrollbar(root, orient="vertical")

scrollbar.grid(row=0, column=1, sticky="ns")
scrollbar2.grid(row=1, column=1, sticky="ns")

lb = tk.Listbox(root, width=50, height=20,
                yscrollcommand=scrollbar.set)
lb.grid(row=0, column=0, sticky="nswe")

lb2 = tk.Listbox(root, width=50, height=20,
                 yscrollcommand=scrollbar2.set)
lb2.grid(row=1, column=0, sticky="nswe")

scrollbar.config(command=lb.yview)
scrollbar2.config(command=lb2.yview)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

#scrollbar.pack(side="right", fill="y")
#lb.pack(side="left",fill="both", expand=True)
#lb2.pack(side="left",fill="both", expand=True)
for i in range(0,100):
    lb.insert("end", "item #%s" % i)
for i in range(0,100):
    lb2.insert("end", "item #%s" % i)

def on_resize(event):
    if event.widget.__class__ == tk.Tk:
        print('resize', event.widget.__class__, event.width, event.height)

root.bind("<Configure>", on_resize)



root.mainloop()
