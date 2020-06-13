from time import *
import socket
import select
import sys
import json
import sqlite3
import random
import math
import turtle
import pygame

from tkinter import messagebox
from tkinter.ttk import *
from tkinter.filedialog import askopenfilename

import PIL
from PIL import ImageTk

from chat_utils import *
import client_state_machine as csm

import threading
from tkinter import *


class Client:
    def __init__(self, args):
        self.peer = ''
        self.console_input = []
        self.state = S_OFFLINE
        self.system_msg = ''
        self.local_msg = ''
        self.peer_msg = ''
        self.args = args
        self.name = ''
        self.running = None
        self.color = ''
        self.music = ["Seventeen_Troye Sivan.wav", "Blues_Étude.wav", "Lovely_Billie Eillish.wav", "Drive_Oh Wonder.wav",
                      "High For This_Ellie Goulding.wav", "Getaway Car_Taylor Swift.wav", "Ø_the tumbled sea.wav",
                      "Autumn Leaves_Gavin Jin.wav", "Chasers (Demo)_Bernice Feng.wav"]

    def quit(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def get_name(self):
        return self.name

    def shutdown_chat(self):
        return

    def send(self, msg):
        mysend(self.socket, msg)

    def my_send(self, event=None):
        self.console_input.append(My_msg.get())
        My_msg.set("")
        time.sleep(CHAT_WAIT)

    def mine_output(self):
        while self.sm.state != S_OFFLINE:
            read, write, error = select.select([self.socket], [], [], 0)
            my_msg = ""
            peer_msg = ""
            # peer_code = M_UNDEF    for json data, peer_code is redundant
            if len(self.console_input) > 0:
                my_msg = self.console_input.pop(0)
                self.system_msg += my_msg
                self.list_proc()
            if self.socket in read:
                peer_msg = self.recv()
            self.system_msg += self.sm.proc(my_msg, peer_msg)
            if self.system_msg:
                self.list_proc()
        self.quit()

    def recv(self):
        return myrecv(self.socket)

    def get_msgs(self):
        read, write, error = select.select([self.socket], [], [], 0)
        my_msg = ''
        peer_msg = []
        #peer_code = M_UNDEF    for json data, peer_code is redundant
        if len(self.console_input) > 0:
            my_msg = self.console_input.pop(0)
        if self.socket in read:
            peer_msg = self.recv()
        return my_msg, peer_msg

    def output(self):
        if len(self.system_msg) > 0:
            msg = self.system_msg
            self.system_msg = ''
            return msg
        return ""

    def login(self):
        my_msg, peer_msg = self.get_msgs()
        my_msg = self.name
        if len(my_msg) > 0:
            msg = json.dumps({"action": "login", "name": self.name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.state = S_LOGGEDIN
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(self.name)
                self.print_instructions()
                return (True)
            elif response["status"] == 'duplicate':
                self.system_msg += 'Duplicate username, try again'
                return False
        else:  # fix: dup is only one of the reasons
            return (False)

    def init_chat(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
        svr = SERVER if self.args.d == None else (self.args.d, CHAT_PORT)
        self.socket.connect(svr)
        self.sm = csm.ClientSM(self.socket)
        self.system_msg += 'Welcome, ' + self.get_name() + '!'
        self.list_proc()
        self.login()
        self.list_proc()

    def print_instructions(self):
        self.system_msg += menu

    def About(self):
        def moreinfo():
            moreinfo_window = Toplevel()
            moreinfo_window.title("PerFect more info")
            positionRight = int(0)
            positionDown = int(0)
            moreinfo_window.geometry("+{}+{}".format(positionRight, positionDown))
            l1 = Label(moreinfo_window, text="PerFect", font="system 30")
            l1.grid(row=1, column=1)
            l2 = Label(moreinfo_window, text="Gavin Jiayao Jin & Bernice Boning Feng", font="system 20")
            l2.grid(row=2, column=1)
            l3 = Label(moreinfo_window, text="2020 Spring ICS Final Project", font="system 20")
            l3.grid(row=3, column=1)
            l4 = Label(moreinfo_window, text="Chat System + GUI", font="system 20")
            l4.grid(row=4, column=1)
            img = ImageTk.PhotoImage(PIL.Image.open("WechatIMG152.png"))
            panel = Label(moreinfo_window, image=img)
            panel.grid(row=5, column=1)
            moreinfo_window.mainloop()
        about_window = Toplevel()
        about_window.title("PerFect")
        positionRight = int(0)
        positionDown = int(0)
        about_window.geometry("+{}+{}".format(positionRight, positionDown))
        imgperfect = ImageTk.PhotoImage(PIL.Image.open("WechatIMG5206.png"))
        l0 = Label(about_window, image=imgperfect)
        l0.grid(row=1, column=1)
        l1 = Label(about_window, text="Version 2.1.01", font="system 20")
        l1.grid(row=2, column=1)
        l2 = Label(about_window, text="2020.05  Gavin Jin&Bernice Feng~(QBLC) - QiBuLaiChuang.", font="system 15", fg="grey")
        l2.grid(row=3, column=1)
        l3 = Label(about_window, text="")
        l3.grid(row=4, column=1)
        teambutton=Button(about_window, text=" more info ", relief='raised', command=moreinfo)
        teambutton.grid(row=5, column=1)
        l4 = Label(about_window, text="")
        l4.grid(row=6, column=1)
        about_window.mainloop()

    def join(self, event=None):
        if self.sm.state == S_LOGGEDIN:
            self.console_input.append("c " + join_msg.get())
            join_msg.set("")
            time.sleep(CHAT_WAIT)
        else:
            listbox.insert(END, "   Only available when alone.")
            listbox.select_clear(listbox.size() - 2)
            listbox.select_set(END)
            listbox.yview(END)

    def search(self, event=None):
        if self.sm.state == S_LOGGEDIN:
            self.console_input.append("? " + search_msg.get())
            search_msg.set("")
            time.sleep(CHAT_WAIT)
        else:
            listbox.insert(END, "   Only available when alone.")
            listbox.select_clear(listbox.size() - 2)
            listbox.select_set(END)
            listbox.yview(END)

    def list_proc(self):
        for each in self.output().split('\n'):
            listbox.insert(END, each)
            listbox.select_clear(listbox.size() - 2)
            listbox.select_set(END)
            listbox.yview(END)

    def Time(self):
        def on_close():
            self.running = False

        turtle.TurtleScreen._RUNNING = True

        wn = turtle.Screen()
        canvas = wn.getcanvas()
        root = canvas.winfo_toplevel()
        root.protocol("WM_DELETE_WINDOW", on_close)

        wn.bgcolor = "white"
        wn.setup(width=405, height=305,startx=1000,starty=1)
        wn.title("Time")
        wn.tracer(0)

        pen = turtle.Turtle()
        pen.hideturtle()
        pen.speed(0)
        pen.pensize(1)

        def draw_clock(h, m, s, pen):
            pen.up()
            pen.goto(0, 84)
            pen.setheading(180)
            pen.color("black")
            pen.pendown()
            pen.circle(84)

            pen.penup()
            pen.goto(0, 0)
            pen.setheading(90)

            for _ in range(12):
                pen.fd(76)
                pen.pensize(2)
                pen.pendown()
                pen.fd(8)
                pen.penup()
                pen.goto(0, 0)
                pen.rt(30)

            pen.penup()
            pen.goto(0, 0)
            pen.pensize(4)
            pen.color('black')
            pen.setheading(90)
            angle = (h / 12) * 360 + (m / 60) * 30
            pen.rt(angle)
            pen.pendown()
            pen.fd(32)

            pen.penup()
            pen.goto(0, 0)
            pen.pensize(2)
            pen.color('black')
            pen.setheading(90)
            angle = (m / 60) * 360
            pen.rt(angle)
            pen.pendown()
            pen.fd(60)

            pen.penup()
            pen.goto(0, 0)
            pen.pensize(1)
            pen.pencolor((0.8, 0.1, 0.1))
            pen.setheading(90)
            angle = (s / 60) * 360
            pen.rt(angle)
            pen.pendown()
            pen.fd(72)

        self.running = True

        while self.running:
            h = int(time.strftime("%H"))
            m = int(time.strftime("%M"))
            s = int(time.strftime("%S"))
            draw_clock(h, m, s, pen)
            wn.update()       #mistake
            time.sleep(1)
            pen.clear()
        wn.bye()


    def run_chat(self):
        def on_closing():
            if messagebox.askokcancel("Quit Reminder", "Do you want to exit the chat system?"):
                self.system_msg += "See u next time!"
                self.sm.state = S_OFFLINE
                chat_window.after(500,chat_window.destroy)
                #sys.exit(0)

        def Exit():
            self.system_msg += "See u next time!"
            self.sm.state = S_OFFLINE
            chat_window.after(1000, chat_window.destroy)
            #exit(0)

        def clear_join_msg(event=None):
            join_msg.set("")
        def show_join_msg(event=None):
            join_msg.set("Join others here.")
        def clear_My_msg(event=None):
            My_msg.set("")
        def show_My_msg(event=None):
            My_msg.set("Type your message here.")
        def clear_search_msg(event=None):
            search_msg.set("")
        def show_search_msg(event=None):
            search_msg.set("Search history here.")


        global listbox, My_msg, join_msg, search_msg

        self.login_main()
        chat_window = Tk()
        #chat_window.geometry("600x400")
        w = 500
        h = 460
        ws = chat_window.winfo_screenwidth()
        hs = chat_window.winfo_screenheight()
        x = ws/2 - w/2
        y = hs/2 - h/2
        chat_window.geometry("%dx%d+%d+%d"%(w,h,x,y))
        #positionRight = int(0)
        #positionDown = int(0)
        #chat_window.geometry("+{}+{}".format(positionRight, positionDown))
        message_frame = Frame(chat_window)

        colors = ["rosybrown", "bisque", "darkkhaki", "lightsteelblue", "powderblue", "pink", "thistle","darkseagreen"]
        self.color=random.choice(colors)

        def time():
            string = strftime('%H:%M:%S %p')
            lbl.config(text=string)
            lbl.after(1000, time)
            string2 = strftime('%Y-%m-%d %X', localtime())
            lbl.config(text=string2)
        lbl = Label(chat_window, font=('Ariel', 15), bg=self.color, fg='black', relief='raised',borderwidth=2)
        lbl.pack()
        time()

        My_msg = StringVar()
        self.system_msg += "Type your message here."
        My_msg.set(self.output())

        search_btn = ImageTk.PhotoImage(PIL.Image.open("search_btn.png"))
        search_msg = StringVar()
        search_msg.set("Search history here.")
        entry_search = Entry(chat_window, width=25, textvariable=search_msg, relief='raised')
        entry_search.bind("<Return>", self.search)
        entry_search.bind("<FocusIn>", clear_search_msg)
        entry_search.bind("<FocusOut>", show_search_msg)
        entry_search.pack()
        search_button = Button(chat_window, image=search_btn, relief='raised', command=self.search)
        search_button.pack()

        scrollbar = Scrollbar(message_frame)
        listbox = Listbox(message_frame, height=15, width=50, bg=self.color, yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.pack(side=LEFT, fill=Y)

        listbox.pack()
        message_frame.pack()

        join_btn = ImageTk.PhotoImage(PIL.Image.open("join_btn.png"))
        join_msg = StringVar()
        join_msg.set("Join others here.")
        entry_c = Entry(chat_window, width=12, relief='raised', textvariable=join_msg)
        entry_c.bind("<Return>", self.join)
        entry_c.bind("<FocusIn>", clear_join_msg)
        entry_c.bind("<FocusOut>", show_join_msg)
        entry_c.pack()
        c_button = Button(chat_window, image=join_btn , relief='raised', command=self.join)
        c_button.pack()

        send_btn = ImageTk.PhotoImage(PIL.Image.open("send_btn.png"))
        entry_filed = Entry(chat_window, width=25, relief='raised', textvariable=My_msg)
        entry_filed.bind("<Return>", self.my_send)
        entry_filed.bind("<FocusIn>", clear_My_msg)
        entry_filed.bind("<FocusOut>", show_My_msg)
        entry_filed.pack()
        send_button = Button(chat_window, image=send_btn, relief='raised', command=self.my_send)
        send_button.pack()

        self.init_chat()
        chat_window.title("CS PerFect - " + self.name)

        output_thread = threading.Thread(target=self.mine_output)
        output_thread.start()

        def Stop():
            music.stop()
            self.system_msg += "    You've stopped your music.\n"
            self.system_msg += "        You can play another music using the menu bar 'Music'.\n"

        def Switch():
            global number, music
            try:
                music.stop()
                new_l = self.music.copy()
                new_l.pop(number)
                pygame.mixer.init()
                for i in range(10):
                    number = random.randint(0, len(new_l) - 1)
                music = pygame.mixer.Sound(new_l[number])
                music.play(-1)
                self.system_msg += "    Now you are listening to " + self.music_proc(new_l[number])
            except:
                pygame.mixer.init()
                for i in range(10):
                    number = random.randint(0, len(self.music) - 1)
                music = pygame.mixer.Sound(self.music[number])
                music.play(-1)
                self.system_msg += "    Now you are listening to " + self.music_proc(self.music[number])


        menu = Menu(chat_window)
        aboutmenu = Menu(menu)
        menu.add_cascade(label="About", menu=aboutmenu)
        aboutmenu.add_command(label="CS PerFect", command=self.About)
        aboutmenu.add_separator()
        aboutmenu.add_command(label="Time", command=self.Time)
        musicmenu = Menu(menu)
        menu.add_cascade(label="Music", menu=musicmenu)
        musicmenu.add_command(label="Stop", command=Stop)
        musicmenu.add_separator()
        musicmenu.add_command(label="Switch/Play", command=Switch)

        windowmenu = Menu(menu)
        menu.add_cascade(label="Window", menu=windowmenu)
        windowmenu.add_command(label="Exit " + str(self.name), command=Exit)
        chat_window.config(menu=menu)


        global number, music
        pygame.mixer.init()
        for i in range(10):
            number = random.randint(0, len(self.music) - 1)
        music = pygame.mixer.Sound(self.music[number])
        music.play(-1)
        self.system_msg += "    Now you are listening to " + self.music_proc(self.music[number])
        self.system_msg += "\n      You can stop or swith music using the menu bar 'Music'.\n"

        chat_window.protocol("WM_DELETE_WINDOW", on_closing)
        chat_window.mainloop()

#==============================================================================
# main processing loop
#==============================================================================

    def music_proc(self,name):
        name = name[:-4]
        music_name, author = name.split("_")[0], name.split("_")[1]
        return "'%s'"%music_name + " by " + author + '.'

    def mine_login(self):
        def on_close_window():
            if messagebox.askokcancel("Quit Reminder", "Do you want to exit the chat system?"):
                login_window.destroy()
                exit(0)

        def back(event=None):
            login_window.destroy()
            self.login_main()

        def Exit():
            login_window.destroy()
            exit(0)

        def login_database(event=None):
            conn = sqlite3.connect("login.db")
            cur = conn.cursor()
            cur.execute("SELECT * FROM test WHERE username=? AND password=?", (e1.get(), e2.get()))
            row = cur.fetchall()
            conn.close()
            if row != []:
                s="Login successful"
                self.name = e1.get()
                correct_sound = pygame.mixer.Sound("succeed.wav")
                correct_sound.play()
                login_window.after(1000, login_window.destroy)
            else:
                s="No username/password"
                fail_sound = pygame.mixer.Sound("fail.wav")
                fail_sound.play()
            l4 = Label(login_window, text=s, bg="MediumAquamarine", font="times 15", width=20)
            l4.grid(row=6, column=2)

        def display(event=None):
            e2["show"] = ""
            b3.config(image=eye_show)

        def hide(event=None):
            e2["show"] = "*"
            b3.config(image=eye_hide)

        window.destroy()
        pygame.mixer.init()
        login_window = Tk()
        login_window.title("Login")
        login_window.geometry("405x188")
        w = 405
        h = 188
        ws = login_window.winfo_screenwidth()
        hs = login_window.winfo_screenheight()
        x = ws / 2 - w / 2
        y = hs / 2 - h / 2
        login_window.geometry("%dx%d+%d+%d" % (w, h, x, y))
        login_window.configure(background="MediumAquamarine")

        l1 = Label(login_window, text="Username: ", bg="MediumAquamarine", font="times 20")
        l1.grid(row=1, column=1)
        l2 = Label(login_window, text="Password: ", bg="MediumAquamarine", font="times 20")
        l2.grid(row=2, column=1)

        username_text = StringVar()
        e1 = Entry(login_window, relief='raised', textvariable=username_text)
        e1.grid(row=1, column=2)
        password_text = StringVar()
        e2 = Entry(login_window, relief='raised', textvariable=password_text)
        e2["show"] = "*"
        e2.bind("<Return>", login_database)
        e2.grid(row=2, column=2)

        eye_hide = ImageTk.PhotoImage(PIL.Image.open("eye_hide.png"))
        eye_show = ImageTk.PhotoImage(PIL.Image.open("eye_show.png"))

        b1 = Button(login_window, text="login", width=10, relief='raised', command=login_database)
        b1.grid(row=3, column=2)
        b2 = Button(login_window, text="back", width=10, relief='raised', command=back)
        b2.grid(row=4, column=2)
        b3 = Button(login_window, image=eye_hide)
        b3.bind("<Enter>", display)
        b3.bind("<Leave>", hide)
        b3.grid(row=2, column=3)
        login_window.bind("<Escape>", back)

        login_window.protocol("WM_DELETE_WINDOW", on_close_window)

        menu = Menu(login_window)
        aboutmenu = Menu(menu)
        menu.add_cascade(label="About", menu=aboutmenu)
        aboutmenu.add_command(label="Chat system", command=self.About)
        aboutmenu.add_separator()
        aboutmenu.add_command(label="Time", command=self.Time)
        windowmenu = Menu(menu)
        menu.add_cascade(label="Exit", menu=windowmenu)
        windowmenu.add_command(label="Exit", command=Exit)
        login_window.config(menu=menu)

        login_window.protocol("WM_DELETE_WINDOW", on_close_window)

        login_window.mainloop()

    def register(self):
        def on_close_window():
            if messagebox.askokcancel("Quit Reminder", "Do you want to exit the chat system?"):
                register_window.destroy()
                exit(0)

        def back(event=None):
            register_window.destroy()
            self.login_main()

        def Exit():
            register_window.destroy()
            exit(0)

        def register_database(event=None):
            conn = sqlite3.connect("login.db")
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS test(id INTEGER PRIMARY KEY,username text, password text)")
            cur.execute("SELECT * FROM test")
            row = cur.fetchall()
            result = [i[1] for i in row]
            if e1.get() in result:
                s = "Name used"
                fail_sound = pygame.mixer.Sound("fail.wav")
                fail_sound.play()
            elif not e1.get():
                s = "User name!!!"
                fail_sound = pygame.mixer.Sound("fail.wav")
                fail_sound.play()
            elif not e2.get():
                s = "Password!!!"
                fail_sound = pygame.mixer.Sound("fail.wav")
                fail_sound.play()
            else:
                cur.execute("INSERT INTO test Values(Null,?,?)", (e1.get(), e2.get()))
                s = "Account created"
                correct_sound = pygame.mixer.Sound("succeed.wav")
                correct_sound.play()
            l4 = Label(register_window, text=s, bg= "lightSalmon", font="times 15", width=15)
            l4.grid(row=6, column=2)

            conn.commit()
            conn.close()

        def display(event=None):
            e2["show"] = ""
            b3.config(image=eye_show)
        def hide(event=None):
            e2["show"] = "*"
            b3.config(image=eye_hide)

        window.destroy()
        pygame.mixer.init()
        register_window = Tk()
        register_window.geometry("405x188")
        w = 405
        h = 188
        ws = register_window.winfo_screenwidth()
        hs = register_window.winfo_screenheight()
        x = ws / 2 - w / 2
        y = hs / 2 - h / 2
        register_window.geometry("%dx%d+%d+%d" % (w, h, x, y))
        register_window.configure(background="LightSalmon")
        register_window.title("Register")
        l1 = Label(register_window, text="Username: ", bg="LightSalmon", font="times 20")
        l1.grid(row=1, column=1)
        l3 = Label(register_window, text="Password: ", bg="LightSalmon", font="times 20")
        l3.grid(row=2, column=1)

        name_text = StringVar()
        e1 = Entry(register_window, relief='raised', textvariable=name_text)
        e1.grid(row=1, column=2)
        pass_text = StringVar()
        e2 = Entry(register_window, relief='raised', textvariable=pass_text)
        e2["show"] = "*"
        e2.bind("<Return>", register_database)
        e2.grid(row=2, column=2)

        eye_hide = ImageTk.PhotoImage(PIL.Image.open("eye_hide.png"))
        eye_show = ImageTk.PhotoImage(PIL.Image.open("eye_show.png"))

        b1 = Button(register_window, text="register", width=10, relief='raised', command=register_database)
        b1.grid(row=3, column=2)
        b2 = Button(register_window, text="back", width=10, relief='raised', command=back)
        b2.grid(row=4, column=2)
        b3 = Button(register_window, image=eye_hide)
        b3.bind("<Enter>", display)
        b3.bind("<Leave>", hide)
        b3.grid(row=2, column=3)
        register_window.bind("<Escape>", back)
        register_window.protocol("WM_DELETE_WINDOW", on_close_window)

        menu = Menu(register_window)
        aboutmenu = Menu(menu)
        menu.add_cascade(label="About", menu=aboutmenu)
        aboutmenu.add_command(label="Chat system", command=self.About)
        aboutmenu.add_separator()
        aboutmenu.add_command(label="Time", command=self.Time)
        windowmenu = Menu(menu)
        menu.add_cascade(label="Exit", menu=windowmenu)
        windowmenu.add_command(label="Exit", command=Exit)
        register_window.config(menu=menu)

        register_window.protocol("WM_DELETE_WINDOW", on_close_window)

        register_window.mainloop()

    def login_main(self):
        def on_close_window():
            if messagebox.askokcancel("Quit Reminder", "Do you want to exit the chat system?"):
                window.destroy()
                exit(0)

        def Exit():
            window.destroy()
            exit(0)

        global window
        window = Tk()
        window.geometry("405x188")
        w = 405
        h = 188
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()
        x = ws / 2 - w / 2
        y = hs / 2 - h / 2
        window.geometry("%dx%d+%d+%d" % (w, h, x, y))
        window.title("CS PerFect")

        #l1 = Label(window, text="Login or Register", font="times 20")
        img = ImageTk.PhotoImage(PIL.Image.open("WechatIMG4809.png"))
        l1 = Label(window, image=img)
        l1.grid(row=1,column=2,columnspan=3)

        b1 = Button(window, text="login", width=22, height=2, fg="black", highlightbackground="MediumAquamarine",
                    relief='raised', command=self.mine_login)
        b1.grid(row=2, column=2)

        b2 = Button(window, text="register", width=22, height=2, fg="black", highlightbackground="LightSalmon",
                    relief='raised', command=self.register)
        b2.grid(row=2, column=3)

        menu = Menu(window)
        aboutmenu = Menu(menu)
        menu.add_cascade(label="About", menu=aboutmenu)
        aboutmenu.add_command(label="Chat system", command=self.About)
        aboutmenu.add_separator()
        aboutmenu.add_command(label="Time", command=self.Time)
        windowmenu = Menu(menu)
        menu.add_cascade(label="Exit", menu=windowmenu)
        windowmenu.add_command(label="Exit", command=Exit)

        window.config(menu=menu)

        window.protocol("WM_DELETE_WINDOW", on_close_window)
        window.mainloop()
