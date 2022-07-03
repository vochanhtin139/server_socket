from tkinter.ttk import *
from tkinter import *
from socket import *
import threading

# *********************************** 
# *         Initialize SOCKET       *
# ***********************************

sck = socket(AF_INET, SOCK_STREAM)
sck.bind(("127.0.0.1", 9000))
sck.listen(5)

# Handling client in the background
def handle_client(client, clientInfo, new_win_text):
    print("Received connection from ", clientInfo)
    message = "Hello client";
    client.send(message.encode())
    new_win_text.config(text=clientInfo)
    client.close()

    return

# Handling listening socket in the background
def handle_socket_listening(sck, new_win_text):
    while True:
        client, clientInfo = sck.accept()
        t = threading.Thread(target=handle_client, args=(client, clientInfo, new_win_text))
        t.start()
    
    return


# *********************************** 
# *          Initialize GUI         *
# ***********************************
w = Tk()

w.title("")

width_of_window = 854
height_of_window = 500
screen_width = w.winfo_screenwidth()
screen_height = w.winfo_screenheight()
x_coordinate = (screen_width / 2) - (width_of_window / 2)
y_coordinate = (screen_height / 2) - (height_of_window / 2)
w.geometry("%dx%d+%d+%d" % (width_of_window, height_of_window, x_coordinate, y_coordinate))

# w.overrideredirect(1)

s = Style()
s.theme_use('clam')
s.configure("red.Horizontal.TProgressbar", foreground='red', background="#4f4f4f")
progress = Progressbar(w, style="red.Horizontal.TProgressbar", orient=HORIZONTAL, length=1000, mode='determinate')

# New window after splash screen
def new_win():
    q = Tk()
    q.title("")
    q.geometry("854x500")
    l1 = Label(q, text='ADD TEXT HERE ', fg='grey', bg=None)
    l = ('Calibri (Body)', 24, 'bold')
    l1.config(font=l)
    l1.pack(expand=TRUE)

    socket_threaded = threading.Thread(target=handle_socket_listening, args=(sck, l1))
    socket_threaded.start()

    q.mainloop()    

# Config the bar at splash screen
def bar():
    l4 = Label(w, text='Loading...', fg="white", bg=a, anchor=S)
    lst4 = ('Calibri (Body)', 10)
    l4.config(font=lst4)
    # l4.place(x=18, y=210)
    l4.pack(side=LEFT, pady=(50, 0))

    import time
    r = 0
    for i in range(100):
        progress['value'] = r
        w.update_idletasks()
        time.sleep(0.02)
        r = r + 1

    w.destroy()
    new_win()

progress.pack(side=BOTTOM)

# Adding widget at splash screen
a = '#249794'
Frame(w, width=857, height=482, bg = a).place(x=0, y=0)

l1 = Label(w, text='SERVER MENU', fg = 'white', bg=a, anchor=W)
lst1 = ('Courier New', 50, 'bold italic')
l1.config(font=lst1)
# l1.place(x=90, y=50)
l1.pack(fill=BOTH, padx=100, pady=(50, 0))

l2 = Label(w, text="Group 08", fg="white", bg=a, anchor=W)
lst2 = ('Tahoma', 28)
l2.config(font=lst2)
# l2.place(x=90, y=110)
l2.pack(fill=BOTH, padx=100)

l3 = Label(w, text="Vo Chanh Tin\nPhan Nhu Quynh\nNguyen Van Dang Huynh", foreground="white", background=a, justify=LEFT, anchor=W)
lst3 = ('Tahoma', 14)
l3.config(font=lst3)
l3.pack(fill=BOTH, padx=100, pady=10)

b1 = Button(w, width=20, height=2, text="Get started", command=bar, border=1, fg=a, bg="white", anchor=CENTER)
# b1.place(x=200, y=300)
b1.pack(pady=50)

w.mainloop()