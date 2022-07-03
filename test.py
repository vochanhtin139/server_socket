from tkinter import *

root = Tk()

def getText(entry):
    print(entry.get())

entry = Entry(root)
entry.pack()

print(entry.get())

# btn = Button(root, text="enter", command=lambda:getText(entry))
# btn.pack()

root.mainloop()