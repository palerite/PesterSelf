from tkinter import messagebox
import tkinter.font
import shutil
from pesterself import *
import signal


STARTUP_FILE_NAME = "PesterSelf Notification System shortcut file.vbs"


def open_write_dialogue():
    return MessageWriter()


def open_folder():
    open_file(get_message_directory())


def queue_free(wdw: Tk):
    global application_exists
    application_exists = False
    wdw.destroy()


def refresh_message_list():
    global SCRead
    global SCUnread

    messages = get_message_list()

    SCRead.be_gone()
    SCUnread.be_gone()
    SCUnread = ScrolledCanvas(UnreadFrame, "white")
    SCRead = ScrolledCanvas(ReadFrame, "white")

    for m in messages:
        if not m.read and m.date_received <= datetime.datetime.now():
            SCUnread.add_button(m)
        elif m.read:
            SCRead.add_button(m)


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


def add_to_startup():
    startup_file_name = get_settings()["startup_file"]
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
        with open("NotificationSystemRunner.sh", "w") as shell_file:
            shell_file.writelines(NOTIFICATION_RUNNER_LINES)
        os.system("chmod +x NotificationSystemRunner.sh")
        with Path(Path.home() / startup_file_name).open("a") as startup_file:
            startup_file.writelines(BASHRC_LINES)


def remove_from_startup():
    startup_file_name = get_settings()["startup_file"]
    if sys.platform == "win32":
        try:
            os.remove(get_startup_directory() / STARTUP_FILE_NAME)
        except FileNotFoundError:
            messagebox.showinfo("Response", "Couldn't remove Notification System from startup apps. \
            The shortcut name must have been changed.")
    elif sys.platform == "darwin":
        pass
    else:
        with Path(Path.home() / startup_file_name).open("r") as startup_file:
            lines = startup_file.readlines()
        lines_to_remove = list()
        for line in lines:
            for l in BASHRC_LINES:
                if l.strip('\n') in line:
                    lines_to_remove.append(line)
        for line in lines_to_remove:
            lines.remove(line)
        with Path(Path.home() / startup_file_name).open("w") as startup_file:
            startup_file.writelines(lines)


def stop_notification_system():
    with (get_message_directory()/"notif.log").open() as log:
        pid = check_pid(log)
        if pid <= 0:
            messagebox.showinfo("Response", "Looks like it was already stopped.")
            return
        try:
            os.kill(pid, signal.SIGTERM)
            messagebox.showinfo("Response", "Successfully stopped the Notification System.")
            with (get_message_directory() / "notif.log").open("w") as log_file:
                log_file.write("0")
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
                execute_file(NS_NAME)
                messagebox.showinfo("Response", "Notification System restarted!")
                return
            except PermissionError:
                pass
            except OSError:
                pass

    execute_file(NS_NAME)
    messagebox.showinfo("Response", "Notification System started!")


def set_text_size(s: int):
    global CHARACTER_WIDTH
    default_font.configure(size=s)
    CHARACTER_WIDTH = default_font.measure("n")


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
        set_icon(self.window)
        self.window.title("Writing a new message")
        # self.window.protocol('WM_DELETE_WINDOW', lambda arg=self.window: decrease_notification_amount(arg))
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        # rw = 240
        # rh = int(rw * 3 / 4)
        # self.window.geometry(f"{rw}x{rh}+{sw//2 - rw//2}+{sh//2 - rh//2}")
        frame_bottom = Frame(self.window)
        frame_bottom.pack(side="bottom", padx=5, pady=5, fill="both")
        frame_right = Frame(self.window)
        frame_right.pack(side="right", padx=5, pady=5, fill="x")
        frame_left = Frame(self.window)
        frame_left.pack(side="left", padx=5, pady=5, fill="x")

        title_label = Label(frame_left, text="Message title:")
        title_label.pack(side="top")
        self.date_var = StringVar()
        self.date_var.trace_add("write", self.watch_date)
        self.date_var_past = ""
        date_label = Label(frame_left, text="Delivery date:")
        date_label.pack(side="bottom")

        self.title_entry = Entry(frame_right)
        self.title_entry.pack(side="top")
        self.date_entry = LabeledEntry(frame_right, textvariable=self.date_var, label="dd.mm.yyyy hh:mm")
        self.date_entry.pack(side="bottom")

        ok_button = Button(frame_bottom, text="Create message", command=self.write)
        ok_button.pack(padx=5)
        cancel_button = Button(frame_bottom, text="Cancel", command=self.be_gone)
        cancel_button.pack(padx=5)
        self.title_entry.focus_force()

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


class WidgetSetting:
    def __init__(self, parent, name: str, label_text: str, description: str, visible=True):
        self.setting_frame = Frame(parent)
        self.name = name
        if visible:
            self.setting_frame.pack(side="top")
        setting_label = Label(self.setting_frame, text=label_text, width=30, justify="right")
        setting_label.pack(side="left")
        setting_label2 = Label(self.setting_frame, text=description, wraplength=150, anchor="w",
                               justify="left", width=30)
        setting_label2.pack(side="right", padx=5, pady=5)
        self.setting_variable = StringVar()
        self.setting_widget = Label(self.setting_frame)

    def get(self):
        return self.setting_variable.get()

    def set_default(self):
        pass


class EntrySetting(WidgetSetting):
    def __init__(self, parent, name: str, label_text: str, description: str, visible=True):
        super().__init__(parent, name, label_text, description, visible)
        self.setting_widget = Entry(self.setting_frame, textvariable=self.setting_variable, width=10)
        self.setting_widget.insert(0, get_settings()[name])

        self.setting_widget.pack(side="right")

    def set_default(self):
        self.setting_widget.delete(0, "end")
        self.setting_widget.insert(0, DEFAULT_SETTINGS[self.name])


class CheckboxSetting(WidgetSetting):
    def __init__(self, parent, name: str, label_text: str, description: str, visible=True):
        super().__init__(parent, name, label_text, description, visible)
        self.setting_widget = Checkbutton(self.setting_frame, width=5, variable=self.setting_variable)
        if get_settings()[name] == "True":
            self.setting_widget.select()
        self.setting_widget.pack(side="right")

    def set_default(self):
        if DEFAULT_SETTINGS["launch_on_startup"] != self.get():
            self.setting_widget.toggle()


class SpinboxSetting(WidgetSetting):
    def __init__(self, parent, name: str, label_text: str, description: str, mn: int, mx: int, visible=True):
        super().__init__(parent, name, label_text, description, visible)
        self.minimal_value = mn
        self.maximal_value = mx
        self.setting_widget = Spinbox(self.setting_frame, textvariable=self.setting_variable, from_=mn, to=mx)
        self.setting_widget.delete(0, "end")
        self.setting_widget.insert(1, get_settings()[name])

        self.setting_widget.pack(side="right")

    def set_default(self):
        self.setting_widget.delete(0, "end")
        self.setting_widget.insert(0, DEFAULT_SETTINGS[self.name])

    def get(self):
        try:
            return str(min(self.maximal_value, max(self.minimal_value, int(self.setting_variable.get()))))
        except ValueError:
            return DEFAULT_SETTINGS[self.name]


class SettingsWindow:
    def __init__(self):
        self.tl = Toplevel(root)
        self.tl.title("PesterSelf settings")
        set_icon(self.tl)
        sw = self.tl.winfo_screenwidth()
        self.rw = int(sw / 2)
        rh = int(self.rw * 3 / 4)
        self.tl.geometry(f"{self.rw}x{rh}+{50}+{50}")
        self.tl.protocol('WM_DELETE_WINDOW', self.destroy)

        bottom_frame = Frame(self.tl)
        button_defaults = Button(bottom_frame, text="Restore defaults", command=self.set_default_settings)
        button_defaults.pack(side="right", padx=5)
        bottom_frame.pack(side="bottom", padx=20, pady=20)
        button_apply = Button(bottom_frame, text="Apply", command=self.apply_settings)
        button_apply.pack(side="left", padx=5)
        button_close = Button(bottom_frame, text="Close and apply", command=self.destroy)
        button_close.pack(side="right", padx=5)

        top_frame = Frame(self.tl, borderwidth=5, relief="sunken")
        top_frame.pack(side="top", padx=10, pady=10)

        self.settings = get_settings()

        self.setting_widgets: dict[str, WidgetSetting] = dict()

        self.setting_widgets["text_size"] = SpinboxSetting(self.tl,
            "text_size",
            "Text size: ",
            "How big the Text is in the interface. No effect on Notification System.",
            5, 24
        )
        self.setting_widgets["inspection_interval"] = SpinboxSetting(self.tl,
            "inspection_interval",
            "\t Inspection interval (min): ",
            "How often the Notification System checks for new messages. Effective on Notification System restart",
            1, 9999
        )
        self.setting_widgets["notification_size"] = SpinboxSetting(self.tl,
            "notification_size",
            "Notification size (px): ",
            "How wide the notification popup is.",
            100, 9999
        )
        self.setting_widgets["launch_on_startup"] = CheckboxSetting(self.tl,
            "launch_on_startup",
            "Notification System on device startup: ",
            "Determines if the Notification System is launched on device startup.",
        )
        self.setting_widgets["startup_file"] = EntrySetting(self.tl,
        "startup_file",
        "Custom startup file path: ",
        "Please only change this if you know what you are doing. "
        "can only be altered if Notification System on startup' is currently disabled",
        visible=sys.platform not in ["win32", "darwin"])

        if self.settings["launch_on_startup"] == "True":
            self.setting_widgets["startup_file"].setting_widget.config(state="disabled")

    def apply_settings(self):
        new_settings = dict()

        for widget in self.setting_widgets.values():
            new_settings[widget.name] = widget.get()

        if self.setting_widgets["launch_on_startup"].get() and new_settings["launch_on_startup"] != self.settings["launch_on_startup"]:
            add_to_startup()
            self.setting_widgets["startup_file"].setting_widget.config(state="disabled")
        elif not self.setting_widgets["launch_on_startup"].get() and \
                new_settings["launch_on_startup"] != self.settings["launch_on_startup"]:
            remove_from_startup()
            self.setting_widgets["launch_on_startup"].setting_widget.config(state="normal")

        set_text_size(int(new_settings["text_size"]))

        set_settings(new_settings)
        self.settings = new_settings

        refresh_message_list()

    def set_default_settings(self):
        for widget in self.setting_widgets.values():
            widget.set_default()
        set_settings(DEFAULT_SETTINGS)
        self.settings = DEFAULT_SETTINGS
        self.apply_settings()

    def add_entry_setting(self, name: str, label_text: str, description: str, visible=True):
        frame_setting = Frame(self.tl)
        if visible:
            frame_setting.pack(side="top")
        setting_label = Label(frame_setting, text=label_text, width=30, justify="right")
        setting_label.pack(side="left")
        setting_label2 = Label(frame_setting, text=description, wraplength=150, anchor="w",
                               justify="left", width=30)
        setting_label2.pack(side="right", padx=5, pady=5)
        setting_variable = StringVar()
        setting_entry = Entry(frame_setting, textvariable=setting_variable, width=10)
        try:
            setting_entry.insert(0, self.settings[name])
        except KeyError:
            setting_entry.insert(0, DEFAULT_SETTINGS[name])
            self.settings["name"] = DEFAULT_SETTINGS[name]

        setting_entry.pack(side="right")
        return setting_variable, setting_entry

    def add_check_setting(self, name: str, label_text: str, description: str, visible = True):
        frame_setting = Frame(self.tl)
        if visible:
            frame_setting.pack(side="top")
        setting_label = Label(frame_setting, text=label_text, width=30, justify="right")
        setting_label.pack(side="left")
        setting_label2 = Label(frame_setting, text=description, wraplength=150, anchor="w",
                               justify="left", width=30)
        setting_label2.pack(side="right", padx=5, pady=5)
        setting_variable = BooleanVar()
        setting_check = Checkbutton(frame_setting, width=5, variable=setting_variable)
        try:
            if self.settings[name] == "True":
                setting_check.select()
        except KeyError:
            if DEFAULT_SETTINGS[name] == "True":
                setting_check.select()
            self.settings[name] = DEFAULT_SETTINGS[name]
        setting_check.pack(side="right")
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
        self.width = CHARACTER_WIDTH * 60
        self.c = Canvas(parent, bg=color)
        self.c.config(width=self.width, height=100)
        self.buttons = []
        self.frames = []
        self.parent = parent
        self.del_icon = PhotoImage(file=INSTALL_DIRECTORY / "resources/garbage_bin_icon.png")

        self.c.config(scrollregion=(0, 0, self.width, 100))
        self.c.config(highlightthickness=0)

        self.scrollbar = Scrollbar(parent)
        self.scrollbar.config(command=self.c.yview)

        self.c.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.c.pack(side="left", fill="both")

    def delete_all_buttons(self):
        for frm in self.frames:
            frm.destroy()
        self.frames.clear()
        self.buttons.clear()

    def add_button(self, message: Message):
        frm = Frame(self.parent, width=self.width, height=20, bg="white")
        frm.config(relief="sunken")
        self.frames.append(frm)
        btn = Button(frm, text="\"" + message.title + f"\" from {message.get_date_sent_pretty()}",
                     width=45, command=lambda x=message: open_message(x))
        btn_del = Button(frm, width=CHARACTER_WIDTH*5, height=CHARACTER_WIDTH*3+5, image=self.del_icon, text="D", command=lambda x=message: delete_message(x))
        self.buttons.append(btn)
        btn.pack(side="left")
        btn_del.pack(side="right")
        space_for_button = 25
        self.c.create_window(5, (space_for_button * len(self.buttons)) - space_for_button, anchor="nw", window=frm)
        self.c.config(scrollregion=(0, 0, self.width, len(self.buttons) * space_for_button))


    def be_gone(self):
        self.delete_all_buttons()
        self.scrollbar.destroy()
        self.c.destroy()

try:
    os.mkdir(get_message_directory())
except FileExistsError:
    pass

(get_message_directory() / "notif.log").touch()
application_exists = True
settings_open = False

root = Tk()
root.title("PesterSelf")
root.config(bg="#cfcecc")
set_icon(root)

default_font = tkinter.font.nametofont("TkDefaultFont")
set_text_size(int(get_settings()["text_size"]))


RightFrame = Frame(root, bg="#cfcecc")
RightFrame.pack(side="right", padx=10)

WriteButton = Button(root, text="Write a message", command=open_write_dialogue)
WriteButton.pack(in_=RightFrame, side="top")
SettingsButton = Button(root, text="Settings", command=open_settings)
SettingsButton.pack(in_=RightFrame, side="top")
OpenFolderButton = Button(root, text="Open message folder", command=open_folder)
OpenFolderButton.pack(in_=RightFrame, side="top")
RefreshButton = Button(root, text="Refresh list", command=refresh_message_list)
RefreshButton.pack(in_=RightFrame, pady=20)


NotifFrame = Frame(RightFrame, bg="#cfcecc")
NotifFrame.pack(side="bottom")
NotifLabel = Label(RightFrame, text="Notification System\ncontrols", bg="#cfcecc")
NotifLabel.pack(side="top")
StopButton = Button(root, text="Stop", command=stop_notification_system)
StopButton.pack(in_=NotifFrame, padx=2, side="right")
StartButton = Button(root, text="Start", command=start_notification_system)
StartButton.pack(in_=NotifFrame, padx=2, side="left")

FRAME_WIDTH = CHARACTER_WIDTH * 60
FRAME_HEIGHT = 60

MessagesLabel = Label(root, text="Unread messages", bg="#cfcecc")
MessagesLabel.pack(side="top")
UnreadFrame = Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
UnreadFrame.pack(padx=5, pady=5, side="top", fill="none")
SCUnread = ScrolledCanvas(UnreadFrame, "white")

MessagesLabel = Label(root, text="Read messages", bg="#cfcecc")
MessagesLabel.pack(side="top")
ReadFrame = Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
ReadFrame.pack(padx=5, pady=5, side="top", fill="none")
SCRead = ScrolledCanvas(ReadFrame, "white")

if not Path(SETTINGS_FILE_PATH).exists():
    messagebox.showinfo("Thank you for downloading PesterSelf",
                        "You can set the notification system to turn on automatically on device startup in settings")

refresh_message_list()

root.protocol("WM_DELETE_WINDOW", root.destroy)
root.mainloop()
