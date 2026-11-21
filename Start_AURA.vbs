Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
folder = fso.GetParentFolderName(WScript.ScriptFullName)
exe = folder & "\dist\AURA\AURA.exe"
If fso.FileExists(exe) Then
    shell.Run """" & exe & """", 0, False
Else
    shell.Run "pythonw """ & folder & "\aura_app.py""", 0, False
End If
