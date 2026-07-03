Attribute VB_Name = "modTrackedSymbols"
Option Explicit

Public Sub UpdateTrackedSymbols()
    On Error GoTo ErrHandler
    Dim lo As ListObject: Set lo = ThisWorkbook.Worksheets("ANALYZY").ListObjects("tblAnalyzy")
    Dim dict As Object: Set dict = CreateObject("Scripting.Dictionary")
    dict.CompareMode = vbTextCompare
    Dim r As ListRow, sym As String, st As String
    If Not lo.DataBodyRange Is Nothing Then
        For Each r In lo.ListRows
            sym = Trim$(CStr(r.Range.Cells(1, 3).Value))
            st = UCase$(Trim$(CStr(r.Range.Cells(1, 11).Value)))
            If Len(sym) > 0 And st = "OPEN" Then If Not dict.Exists(sym) Then dict.Add sym, sym
        Next r
    End If
    Dim path As String: path = CommonFolderPath() & GetConfigValue("TrackedSymbolsFile", "TrackedSymbols.csv")
    Dim f As Integer: f = FreeFile
    Open path For Output As #f
    Print #f, "Symbol"
    Dim k As Variant
    For Each k In dict.Keys: Print #f, CStr(k): Next k
    Close #f
    MsgBox "Do TrackedSymbols.csv bylo zapsáno symbolů: " & dict.Count, vbInformation, "MT5 dashboard"
    Exit Sub
ErrHandler:
    MsgBox "Chyba při zápisu TrackedSymbols.csv: " & Err.Description, vbExclamation, "MT5 dashboard"
End Sub
