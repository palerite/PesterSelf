from tkinter import *
from pesterself import *

testmsg = Message("TestTitle", datetime.datetime.now(), datetime.datetime.now(),
                  get_message_directory() / "null.txt", False)
notifications_on_screen = 0


def decrease_notification_amount(wdw):
    global notifications_on_screen
    notifications_on_screen -= 1
    if wdw is root:
        wdw.withdraw()
    else:
        wdw.destroy()


def inspection():
    global msgs_added
    global messages
    msgs_instantly = 0
    messages = get_message_list()
    for msg in messages:
        if not msg.read and msg not in msgs_added:
            root.after(
                max(datetime_to_msec(msg.date_received) - int(time.time() * 1000), 3000 + msgs_instantly * 1000),
                notification_popup, msg)
            msgs_added.append(msg)
            if datetime_to_msec(msg.date_received) - int(time.time() * 1000) < 3000:
                msgs_instantly += 1
            print("MESSAGE TO BE DELIVERED:", msg.title)
    root.after(int(INSPECTION_INTERVAL * 60 * 1000), inspection)


INSPECTION_INTERVAL = 0.2
PESTERSELF_DIRECTORY = "main.py"

root = Tk()
root.iconbitmap("icon.ico")
root.title("PesterSelf notification")
root_sw = root.winfo_screenwidth()
root_sh = root.winfo_screenheight()
root_rw = int(root_sw / 3)
root_rh = int(root_rw * 5 / 16)
root.geometry(f"{root_rw}x{root_rh}+{root_sw-root_rw-5}+{root_sh-root_rh-72}")
root.withdraw()
root.protocol('WM_DELETE_WINDOW', lambda arg=root: decrease_notification_amount(arg))


def lift_root():
    root.lift()
    print("LIFTING ROOT")
    root.after(50, lift_root)


def open_interface():
    open_file(PESTERSELF_DIRECTORY)


def notification_popup(msg: Message, window=root):
    global notifications_on_screen

    print(msg.title, "POPPING UP NOW")

    if notifications_on_screen:
        pass
    window = Toplevel(root)
    window.iconbitmap("icon.ico")
    window.title("PesterSelf notification")
    window.protocol('WM_DELETE_WINDOW', lambda arg=window: decrease_notification_amount(arg))
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    rw = int(sw / 3)
    rh = int(rw * 5 / 16)
    window.geometry(f"{rw}x{rh}+{sw-rw-5}+{sh-rh-72-notifications_on_screen*(rh+36)}")

    padding_px = 10

    frame_left = Frame(window)
    frame_left.pack(side=LEFT, padx=padding_px, pady=padding_px)
    frame_right = Frame(window)
    frame_right.pack(side=RIGHT, padx=padding_px, pady=padding_px)

    label = Label(frame_left,
                  text=f"\tYou have a new message from yourself!\n\n\t\"{msg.title}\" from {msg.get_date_sent_pretty()}")
    label.pack()

    open_button = Button(frame_right, text="Open the message", command=lambda x=msg, y=window: open_message(x, y))
    open_button.pack(pady=padding_px)
    client_button = Button(frame_right, text="Open PesterSelf", command=open_interface)
    client_button.pack(pady=padding_px)

    root.update()
    # lift_root()

    notifications_on_screen += 1


def open_message(msg: Message, wdw):
    decrease_notification_amount(wdw)
    msg.open()


messages = list()
msgs_startup = 0
msgs_added = list()
inspection()
# root.after(2000, notification_popup, testmsg)

root.mainloop()
