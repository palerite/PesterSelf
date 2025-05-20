# PesterSelf
A handy tool for sending annoying/supportive messages to your future self.

This app is for you if the idea of texting yourself through time sounds as extremely cool to you as it does to me. What can't you do using this! Remind future you about some embarassing thing they did, or do it accidentally not realizing it is embarassing! Tell them about what is important to you now! Congratulate them on some occasion! Tell them they matter and that people care abouth them! What are they going to do, reply?

I used to do that through the calendar app on my phone but after "sending a message" this way into 2077 I realized that it's likely that I won't be using this calendar app so far away into the future. So I decided to make a tool for future-messaging using something more lasting - python and text files.


## Table of Contents
1. [Getting started](#getting-started)
	- [Windows](#windows)
	- [Linux](#linux)
2. [Usage](#usage)
3. [License](#license)
4. [Acknowledgments](#acknowledgments)

# Getting Started

## Windows

### Prerequisites
You just need python 3.9+ and its standard library for PesterSelf to run: [https://www.python.org/downloads/](https://www.python.org/downloads/)
### Installation
- Download the win32 release from [the github page](https://github.com/palerite/PesterSelf/) and unpack the archive in a folder of your liking. 
- Run `Create Shortcut to Interface.vbs` and use the created shortcut to access the app.
## Linux

### Prerequisites
- You need python 3.9+ and its standard library for PesterSelf to run: [https://docs.python.org/3/using/unix.html](https://docs.python.org/3/using/unix.html)
- Tkinter may not be included in your distribution, if that is the case, install it with `pip install tkinter`
### Installation
- Download the linux release from [the github page](https://github.com/palerite/PesterSelf/) and unpack the archive in a folder of your liking.
- Use `PesterSelfInterface.sh` to access the app

# Usage
PesterSelf consists of two parts - the **Interface**, used to interact with messages and set preferences, and the **Notification System**, used to deliver written messages. At no point should you interact with the **Notification System** directly, there are controls in the **Interface** to use it properly.
## Interface
In the interface, you will find messages that were already delivered, read and unread. 

You can open messages by clicking on them and delete by pressing the garbage bin icon. In *Settings* you'll find options for cutomizing the notification popup and an extremely important checkbox that adds the **Notification System** to the startup apps on your device. That way, you'll ensure that it is always running and messages reach you on time.

Also in the interface are controls for the **Notification System**. You can start or stop it from here, but I'd advise to keep it running at all times because you never know at what time past you wanted a message to reach you.
## Notification System
As said above, **Notification System** is launched by either the interface or the startup script on your device. Please don't stop it manually(bypassing the interface). You can start it manually but why would you do that.

**Notification System** sends notifications to you in the lower-right corner of the screen. It only checks for new messages every 30 minutes(customizable in settings) so messages may take a slightly longer time to reach you if set to be delivered too soon.

# License
Distributed under the GNU General Public License 3.0, see `LICENSE.txt` for details.

# Acknowledgments
Homestuck was an obvious inspiration. I used to send messages into the future long before I read it but the idea for this app definetely appeared because of this comic. I mean come on did you see `/resources/icon.png` yet, did you read the title
