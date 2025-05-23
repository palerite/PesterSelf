from pathlib import Path
import os
import sys
import subprocess
import datetime
import time
import re
import configparser
from tkinter import *


INSTALL_DIRECTORY = Path(os.getcwd()).parent

SETTINGS_FILE_PATH = INSTALL_DIRECTORY / "settings.cfg"

DEFAULT_SETTINGS = {
    "launch_on_startup": "False",
    "notification_size": "450",
    "text_size": "10",
    "inspection_interval": "30",
    "startup_file": ".bash_profile" if (Path.home() / ".bash_profile").exists() else ".profile",
}

LINUX_STARTUP_LINES = [
    "start on runlevel [2345]\n",
    "stop on runlevel [!2345]\n",
    "\n",
    f"exec {INSTALL_DIRECTORY}NotificationSystem.py",
]

SHORTCUT_LINES = [
    "Set objShell = CreateObject(\"Wscript.Shell\")\n"
    f"objShell.CurrentDirectory = \"{INSTALL_DIRECTORY}\\scripts\"\n",
    "objShell.Run \"NotificationSystemRunner.bat\",0,True",
]

if sys.platform == "win32":
    NS_NAME = "NotificationSystem.vbs"
elif sys.platform == "darwin":
    NS_NAME = "PesterSelfNotificationSystem.py"
else:
    NS_NAME = "PesterSelfNotificationSystem.py"

BASHRC_LINES = [
    "\n# The following line launches PesterSelf Notification System. "
               "You can remove it by unchecking the 'run on startup' box in PesterSelf Settings\n",
   f"{INSTALL_DIRECTORY}/scripts/NotificationSystemRunner.sh\n",
]

NOTIFICATION_RUNNER_LINES = [
    "#!/bin/sh\n",
    f"cd {INSTALL_DIRECTORY}/scripts && python PesterSelfNotificationSystem.py &\n"
]


def get_message_directory():
    if sys.platform == "win32":
        home = Path.home()
        message_directory = home / "AppData" / "Roaming" / "PesterSelf/"
        # os.chmod(home / "AppData" / "Roaming" / "PesterSelf", 0o666)
    elif sys.platform == "darwin":
        home = Path.home()
        message_directory = home / "Application support" / "PesterSelf/"
    else:
        home = Path.home()
        message_directory = home / ".pesterself/"

    return message_directory



def get_startup_directory():
    return Path.home() / """AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"""


def check_pid(log_file):
    ln = log_file.readline()
    if not ln:
        return -1
    return int(ln)


def set_icon(window):
    if sys.platform == "win32":
        window.iconbitmap(INSTALL_DIRECTORY / "resources/icon.ico")
    else:
        window.iconphoto(False, PhotoImage(file=INSTALL_DIRECTORY / "resources/icon.png"))


def set_settings(settings):
    config = configparser.ConfigParser()
    config["settings"] = {}
    for setting in settings:
        config["settings"][setting] = settings[setting]
    with open(SETTINGS_FILE_PATH, "w") as out_f:
        config.write(out_f)


def get_settings():
    settings = {}
    config = configparser.ConfigParser()

    config.read(SETTINGS_FILE_PATH)

    if not config.sections():
        set_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    for setting in config["settings"]:
        settings[setting] = config["settings"][setting]

    for setting in DEFAULT_SETTINGS:
        if setting not in settings:
            settings[setting] = DEFAULT_SETTINGS[setting]

    return settings


def find_messages():
    message_directory = get_message_directory()
    try:
        os.mkdir(message_directory)
    except FileExistsError:
        pass
    return [message_directory / str(file) for file in os.listdir(message_directory)
            if os.path.isfile(os.path.join(message_directory, file))]


def get_message_list():
    messages = list()
    for message_path in find_messages():
        filename = str(message_path)[str(message_path).rfind("\\")+1:]
        if filename[-4:] != ".txt":
            continue
        with message_path.open() as f:

            f.readline()
            f.readline()
            test = f.readline()
            if not re.match(r".*\d{2}\.\d{2}\.\d{4}.*", test):
                continue
            test = f.readline()
            if not re.match(r".*\d{2}\.\d{2}\.\d{4}.*", test):
                continue

            f.seek(0)
            f.readline()
            message_read = "unread" not in f.readline().lower()
            text = f.readline()
            sent = to_datetime(text[text.find(": ") + 2:])
            text = f.readline()
            received = to_datetime(text[text.find(": ") + 2:])
            f.readline()
            message_title = f.readline()
            messages.append(Message(message_title, sent, received, message_path, message_read))
    messages = sorted(messages, key=lambda x: x.date_received)
    return messages


def is_date_valid(date: str) -> bool:
    try:
        to_datetime(date)
        return True
    except ValueError:
        return False


def to_datetime(date: str) -> datetime.datetime:
    date = date.strip()
    parts = [int(x) for x in date.split(" ")[0].split(".")]
    if len(date.split(" ")) > 1:
        parts += [int(x) for x in date.split(" ")[1].split(":")]
        return datetime.datetime(parts[2], parts[1], parts[0], hour=parts[3], minute=parts[4])
    return datetime.datetime(parts[2], parts[1], parts[0])


def datetime_to_msec(dt: datetime.datetime) -> int:
    return int(time.mktime(dt.timetuple())*1000 + dt.microsecond)


def open_file(filename):
    if sys.platform == 'win32':
        os.startfile(filename)
    elif sys.platform == 'darwin':
        subprocess.call(('open', filename))
    else:
        subprocess.call(('xdg-open', filename))


def execute_file(filename):
    if sys.platform == 'win32':
        os.startfile(filename)
    elif sys.platform == 'darwin':
        subprocess.call(('open', filename))
    else:
        os.system(f"python {filename} &")


class Message:
    def __init__(self, title: str, date_sent, date_received, file_path, read):
        self.title = title.strip("\n")
        self.date_sent = date_sent
        self.date_received = date_received
        self.file_path = file_path
        self.read = read

    def get_date_sent_pretty(self):
        return self.date_sent.strftime('%d.%m.%Y')

    def open(self):
        tmp_dir = get_message_directory() / "tmp.txt"
        try:
            os.remove(tmp_dir)
        except FileNotFoundError:
            pass
        tmp_dir.touch()
        with self.file_path.open("r") as in_f, tmp_dir.open("w") as out_f:
            lines = in_f.readlines()
            lines[1] = "State: read\n"
            out_f.writelines(lines)
        try:
            os.remove(self.file_path)
            os.rename(tmp_dir, self.file_path)
        except PermissionError:
            pass

        open_file(self.file_path)

    def info(self):
        return {
            "Title": self.title,
            "Date sent": self.date_sent,
            "Date received": self.date_received,
            "File path": self.file_path,
        }

    def delete(self) -> int:
        try:
            os.remove(self.file_path)
            return 0
        except FileNotFoundError:
            return 1

    def __eq__(self, other):
        return self.file_path == other.file_path
