from pesterself import *
import signal
import tkinter.font

testmsg = Message("TestTitle", datetime.datetime.now(), datetime.datetime.now(),
                  get_message_directory() / "null.txt", False)
notifications_on_screen = 0

try:
    os.mkdir(get_message_directory())
except FileExistsError:
    pass

(get_message_directory() / "notif.log").touch()

with (get_message_directory() / "notif.log").open() as log:
    pid = check_pid(log)
    if pid > 0:
        try:
            os.kill(pid, signal.SIGTERM)
        except PermissionError:
            pass
        except OSError:
            pass

with (get_message_directory() / "notif.log").open("w") as log:
    log.write(str(os.getpid()))


def decrease_notification_amount(window):
    global notifications_on_screen
    notifications_on_screen -= 1
    if window is root:
        window.withdraw()
    else:
        window.destroy()


def inspection():
    global msgs_added
    msgs_instantly = 0
    messages = get_message_list()
    for msg in messages:
        if not msg.read and msg not in msgs_added:
            time_amount = max(datetime_to_msec(msg.date_received) - int(time.time() * 1000),
                              5000 + msgs_instantly * 1000)
            if time_amount > INSPECTION_INTERVAL*60*1000:
                continue
            root.after(
                int(time_amount),
                notification_popup, msg)
            msgs_added.append(msg)
            if datetime_to_msec(msg.date_received) - int(time.time() * 1000.0) < 5000:
                msgs_instantly += 1
    root.after(int(INSPECTION_INTERVAL * 60 * 1000), inspection)


def open_interface():
    open_file(PESTERSELF_DIRECTORY)


def notification_popup(msg: Message):
    global notifications_on_screen

    if notifications_on_screen:
        pass
    window = Toplevel(root)
    set_icon(window)
    window.title("PesterSelf notification")
    window.protocol('WM_DELETE_WINDOW', lambda arg=window: decrease_notification_amount(arg))
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    rw = int(settings["notification_size"])
    rh = int(rw * 5 / 16)
    window.geometry(f"{rw}x{rh}+{sw-rw-5}+{sh-rh-72-notifications_on_screen*(rh+36)}")

    padding_px = 5

    frame_right = Frame(window, width=CHARACTER_WIDTH*15)
    frame_right.pack(side="right", padx=padding_px, pady=rh//5, fill="both", expand=True)
    frame_left = Frame(window, width=CHARACTER_WIDTH*40)
    frame_left.pack(side="right", padx=padding_px, pady=rh//4, fill="both", expand=True)

    label = Label(frame_left,
                  text=f"You have a new message from yourself!\n\n\"{msg.title}\" from {msg.get_date_sent_pretty()}")
    label.pack(anchor="center")

    open_button = Button(frame_right, text="Open the message", command=lambda x=msg, y=window: open_message(x, y))
    open_button.pack(pady=padding_px)
    client_button = Button(frame_right, text="Open PesterSelf", command=open_interface)
    client_button.pack(pady=padding_px)

    root.update()

    notifications_on_screen += 1


def open_message(msg: Message, window):
    decrease_notification_amount(window)
    msg.open()


# def exit_handling(*args):
#     with (get_message_directory() / "notif.log").open("w") as log_file:
#         log_file.write("0")




settings = get_settings()

INSPECTION_INTERVAL = int(settings["inspection_interval"])
PESTERSELF_DIRECTORY = INSTALL_DIRECTORY / "scripts/PesterSelfInterface.vbs"

root = Tk()
set_icon(root)
root.title("PesterSelf Notification System")

default_font = tkinter.font.nametofont("TkDefaultFont")
s = 20
default_font.configure(size=s)
while default_font.measure("n") * 61 > int(settings["notification_size"]):
    s -= 1
    default_font.configure(size=s)
CHARACTER_WIDTH = default_font.measure("n")

calmingLabel = Label(root, text="PesterSelf Notification System launched.\nClosing this info window in 3")
calmingLabel.pack()


for i in range(2000, -1000, -1000):
    root.after(3000 - i, lambda x=f"PesterSelf Notification System launched.\n"
                                    f"Closing this info window in {i//1000}": calmingLabel.config(text=x))
root.after(3000, root.withdraw)
root.protocol('WM_DELETE_WINDOW', root.withdraw)

msgs_added = list()
inspection()

root.mainloop()
