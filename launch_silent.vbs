' Nis aplikacionin STRICT LOUNGE & BAR ne menyre te qete (pa dritare te zeze terminali)
Set WshShell = CreateObject("WScript.Shell")
Dim fso, scriptDir
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

WshShell.Run "python -c ""from desktop.launcher import launch_desktop; launch_desktop()""", 0, False
