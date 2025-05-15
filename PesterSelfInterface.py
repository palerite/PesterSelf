from tkinter import *
from tkinter import messagebox
# from pathlib import Path
# import sys
# import subprocess
# import datetime
import shutil
from pesterself import *
import signal


def open_write_dialogue():
    return MessageWriter()


def open_folder():
    message_directory = get_message_directory()
    if sys.platform == "win32":
        os.startfile(message_directory)
    elif sys.platform == "darwin":
        subprocess.call(["open", message_directory])
    else:
        subprocess.call(["xdg-open", message_directory])


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


def delete_message(msg: Message):
    answer = messagebox.askyesno("Confirmation", f"Are you sure you want to delete \"{msg.title}\"?\n"
                                 f"(No undo)")
    if answer:
        if msg.delete() == 0:
            refresh_message_list()
        else:
            messagebox.showinfo("Something went wrong")


STARTUP_FILE_NAME = "PesterSelf Notification System shortcut file.vbs"


def add_to_startup():
    if sys.platform == "win32":
        try:
            with open(STARTUP_FILE_NAME, "w") as shortcut:
                shortcut.writelines(SHORTCUT_LINES)

            shutil.copyfile(Path(STARTUP_FILE_NAME), get_startup_directory() /
                            STARTUP_FILE_NAME)
            os.remove(STARTUP_FILE_NAME)
        except FileNotFoundError:
            messagebox.showinfo("Response", "Couldn't add Notification System to startup apps. \
                                PesterSelf Notification System.lnk missing ")
    elif sys.platform == "darwin":
        pass
    else:
        with Path(Path.home() / ".bashrc").open("a") as startup_file:
            startup_file.write(BASHRC_LINE)


def remove_from_startup():
    if sys.platform == "win32":
        try:
            os.remove(get_startup_directory() / STARTUP_FILE_NAME)
        except FileNotFoundError:
            messagebox.showinfo("Response", "Couldn't remove Notification System from startup apps. \
            The shortcut name must have been changed.")
    elif sys.platform == "darwin":
        pass
    else:
        with Path(Path.home() / ".bashrc").open("r") as startup_file:
            lines = startup_file.readlines()
        for line in lines:
            if BASHRC_LINE.strip('\n') in line:
                lines.remove(line)
        with Path(Path.home() / ".bashrc").open("w") as startup_file:
            startup_file.writelines(lines)


def stop_notification_system():
    with (get_message_directory()/"notif.log").open() as log:
        pid = check_pid(log)
        if pid == 0:
            messagebox.showinfo("Response", "Looks like it was already stopped.")
            return
        try:
            os.kill(pid, signal.SIGTERM)
            messagebox.showinfo("Response", "Successfully stopped the Notification System.")
            with (get_message_directory() / "notif.log").open("w") as log_file:
                log_file.write("0")
            print("Notification System successfully disabled")
        except PermissionError:
            messagebox.showinfo("Response", "Couldn't do that. It probably was already stopped.")
        except OSError:
            messagebox.showinfo("Response", "Couldn't do that. It probably was already stopped.")


def start_notification_system():
    with (get_message_directory() / "notif.log").open() as log:
        pid = check_pid(log)
        if pid > 0:
            try:
                os.kill(pid, signal.SIGTERM)
                open_file(NS_NAME)
                messagebox.showinfo("Response", "Notification System restarted!")
                return
            except PermissionError:
                pass
            except OSError:
                pass

    open_file(NS_NAME)
    messagebox.showinfo("Response", "Notification System started!")


class LabeledEntry(Entry):
    def __init__(self, parent, label, **kwargs):
        Entry.__init__(self, parent, **kwargs)
        self.label = label
        self.on_exit("<FocusOut>")
        self.bind("<FocusIn>", self.on_entry)
        self.bind("<FocusOut>", self.on_exit)

    def on_entry(self, _event):
        if self.get() == self.label:
            self.delete(0, "end")
            self.insert(0, "")
            self.config(fg="black")

    def on_exit(self, _event):
        if self.get() == "":
            self.insert(0, self.label)
            self.config(fg="grey")


class MessageWriter:
    def __init__(self):
        self.window = Toplevel(root)
        self.window.iconbitmap("icon.ico")
        self.window.title("Writing a new message")
        # self.window.protocol('WM_DELETE_WINDOW', lambda arg=self.window: decrease_notification_amount(arg))
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        rw = 240
        rh = int(rw * 3 / 4)
        self.window.geometry(f"{rw}x{rh}+{sw//2 - rw//2}+{sh//2 - rh//2}")
        frame_bottom = Frame(self.window)
        frame_bottom.pack(side=BOTTOM, padx=5, pady=5, fill=BOTH)
        frame_right = Frame(self.window)
        frame_right.pack(side=RIGHT, padx=5, pady=5, fill=X)
        frame_left = Frame(self.window)
        frame_left.pack(side=LEFT, padx=5, pady=5, fill=X)

        title_label = Label(frame_left, text="Message title:")
        title_label.pack(side=TOP)
        self.date_var = StringVar()
        self.date_var.trace_add("write", self.watch_date)
        self.date_var_past = ""
        date_label = Label(frame_left, text="Delivery date:")
        date_label.pack(side=BOTTOM)

        self.title_entry = Entry(frame_right)
        self.title_entry.pack(side=TOP)
        self.date_entry = LabeledEntry(frame_right, textvariable=self.date_var, label="dd.mm.yyyy hh:mm")
        self.date_entry.pack(side=BOTTOM)

        ok_button = Button(frame_bottom, text="Create message", command=self.write)
        ok_button.pack(padx=5)
        cancel_button = Button(frame_bottom, text="Cancel", command=self.be_gone)
        cancel_button.pack(padx=5)

    def watch_date(self, _var, _index, _mode):
        date = self.date_var.get()
        if len(self.date_var_past) < len(date):
            if re.match(r"\d{2}$", date):
                self.date_entry.insert("end", ".")
            elif re.match(r"\d{2}\.\d{2}$", date):
                self.date_entry.insert("end", ".")
            elif re.match(r"\d{2}\.\d{2}\.\d{4}$", date):
                self.date_entry.insert("end", " ")
            elif re.match(r"\d{2}\.\d{2}\.\d{4} \d{2}$", date):
                self.date_entry.insert("end", ":")
            elif re.match(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}.$", date):
                print("Oh?")
                self.date_var.set(self.date_var_past)
        self.date_var_past = self.date_var.get()

    def be_gone(self):
        self.window.destroy()

    def write(self):
        title = self.title_entry.get()
        date = self.date_entry.get()
        if not re.match(r"\d{2}\.\d{2}\.\d{4}.*", date) and not title:
            messagebox.showinfo("Response", "Incorrect date format and empty title")
            return
        elif not title:
            messagebox.showinfo("Response", "Message title can not be empty")
            return
        elif not re.match(r"\d{2}\.\d{2}\.\d{4}.*", date):
            messagebox.showinfo("Response", "Incorrect date format")
            return
        elif not is_date_valid(date):
            print(date)
            messagebox.showinfo("Response", "Invalid date")
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
                    f"Received: {date}\n",
                    "------------------------------\n",
                    title + "\n"
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
        self.be_gone()


class SettingsWindow:
    def __init__(self):
        self.tl = Toplevel(root)
        self.tl.title("PesterSelf settings")
        self.tl.iconbitmap("icon.ico")
        sw = self.tl.winfo_screenwidth()
        self.rw = int(sw / 2.5)
        rh = int(self.rw * 3 / 4)
        self.tl.geometry(f"{self.rw}x{rh}+{50}+{50}")
        self.tl.protocol('WM_DELETE_WINDOW', self.destroy)
        top_frame = Frame(self.tl, borderwidth=5, relief=SUNKEN)
        top_frame.pack(side=TOP, padx=10, pady=10)

        self.settings = get_settings()

        self.inspection_interval, self.interval_entry = self.add_entry_setting(
            "inspection_interval",
            "\t Inspection interval (min): ",
            "How often the Notification System checks for new messages. Effective on Notification System restart",
        )
        self.notification_size, self.size_entry = self.add_entry_setting(
            "notification_size",
            "Notification size (x / screen width): ",
            "How big the notification popup is in relation to the screen's width."
        )
        self.launch_on_startup, self.startup_check = self.add_check_setting(
            "launch_on_startup",
            "Notification System on startup: ",
            "Determines if the Notification System is launched on device startup."
        )

        bottom_frame = Frame(self.tl)
        bottom_frame.pack(side=BOTTOM, padx=20, pady=20)
        button_apply = Button(bottom_frame, text="Apply", command=self.apply_settings)
        button_apply.pack(side=LEFT, padx=5)
        button_close = Button(bottom_frame, text="Close and apply", command=self.destroy)
        button_close.pack(side=RIGHT, padx=5)
        button_defaults = Button(bottom_frame, text="Restore defaults", command=self.set_default_settings)
        button_defaults.pack(side=RIGHT, padx=5)

    def apply_settings(self):
        new_settings = {
            "launch_on_startup": str(self.launch_on_startup.get()),
            "notification_size": str(self.notification_size.get()),
            "inspection_interval": str(self.inspection_interval.get()),
        }

        if self.launch_on_startup.get() and new_settings["launch_on_startup"] != self.settings["launch_on_startup"]:
            add_to_startup()
        elif not self.launch_on_startup.get() and \
                new_settings["launch_on_startup"] != self.settings["launch_on_startup"]:
            remove_from_startup()

        set_settings(new_settings)
        self.settings = new_settings

    def set_default_settings(self):
        if DEFAULT_SETTINGS["launch_on_startup"] != self.settings["launch_on_startup"]:
            self.startup_check.toggle()
        self.size_entry.delete(0, 999)
        self.size_entry.insert(0, DEFAULT_SETTINGS["notification_size"])
        self.interval_entry.delete(0, 999)
        self.interval_entry.insert(0, DEFAULT_SETTINGS["inspection_interval"])
        set_settings(DEFAULT_SETTINGS)
        self.settings = DEFAULT_SETTINGS

    def add_entry_setting(self, name: str, label_text: str, description: str):
        frame_setting = Frame(self.tl)
        frame_setting.pack(side=TOP)
        setting_label = Label(frame_setting, text=label_text, width=30, justify=RIGHT)
        setting_label.pack(side=LEFT)
        setting_label2 = Label(frame_setting, text=description, wraplength=150, anchor=W,
                               justify=LEFT, width=30)
        setting_label2.pack(side=RIGHT, padx=5, pady=5)
        setting_variable = StringVar()
        setting_entry = Entry(frame_setting, textvariable=setting_variable, width=10)
        setting_entry.insert(0, self.settings[name])
        setting_entry.pack(side=RIGHT)
        return setting_variable, setting_entry

    def add_check_setting(self, name: str, label_text: str, description: str):
        frame_setting = Frame(self.tl)
        frame_setting.pack(side=TOP)
        setting_label = Label(frame_setting, text=label_text, width=30, justify=RIGHT)
        setting_label.pack(side=LEFT)
        setting_label2 = Label(frame_setting, text=description, wraplength=150, anchor=W,
                               justify=LEFT, width=30)
        setting_label2.pack(side=RIGHT, padx=5, pady=5)
        setting_variable = BooleanVar()
        setting_check = Checkbutton(frame_setting, width=5, variable=setting_variable)
        if self.settings[name] == "True":
            setting_check.select()
        setting_check.pack(side=RIGHT)
        return setting_variable, setting_check

    def destroy(self):
        global settings_open
        self.apply_settings()
        settings_open = False
        self.tl.destroy()


def open_settings():
    global settings_open
    if settings_open:
        return
    settings_open = True
    settings = SettingsWindow()
    settings.tl.after(30, settings.tl.focus_force)


class ScrolledCanvas:
    def __init__(self, parent, color='brown'):
        self.c = Canvas(parent, bg=color)
        self.c.config(width=400, height=100)
        self.buttons = []
        self.frames = []
        self.parent = parent
        self.del_icon = PhotoImage(file=r"garbage_bin_icon.png")

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
        frm = Frame(self.parent, width=400, height=20, bg="white")
        frm.config(relief=SUNKEN)
        self.frames.append(frm)
        btn = Button(frm, text="\"" + message.title + f"\" from {message.get_date_sent_pretty()}",
                     width=50, command=lambda x=message: open_message(x))
        btn_del = Button(frm, image=self.del_icon, text="D", command=lambda x=message: delete_message(x))
        self.buttons.append(btn)
        btn.pack(side=LEFT)
        btn_del.pack(side=RIGHT)
        space_for_button = 25
        self.c.create_window(5, (space_for_button * len(self.buttons)) - space_for_button, anchor=NW, window=frm)
        self.c.config(scrollregion=(0, 0, 400, len(self.buttons) * space_for_button))


(get_message_directory() / "notif.log").touch()
application_exists = True
settings_open = False

root = Tk()
root.title("PesterSelf")
root.config(bg="#cfcecc")
root.iconbitmap("icon.ico")
DEFAULT_SETTINGS["notification_size"] = str(root.winfo_screenwidth()//3)

RightFrame = Frame(root, bg="#cfcecc")
RightFrame.pack(side=RIGHT)

WriteButton = Button(root, text="Write a message", command=open_write_dialogue)
WriteButton.pack(in_=RightFrame, side=TOP)
SettingsButton = Button(root, text="Settings", command=open_settings)
SettingsButton.pack(in_=RightFrame, side=TOP)
OpenFolderButton = Button(root, text="Open message folder", command=open_folder)
OpenFolderButton.pack(in_=RightFrame, side=TOP)
RefreshButton = Button(root, text="Refresh list", command=refresh_message_list)
RefreshButton.pack(in_=RightFrame, pady=20)


NotifFrame = Frame(RightFrame, bg="#cfcecc")
NotifFrame.pack(side=BOTTOM)
NotifLabel = Label(RightFrame, text="Notification System\ncontrols", bg="#cfcecc")
NotifLabel.pack(side=TOP)
StopButton = Button(root, text="Stop", command=stop_notification_system)
StopButton.pack(in_=NotifFrame, padx=2, side=RIGHT)
StartButton = Button(root, text="Start", command=start_notification_system)
StartButton.pack(in_=NotifFrame, padx=2, side=LEFT)

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

if not Path("settings.cfg").exists():
    messagebox.showinfo("Thank you for downloading PesterSelf",
                        "You can set the notification system to turn on automatically on device startup in settings")

buttons = list()

refresh_message_list()

root.protocol("WM_DELETE_WINDOW", queue_free)
while application_exists:
    root.update()
    root.update_idletasks()
