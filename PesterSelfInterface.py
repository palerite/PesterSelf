from tkinter import *
from tkinter import simpledialog
# from pathlib import Path
# import os
# import sys
# import subprocess
# import datetime
from pesterself import *


def write():
    title = simpledialog.askstring(title="Writing a new message", prompt="\tPlease enter message title: \t\t")
    if not title:
        return
    msg_id = 1
    message_created = False
    while not message_created:
        try:
            msg_dir = get_message_directory() / ("Message" + str(msg_id) + ".txt")
            msg_file = msg_dir.open(mode="x")
            msg_file.writelines([
                "------------------------------\n",
                "Status: unread\n",
                f"Sent: {datetime.datetime.now().strftime('%d.%m.%Y')}\n",
                "Received: dd.mm.yyyy 00:00\n",
                "------------------------------\n",
                title+"\n"
            ])
            msg_file.close()
            with msg_dir.open() as attempt:
                if attempt.readlines():
                    open_file(msg_dir)
                    refresh_message_list()
                else:
                    try:
                        os.remove(msg_dir)
                    except FileNotFoundError:
                        pass

            message_created = True
        except FileExistsError:
            msg_id += 1
            
    return title


def open_folder():
    message_directory = get_message_directory()
    os.startfile(message_directory)


def queue_free():
    global application_exists
    application_exists = False


def refresh_message_list():
    global sc_read
    global sc_unread

    messages = get_message_list()

    sc_read.delete_all_buttons()
    sc_unread.delete_all_buttons()
    for m in messages:
        if not m.read and m.date_received <= datetime.datetime.now():
            sc_unread.add_button(m)
        elif m.read:
            sc_read.add_button(m)


def open_message(msg: Message):
    msg.open()
    refresh_message_list()


class ScrolledCanvas:
    def __init__(self, parent, color='brown'):
        self.c = Canvas(parent, bg=color)
        self.c.config(width=400, height=100)
        self.buttons = []
        self.frames = []
        self.parent = parent

        self.c.config(scrollregion=(0, 0, 400, 100))
        self.c.config(highlightthickness=0)

        scrollbar = Scrollbar(parent)
        scrollbar.config(command=self.c.yview)

        self.c.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.c.pack(side=LEFT, fill=BOTH)

    def delete_all_buttons(self):
        for frm in self.frames:
            frm.destroy()
        self.frames.clear()
        self.buttons.clear()

    def add_button(self, message: Message):
        frm = Frame(self.parent, width=400, height=20, bg="#cfcfcf")
        frm.config(relief=SUNKEN)
        self.frames.append(frm)
        btn = Button(frm, text="\"" + message.title + f"\" from {message.get_date_sent_pretty()}",
                     width=54, command=lambda x=message: open_message(x))
        self.buttons.append(btn)
        btn.grid()
        space_for_button = 25
        self.c.create_window(5, (space_for_button * len(self.buttons)) - space_for_button, anchor=NW, window=frm)
        self.c.config(scrollregion=(0, 0, 400, len(self.buttons) * space_for_button))


application_exists = True

root = Tk()
root.title("PesterSelf")
root.config(bg="#cfcecc")
root.iconbitmap("icon.ico")

RightFrame = Frame(root, bg="#cfcecc")
RightFrame.pack(side=RIGHT)

WriteButton = Button(root, text="Write a message", command=write)
WriteButton.pack(in_=RightFrame, side=TOP)
OpenFolderButton = Button(root, text="Open message folder", command=open_folder)
OpenFolderButton.pack(in_=RightFrame, side=TOP)
RefreshButton = Button(root, text="Refresh list", command=refresh_message_list)
RefreshButton.pack(in_=RightFrame, side=BOTTOM, pady=20)

FRAME_WIDTH = 200
FRAME_HEIGHT = 60

MessagesLabel = Label(root, text="Unread messages", bg="#cfcecc")
MessagesLabel.pack(side=TOP)
unread_frame = Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
unread_frame.pack(padx=5, pady=5, side=TOP, fill=NONE)
sc_unread = ScrolledCanvas(unread_frame, "white")

MessagesLabel = Label(root, text="Read messages", bg="#cfcecc")
MessagesLabel.pack(side=TOP)
read_frame = Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
read_frame.pack(padx=5, pady=5, side=TOP, fill=NONE)
sc_read = ScrolledCanvas(read_frame, "white")

buttons = list()

refresh_message_list()

root.protocol("WM_DELETE_WINDOW", queue_free)
while application_exists:
    root.update()
    root.update_idletasks()
