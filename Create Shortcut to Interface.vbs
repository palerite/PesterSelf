
' This file needs to be exactly in the install directory to function

Set Shell = CreateObject("WScript.Shell")
Set link = Shell.CreateShortcut("PesterSelf Interface.lnk")
strFolder = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))

link.Arguments = "1 2 3"
link.Description = "PesterSelf Interface"
link.IconLocation = strFolder & "\resources\icon.ico"
link.TargetPath = strFolder & "\scripts\PesterSelfInterface.vbs"
link.WindowStyle = 3
link.WorkingDirectory = strFolder + "\scripts"
link.Save