Option Explicit

Dim shell, fso
Dim expr
Dim baseDir, logsDir
Dim logPath, timestamp
Dim pythonExe, botPath, cmd
Dim envFile, envLines, line, parts, i

' -------------------------
' Get argument
' -------------------------
expr = WScript.Arguments(0)

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
' Default Python
' -------------------------
pythonExe = "python"  ' fallback if .env not found

' -------------------------
' Read .env file if it exists
' -------------------------
If fso.FileExists(envFile) Then
    envLines = Split(fso.OpenTextFile(envFile, 1).ReadAll, vbCrLf)
    For i = 0 To UBound(envLines)
        line = Trim(envLines(i))
        If Left(line, 11) = "PYTHON_PATH" Then
            parts = Split(line, "=")
            If UBound(parts) = 1 Then
                pythonExe = Trim(parts(1))
                
                ' Handle relative path
                If Left(pythonExe, 2) = ".\" Then
                    pythonExe = fso.BuildPath(baseDir, Mid(pythonExe, 3))
                End If
            End If
            Exit For
        End If
    Next
End If

' -------------------------
' Bot path
' -------------------------
botPath = """" & baseDir & "\bot.py"""  ' quote path in case of spaces

' -------------------------
' Build command
' -------------------------
cmd = "cmd /c " & _
      "chcp 65001>nul && " & _
      """" & pythonExe & """ -X utf8 " & botPath & " """ & expr & """ > """ & logPath & """ 2>&1"

' -------------------------
' Run hidden, wait for completion
' -------------------------
shell.Run cmd, 0, True
