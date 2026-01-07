Option Explicit

Dim shell, fso
Dim expr
Dim baseDir, logsDir
Dim logPath, timestamp
Dim botPath, pythonExe, cmd
Dim envFile, envLines, line, parts

' -------------------------
' Get argument
' -------------------------
If WScript.Arguments.Count > 0 Then
    expr = WScript.Arguments(0)
Else
    expr = ""
End If

' -------------------------
' Create objects
' -------------------------
Set shell = CreateObject("WScript.Shell")
Set fso   = CreateObject("Scripting.FileSystemObject")

' -------------------------
' Base directories
' -------------------------
baseDir = fso.GetParentFolderName(WScript.ScriptFullName)
logsDir = baseDir & "\logs"
envFile = baseDir & "\.env"

' -------------------------
' Create logs directory if missing
' -------------------------
If Not fso.FolderExists(logsDir) Then
    fso.CreateFolder logsDir
End If

' -------------------------
' Read .env file
' -------------------------
pythonExe = ""

If fso.FileExists(envFile) Then
    Set envLines = fso.OpenTextFile(envFile, 1)

    Do Until envLines.AtEndOfStream
        line = Trim(envLines.ReadLine)

        If InStr(line, "=") > 0 Then
            parts = Split(line, "=")
            If UCase(Trim(parts(0))) = "PYTHON_EXE" Then
                pythonExe = Trim(parts(1))
            End If
        End If
    Loop

    envLines.Close
End If

If pythonExe = "" Then
    WScript.Echo "ERROR: PYTHON_EXE not found in .env"
    WScript.Quit 1
End If

' -------------------------
' Bot path (bot.py)
' -------------------------
botPath = """" & baseDir & "\bot.py"""  ' quote path

' -------------------------
' Timestamp
' -------------------------
timestamp = Year(Now) & "-" & _
            Right("0" & Month(Now), 2) & "-" & _
            Right("0" & Day(Now), 2) & "_" & _
            Right("0" & Hour(Now), 2) & "-" & _
            Right("0" & Minute(Now), 2) & "-" & _
            Right("0" & Second(Now), 2)

' Log file path
logPath = logsDir & "\log_" & timestamp & ".txt"

' -------------------------
' Build command
' -------------------------
cmd = "cmd /c chcp 65001>nul && """ & pythonExe & """ -X utf8 " & botPath & _
      " """ & expr & """ > """ & logPath & """ 2>&1"

' -------------------------
' Run hidden, wait for completion
' -------------------------
shell.Run cmd, 0, True
