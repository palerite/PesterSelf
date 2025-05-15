Set Shell = CreateObject("WScript.Shell")
Set link = Shell.CreateShortcut("PesterSelf Interface.lnk")
strFolder = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))

link.Arguments = "1 2 3"
link.Description = "PesterSelf Interface"
link.IconLocation = strFolder & "\icon.ico"
link.TargetPath = strFolder & "\PesterSelf Interface.vbs"
link.WindowStyle = 3
link.WorkingDirectory = strFolder
link.Save