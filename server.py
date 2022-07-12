# from asyncio.windows_events import NULL
from cProfile import label
from ctypes import set_last_error
from email.mime import image
# from ctypes import WinDLL, sizeof
from email.utils import formataddr
from logging import root
from optparse import Option
from posixpath import split
from tkinter.ttk import *
from tkinter import *
from tokenize import String
from turtle import up, width
from PIL import Image, ImageTk
from socket import *
import threading
import sqlite3
import os
import tkinter.filedialog
from tkinter.filedialog import Open, askopenfilename
import json

# *********************************** 
# *        Initialize SQLite        *
# ***********************************

num_connection = [0]

sqliteConnection = sqlite3.connect("sqlite.db")
dbCursor = sqliteConnection.cursor()
# dbCursor.close()

dbCursor.execute("""CREATE TABLE IF NOT EXISTS "food_menu" (
	"id"	INTEGER NOT NULL UNIQUE,
	"food_name"	TEXT,
	"price"	INTEGER,
	"description"	TEXT,
	"image"	BLOB,
	PRIMARY KEY("id" AUTOINCREMENT)
);""")

# *********************************** 
# *         Initialize SOCKET       *
# ***********************************

# Declare socket
sck = socket(AF_INET, SOCK_STREAM)
sck.bind(("127.0.0.1", 9000))
sck.listen(5)

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

# Handling client in the background
def handle_client(client, clientInfo, new_win_text, btn_client_connecting_str):
    print("Received connection from ", clientInfo)

    # num_connection + 1
    num_connection[0] += 1
    
    btn_client_connecting_str.set(str(num_connection[0]) + " client đã kết nối")

    # message = "Hello client"
    # client.send(message.encode())
    # new_win_text.config(text=clientInfo)
    # client.close()

    sqliteConn = sqlite3.connect("sqlite.db")
    curs = sqliteConn.cursor()
    
    length = recvall(client, 64).decode('utf-8')
    tableId = recvall(client, int(length)).decode()

    tId = "table" + str(tableId)
    
    curs.execute("CREATE TABLE IF NOT EXISTS \"" + tId + """\" (
        \"id\"	INTEGER NOT NULL UNIQUE,
        \"food_order\"	TEXT,
        \"total\"	INTEGER,
        \"cash\"	INTEGER,
        \"card\"	TEXT,
        \"time_order\"	TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
    );""")
    
    curs.execute("SELECT * FROM food_menu ORDER BY id ASC")
    
    tmp = {
        "type": "food_menu"
    }
    jArr = []
    jArr.append(tmp)
    cnt = 1

    records = curs.fetchall()
    for item in records:
        tfood = "food" + str(cnt)
        js = {
            tfood: {
                "id": item[0],
                "food_name": item[1],
                "price": item[2],
                "description": item[3]
            }
        }
        cnt += 1
        jArr.append(js)
    client.sendall(str(len(json.dumps(jArr))).encode().ljust(64))
    client.sendall(json.dumps(jArr).encode())

    curs.execute("SELECT * FROM food_menu ORDER BY id ASC")
    for iPic in curs.fetchall():
        client.sendall(str(len(iPic[4])).encode().ljust(64))

        client.sendall(iPic[4])

    # sendStr = "Sent"
    # client.sendall(sendStr)
    
    
    while True: 
        order_length = recvall(client, 64).decode()
        order = recvall(client, int(order_length)).decode()
        
        if (order == "Order Food"):
            jData_length = recvall(client, 64).decode() 
            jData = recvall(client, int(jData_length)).decode()
            
            jRecv = json.loads(jData)
            
            time_orderAdd_length = recvall(client, 64).decode()
            time_orderAdd = recvall(client, int(time_orderAdd_length)).decode()
            
            sum = 0
            for i in range(len(jRecv) - 1):
                tfood = "food" + str(i + 1)
                sum = sum + int(jRecv[i+1][tfood]['num']) * int(jRecv[i+1][tfood]['price'])
                
            # Save to sqlite
            add_food_order_sql(str(jRecv), sum, time_orderAdd, tId)
            
            # Send total
            client.sendall(str(len(str(sum))).encode().ljust(64))
            client.sendall(str(sum).encode())
            
            while True:
                # Receive payment info
                cashAdd_length = recvall(client, 64).decode()
                cashAdd = recvall(client, int(cashAdd_length)).decode()
                
                cardAdd_length = recvall(client, 64).decode()
                cardAdd = recvall(client, int(cardAdd_length)).decode()
                
                # Pay by card
                if cardAdd != "":
                    flag = 1
                    if len(cardAdd) == 10:
                        for i in range(10):
                            if (cardAdd[i] >= '0') and (cardAdd[i] <= '9'):
                                continue
                            else:
                                flag = 0
                                cardAdd = ""
                                break 
                    else:
                        cardAdd = ""
                        flag = 0
                    
                    client.sendall(str(len(str(flag))).encode().ljust(64))
                    client.sendall(str(flag).encode())
                    
                    if flag == 1:
                        break
                else:
                    break
            # Add status payment
            add_status_payment_sql(int(sum), int(cashAdd), cardAdd, tId)
        else: 
            # Update food order
            updTime_length = recvall(client, 64).decode()
            updTime = recvall(client, int(updTime_length)).decode()
            
            if updTime == "false":
                sqliteDel = sqlite3.connect("sqlite.db")
                delCursor = sqliteDel.cursor()
                delCursor.execute("DROP TABLE \"" + tId + """\" """)
                sqliteDel.commit()
                break
            
            jData_length = recvall(client, 64).decode() 
            jData = recvall(client, int(jData_length)).decode()
            
            jRecv = json.loads(jData)
            
            upd_food_order_sql(str(jRecv), tId)
            
            time_orderAdd_length = recvall(client, 64).decode()
            time_orderAdd = recvall(client, int(time_orderAdd_length)).decode()
            
            sum = 0
            for i in range(len(jRecv) - 1):
                tfood = "food" + str(i + 1)
                sum = sum + int(jRecv[i+1][tfood]['num']) * int(jRecv[i+1][tfood]['price'])

            # Send total
            client.sendall(str(len(str(sum))).encode().ljust(64))
            client.sendall(str(sum).encode())
            
            while True:
                # Receive payment info
                cashAdd_length = recvall(client, 64).decode()
                cashAdd = recvall(client, int(cashAdd_length)).decode()
                
                cardAdd_length = recvall(client, 64).decode()
                cardAdd = recvall(client, int(cardAdd_length)).decode()
                
                # Pay by card
                if cardAdd != "":
                    flag = 1
                    if len(cardAdd) == 10:
                        for i in range(10):
                            if (cardAdd[i] >= '0') and (cardAdd[i] <= '9'):
                                continue
                            else:
                                flag = 0
                                cardAdd = ""
                                break 
                    else:
                        cardAdd = ""
                        flag = 0
                    
                    client.sendall(str(len(str(flag))).encode().ljust(64))
                    client.sendall(str(flag).encode())
                    
                    if flag == 1:
                        break
                else:
                    break
            # Add status payment
            add_status_payment_sql(int(sum), int(cashAdd), cardAdd, tId)
            
    curs.close()
    # data = client.recv(10000)
    # print(data.decode()) 
    
    print(clientInfo, "disconnected")

    # num_connection + 1
    num_connection[0] -= 1
    
    btn_client_connecting_str.set(str(num_connection[0]) + " client đã kết nối")
    
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

# Convert picture to Binary
def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

f_type = [("Tất cả file",".*"),("Tập tin hình ảnh",".png")]
picture_link = ""
empPhoto = [""]

# Adding picture
def add_picture(popup, fleft):
    global picture_link 
    picture_link = tkinter.filedialog.askopenfilename(parent=popup, initialdir=os.getcwd(), title="Chọn tập tin",filetypes=f_type)
    
    lbDir.configure(text=picture_link)

    empPhoto[0] = convertToBinaryData(picture_link)

    substring = StringVar()
    substring = picture_link.split("/")
    substring.reverse()
    
    picture_link = "icon/"
    picture_link += substring[0]

    btnIMG_fileReplace = Image.open(picture_link)
    btnIMG_fileReplace.thumbnail((200, 200), Image.ANTIALIAS)
    btnIMG_objectReplace= ImageTk.PhotoImage(btnIMG_fileReplace)

    btnIMG.configure(image=btnIMG_objectReplace)
    btnIMG.image = btnIMG_objectReplace

# Turn back to normal state when user click cancel
def remove_picture(fleft):
    lbDir.configure(text="No file chosen")

    btnIMG_fileReplace = Image.open("icon/fast_food.png")
    btnIMG_fileReplace.thumbnail((200, 200), Image.ANTIALIAS)
    btnIMG_objectReplace= ImageTk.PhotoImage(btnIMG_fileReplace)

    btnIMG.configure(image=btnIMG_objectReplace)
    btnIMG.image = btnIMG_objectReplace

# Add food menu to sql
def add_food_menu_sql(food_nameAdd, priceAdd, descripAdd, photoAdd):
    sql_insert_query = "INSERT INTO food_menu (food_name, price, description, image) VALUES (?, ?, ?, ?)"

    data_tuple = (food_nameAdd, priceAdd, descripAdd, photoAdd)
    dbCursor.execute(sql_insert_query, data_tuple)
    sqliteConnection.commit()

    r = Tk()
    r.geometry("300x100")
    r.title("Thêm món ăn")

    lb = Label(r, text="Đã thêm món ăn vào thực đơn!")
    lb.pack(fill=BOTH, pady=30)

    r.mainloop()

def add_food_order_sql(food_order, total, time_order, tId):
    sqliteConnectionTable = sqlite3.connect("sqlite.db")
    tableCursor = sqliteConnectionTable.cursor()
    
    sql_insert_query = "INSERT INTO \"" + tId + """\" (food_order, total, time_order) VALUES (?, ?, ?)"""
    
    data_tuple = (food_order, total, time_order)
    tableCursor.execute(sql_insert_query, data_tuple)
    sqliteConnectionTable.commit()

def add_status_payment_sql(total, cash, card, tId):
    sqliteConnectionTable = sqlite3.connect("sqlite.db")
    tableCursor = sqliteConnectionTable.cursor()
    
    sql_insert_query = "UPDATE \"" + tId + """\" SET total=?, cash=?, card=?"""
    
    data_tuple = (total, cash, card)
    tableCursor.execute(sql_insert_query, data_tuple)
    sqliteConnectionTable.commit()
    
def upd_food_order_sql(food_order, tId):
    sqliteConnectionTable1 = sqlite3.connect("sqlite.db")
    tableCursor1 = sqliteConnectionTable1.cursor()
    
    sql_insert_query = "UPDATE \"" + tId + """\" SET food_order=?"""
    
    data_tuple = [food_order]
    tableCursor1.execute(sql_insert_query, data_tuple)
    sqliteConnectionTable1.commit()

# Add food pop up windows
def add_food_popup_windows(root, sqliteConnection):
    popup = Toplevel(root)
    popup.geometry("700x500+300+300")
    popup.title("Thêm món ăn")

    fleft = Frame(popup, width=100, height=50, relief=RAISED, background="#249794")

    btnIMG_file = Image.open("icon/fast_food.png")
    btnIMG_file.thumbnail((200, 200), Image.ANTIALIAS)
    btnIMG_object= ImageTk.PhotoImage(btnIMG_file)

    global btnIMG
    btnIMG = Label(fleft, image=btnIMG_object)
    btnIMG.pack(fill=BOTH, padx=40, pady=40)

    global lbDir
    lbDir = Label(fleft, text="Không có nào được chọn")
    lbDir.pack()

    #picture_link = StringVar()
    btnInsert = Button(fleft, height=2, width=10, text="THÊM", command=lambda *agrs: add_picture(popup, fleft))
    btnInsert.pack(side=LEFT, anchor=S, padx=(30, 0), pady=15)

    btnInsert = Button(fleft, height=2, width=10, text="HỦY", command=lambda: remove_picture(fleft))
    btnInsert.pack(side=RIGHT, anchor=S, padx=(0, 30), pady=15)

    fleft.pack(fill=BOTH, side=LEFT)

    # fleft = Frame(popup, relief=RAISED, borderwidth=1)
    # fleft.pack(side=RIGHT)

    fright = Frame(popup, width=100, height=50, relief=RAISED, background="#249794")

    food_nameDir = Label(fright, text="Tên món ăn", background="#249794", foreground="#fff")
    food_nameDir.config(font=("Tahoma", 15, "bold"))
    food_nameDir.pack(anchor = W, pady=(25, 0))

    food_nameAdd = StringVar()
    food_nameText = Entry(fright, bg="white", justify=CENTER, textvariable=food_nameAdd)
    food_nameText.configure(font=("Tahoma", 15))
    food_nameText.pack(fill=BOTH, pady=(25, 0), padx=(0, 40))

    priceDir = Label(fright, text="Giá", background="#249794", foreground="#fff")
    priceDir.config(font=("Tahoma", 15, "bold"))
    priceDir.pack(anchor = W, pady=(25, 0))

    priceAdd = IntVar()
    priceText = Entry(fright, bg="white", justify=CENTER, textvariable=priceAdd)
    priceText.configure(font=("Tahoma", 15))
    priceText.pack(fill=BOTH, pady=(25, 0), padx=(0, 40))

    descripDir = Label(fright, text="Mô tả", background="#249794", foreground="#fff")
    descripDir.config(font=("Tahoma", 15, "bold"))
    descripDir.pack(anchor = W, pady=(25, 0))

    descripAdd = StringVar()
    descripText = Entry(fright, bg="white", justify=CENTER, textvariable=descripAdd)
    descripText.configure(font=("Tahoma", 15))
    descripText.pack(fill=BOTH, pady=(25, 0), padx=(0, 40))

    btnInsertR = Button(fright, height=2, width=10, text="THÊM MÓN ĂN", command=lambda: add_food_menu_sql(food_nameAdd.get(), priceAdd.get(), descripAdd.get(), empPhoto[0]))
    btnInsertR.pack(side=BOTTOM, pady=15)

    fright.pack(fill=BOTH, expand=TRUE)

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
w.overrideredirect(1)

# Set up progress bar
s = Style()
s.theme_use('clam')
s.configure("red.Horizontal.TProgressbar", foreground='red', background="#4f4f4f")
progress = Progressbar(w, style="red.Horizontal.TProgressbar", orient=HORIZONTAL, length=1000, mode='determinate')

# 'About us' window
def aboutUsWindows(q):
    popup = Toplevel(q)
    popup.title("Về chúng tôi")
    popup.geometry("400x350+300+300")

    lb1 = Label(popup, text="Nhóm 08 - 21CLC10", font=("Tahoma", 20, "bold"))
    lb1.pack(pady=(20, 0))

    lb2 = Label(popup, text="Đồ án mạng máy tính Food Order", font=("Tahoma", 15))
    lb2.pack(pady=(20, 0))

    lb3 = Label(popup, text="Thực hiện bởi:", font=("Tahoma", 13))
    lb3.pack(anchor=W, pady=(20, 0), padx=(20, 0))

    lb4 = Label(popup, justify=LEFT, text="Võ Chánh Tín - 21127182\nPhan Như Quỳnh - 21127155\nNguyễn Văn Đăng Huỳnh - 21127063", font=("Tahoma", 11, "bold"))
    lb4.pack(pady=(5, 0))

    img = Image.open("icon\\fit_logo.png")
    imgTk = ImageTk.PhotoImage(img)
    lb5 = Label(popup, image=imgTk)
    lb5.pack(pady=(10, 0))

    popup.mainloop()

# New window after splash screen
def new_win():
    q = Tk()
    q.title("Server Menu")
    q.geometry("854x500")

    btn_setting_icon = Image.open("icon/setting.png")
    btn_setting_icon.thumbnail((50, 50), Image.ANTIALIAS)
    btn_setting_img= ImageTk.PhotoImage(btn_setting_icon)
    btn_setting = Menubutton(q, text="Preferences", image=btn_setting_img)
    btn_setting.grid()
    btn_setting.menu = Menu(btn_setting, tearoff=0)
    btn_setting["menu"] = btn_setting.menu
    btn_setting.menu.add_command(label="Thêm món ăn", command=lambda:add_food_popup_windows(q, sqliteConnection))
    btn_setting.menu.add_command(label="Về chúng tôi", command=lambda:aboutUsWindows(q))
    btn_setting.pack(side=RIGHT, anchor=N, padx=(0, 10), pady=(10, 0))

    btn_client_connecting_str = StringVar()
    btn_client_connecting_str.set(str(num_connection[0]) + " client đã kết nối")
    btn_client_connecting = Button(q, textvariable=btn_client_connecting_str)
    btn_client_connecting.pack(side=RIGHT, anchor=N, padx=(0, 20), pady=(20, 0))

    lb1 = Label(q, text="Server Menu", foreground='#249794')
    lb1.config(font=("Tahoma", 30, "italic"))
    lb1.pack(side=LEFT, anchor=N, padx=(20, 0), pady=(10, 0))

    l1 = Label(q, text='127.0.0.1 | PORT 9000', fg='grey', bg=None)
    l = ('Calibri (Body)', 24, 'bold')
    l1.config(font=l)
    l1.pack(expand=TRUE)

    socket_threaded = threading.Thread(target=handle_socket_listening, args=(sck, l1, btn_client_connecting_str))
    socket_threaded.start()

    q.mainloop()    

# Config the bar at splash screen
def bar():
    l4 = Label(w, text='Đang tải...', fg="white", bg=a, anchor=S)
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
splashIMG = Image.open("icon\\splash_screen.png")
splashIMG_TK = ImageTk.PhotoImage(splashIMG)

Frame(w, width=857, height=482, bg=a).place(x=0, y=0)

l1 = Label(w, text='SERVER MANAGER', fg = 'white', bg=a, anchor=W)
lst1 = ('Courier New', 50, 'bold italic')
l1.config(font=lst1)
# l1.place(x=90, y=50)
l1.pack(fill=BOTH, padx=100, pady=(50, 0))

l2 = Label(w, text="NHÓM 08", fg="white", bg=a, anchor=W)
lst2 = ('Tahoma', 28)
l2.config(font=lst2)
# l2.place(x=90, y=110)
l2.pack(fill=BOTH, padx=100)

l3 = Label(w, text="Võ Chánh Tín\nPhan Như Quỳnh\nNguyễn Văn Đăng Huỳnh", foreground="white", background=a, justify=LEFT, anchor=W)
lst3 = ('Tahoma', 14)
l3.config(font=lst3)
l3.pack(fill=BOTH, padx=100, pady=10)

b1 = Button(w, width=20, height=2, text="Bắt đầu", command=bar, border=1, fg=a, bg="white", anchor=CENTER)
# b1.place(x=200, y=300)
b1.pack(pady=50)

w.mainloop()