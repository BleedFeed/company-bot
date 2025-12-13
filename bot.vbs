' thx chatgippity

Option Explicit

Dim shell, fso
Dim expr
Dim baseDir, logsDir
Dim logPath, timestamp
Dim cmd

' Get argument
expr = WScript.Arguments(0)

' Objects
Set shell = CreateObject("WScript.Shell")
Set fso   = CreateObject("Scripting.FileSystemObject")

' Directory where this VBS file lives
baseDir = fso.GetParentFolderName(WScript.ScriptFullName)
logsDir = baseDir & "\logs"

' Create logs directory if missing
If Not fso.FolderExists(logsDir) Then
    fso.CreateFolder logsDir
End If

' Timestamp
timestamp = _
    Year(Now) & "-" & _
    Right("0" & Month(Now), 2) & "-" & _
    Right("0" & Day(Now), 2) & "_" & _
    Right("0" & Hour(Now), 2) & "-" & _
    Right("0" & Minute(Now), 2) & "-" & _
    Right("0" & Second(Now), 2)

' Log file path
logPath = logsDir & "\log_" & timestamp & ".txt"

' Command
cmd = "cmd /c " & _
      "chcp 65001>nul && " & _
      """" & baseDir & "\venv\Scripts\python.exe"" -X utf8 " & _
      """" & baseDir & "\bot.py"" """ & expr & _
      """ > """ & logPath & """ 2>&1"

' Run hidden, wait for completion
shell.Run cmd, 0, True
