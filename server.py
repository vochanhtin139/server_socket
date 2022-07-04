from cProfile import label
from logging import root
from optparse import Option
from tkinter.ttk import *
from tkinter import *
from turtle import up
from PIL import Image, ImageTk
from socket import *
import threading
import sqlite3

# *********************************** 
# *        Initialize SQLite        *
# ***********************************

num_connection = [0]

sqliteConnection = sqlite3.connect("sqlite.db")
dbCursor = sqliteConnection.cursor()
dbCursor.close()

# *********************************** 
# *         Initialize SOCKET       *
# ***********************************

# Declare socket
sck = socket(AF_INET, SOCK_STREAM)
sck.bind(("127.0.0.1", 9000))
sck.listen(5)

# Handling client in the background
def handle_client(client, clientInfo, new_win_text, btn_client_connecting_str):
    print("Received connection from ", clientInfo)

    # num_connection + 1
    num_connection[0] += 1
    
    btn_client_connecting_str.set(str(num_connection[0] + 1) + " client(s) connected")

    message = "Hello client";
    client.send(message.encode())
    new_win_text.config(text=clientInfo)
    # client.close()
    data = client.recv(10000)
    print(data.decode()) 

    return

# Handling listening socket in the background
def handle_socket_listening(sck, new_win_text, btn_client_connecting_str):
    while True:
        client, clientInfo = sck.accept()
        t = threading.Thread(target=handle_client, args=(client, clientInfo, new_win_text, btn_client_connecting_str))
        t.start()
    
    return


# *********************************** 
# *          Initialize GUI         *
# ***********************************

# Add food pop up windows
def add_food_popup_windows(root):
    popup = Toplevel(root)
    popup.geometry("700x500+300+300")

    fleft = Frame(popup, width=100, height=50, relief=RAISED, background="#0ffc03")

    btnIMG_file = Image.open("icon\\fast_food.png")
    btnIMG_file.thumbnail((200, 200), Image.ANTIALIAS)
    btnIMG_object= ImageTk.PhotoImage(btnIMG_file)

    btnIMG = Button(fleft, height=200, width=200, image=btnIMG_object)
    btnIMG.pack(fill=BOTH, padx=40, pady=40)

    lbDir = Label(fleft, text="No file chosen")
    lbDir.pack()

    btnInsert = Button(fleft, height=2, width=10, text="INSERT")
    btnInsert.pack(side=LEFT, anchor=S, padx=(30, 0), pady=15)

    btnInsert = Button(fleft, height=2, width=10, text="CANCEL")
    btnInsert.pack(side=RIGHT, anchor=S, padx=(0, 30), pady=15)

    fleft.pack(fill=BOTH, side=LEFT)

    # fleft = Frame(popup, relief=RAISED, borderwidth=1)
    # fleft.pack(side=RIGHT)

    popup.mainloop()

# Initialize height and weight of windows
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

# Set up progress bar
s = Style()
s.theme_use('clam')
s.configure("red.Horizontal.TProgressbar", foreground='red', background="#4f4f4f")
progress = Progressbar(w, style="red.Horizontal.TProgressbar", orient=HORIZONTAL, length=1000, mode='determinate')

# New window after splash screen
def new_win():
    q = Tk()
    q.title("Server Menu")
    q.geometry("854x500")

    btn_setting_icon = Image.open("icon\\setting.png")
    btn_setting_icon.thumbnail((50, 50), Image.ANTIALIAS)
    btn_setting_img= ImageTk.PhotoImage(btn_setting_icon)
    btn_setting = Menubutton(q, text="Preferences", image=btn_setting_img)
    btn_setting.grid()
    btn_setting.menu = Menu(btn_setting, tearoff=0)
    btn_setting["menu"] = btn_setting.menu
    btn_setting.menu.add_command(label="Add food", command=lambda:add_food_popup_windows(q))
    btn_setting.menu.add_command(label="Settings")
    btn_setting.menu.add_command(label="About us")
    btn_setting.pack(side=RIGHT, anchor=N, padx=(0, 10), pady=(10, 0))

    btn_client_connecting_str = StringVar()
    btn_client_connecting_str.set(str(num_connection[0]) + " client(s) connected")
    btn_client_connecting = Button(q, textvariable=btn_client_connecting_str);
    btn_client_connecting.pack(side=RIGHT, anchor=N, padx=(0, 20), pady=(20, 0))

    lb1 = Label(q, text="Sever Menu", foreground='#249794')
    lb1.config(font=("Tahoma", 30, "italic"))
    lb1.pack(side=LEFT, anchor=N, padx=(20, 0), pady=(10, 0))

    l1 = Label(q, text='ADD TEXT HERE ', fg='grey', bg=None)
    l = ('Calibri (Body)', 24, 'bold')
    l1.config(font=l)
    l1.pack(expand=TRUE)

    socket_threaded = threading.Thread(target=handle_socket_listening, args=(sck, l1, btn_client_connecting_str))
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