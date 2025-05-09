from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
# from pathlib import Path
# import sys
# import subprocess
# import datetime
import shutil
from pesterself import *
import signal


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


def add_to_startup():
    if sys.platform == "win32":
        try:
            shutil.copyfile(Path("PesterSelf Notification System.lnk"), get_startup_directory() /
                            "PesterSelf Notification System.lnk")
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
            os.remove(get_startup_directory() / "PesterSelf Notification System.lnk")
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
        pid = int(log.readline())
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
        pid = int(log.readline())
        if pid != 0:
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
        top_frame = Frame(self.tl)
        top_frame.pack(side=TOP, padx=10, pady=10, fill=Y)

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
settings_open = False

root = Tk()
root.title("PesterSelf")
root.config(bg="#cfcecc")
root.iconbitmap("icon.ico")

RightFrame = Frame(root, bg="#cfcecc")
RightFrame.pack(side=RIGHT)

WriteButton = Button(root, text="Write a message", command=write)
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
