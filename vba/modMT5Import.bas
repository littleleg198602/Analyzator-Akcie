Attribute VB_Name = "modMT5Import"
Option Explicit

Public Sub RefreshAllMT5Data()
    On Error GoTo ErrHandler
    Application.ScreenUpdating = False
    Application.EnableEvents = False

    ImportSemicolonCsvToTable "MT5_CENY", "tblMT5Ceny", GetConfigValue("AnalysisPricesFile")
    ImportSemicolonCsvToTable "MT5_PORTFOLIO", "tblMT5Portfolio", GetConfigValue("PortfolioPositionsFile")
    FillPriceUsed
    RebuildAnalysisResults
    RebuildPortfolioLatest
    UpdateDashboard

    ThisWorkbook.RefreshAll
    Application.CalculateFull
    MsgBox "Import MT5 dat a přepočet dashboardu byl dokončen.", vbInformation, "MT5 dashboard"
CleanExit:
    Application.EnableEvents = True
    Application.ScreenUpdating = True
    Exit Sub
ErrHandler:
    MsgBox "Chyba při importu MT5 dat: " & Err.Description, vbExclamation, "MT5 dashboard"
    Resume CleanExit
End Sub

Public Function GetConfigValue(ByVal key As String, Optional ByVal defaultValue As String = "") As String
    Dim lo As ListObject, r As ListRow
    Set lo = ThisWorkbook.Worksheets("CONFIG").ListObjects("tblConfig")
    For Each r In lo.ListRows
        If StrComp(CStr(r.Range.Cells(1, 1).Value), key, vbTextCompare) = 0 Then
            GetConfigValue = CStr(r.Range.Cells(1, 2).Value)
            Exit Function
        End If
    Next r
    GetConfigValue = defaultValue
End Function

Public Function CommonFolderPath() As String
    Dim p As String
    p = GetConfigValue("MT5CommonFolderPath", "%APPDATA%\MetaQuotes\Terminal\Common\Files\")
    p = Replace(p, "%APPDATA%", Environ$("APPDATA"), , , vbTextCompare)
    If Right$(p, 1) <> "\" Then p = p & "\"
    CommonFolderPath = p
End Function

Private Sub ImportSemicolonCsvToTable(ByVal sheetName As String, ByVal tableName As String, ByVal fileName As String)
    Dim path As String: path = CommonFolderPath() & fileName
    Dim ws As Worksheet: Set ws = ThisWorkbook.Worksheets(sheetName)
    Dim lo As ListObject: Set lo = ws.ListObjects(tableName)
    If Dir$(path) = "" Then
        ClearTableBody lo
        MsgBox "Soubor nebyl nalezen: " & path, vbExclamation, "MT5 import"
        Exit Sub
    End If

    Dim f As Integer, line As String, fields() As String, rowIndex As Long, colIndex As Long
    ClearTableBody lo
    f = FreeFile
    Open path For Input As #f
    If Not EOF(f) Then Line Input #f, line ' header
    rowIndex = 0
    Do While Not EOF(f)
        Line Input #f, line
        If Len(Trim$(line)) > 0 Then
            fields = Split(line, ";")
            rowIndex = rowIndex + 1
            lo.ListRows.Add
            For colIndex = 1 To lo.ListColumns.Count
                If colIndex - 1 <= UBound(fields) Then
                    lo.DataBodyRange.Cells(rowIndex, colIndex).Value = CoerceCsvValue(fields(colIndex - 1), lo.HeaderRowRange.Cells(1, colIndex).Value)
                End If
            Next colIndex
        End If
    Loop
    Close #f
End Sub

Private Sub ClearTableBody(ByVal lo As ListObject)
    If Not lo.DataBodyRange Is Nothing Then lo.DataBodyRange.Delete
End Sub

Private Function CoerceCsvValue(ByVal textValue As String, ByVal headerName As String) As Variant
    Dim s As String: s = Trim$(textValue)
    If Len(s) = 0 Then CoerceCsvValue = Empty: Exit Function
    If InStr(1, headerName, "Time", vbTextCompare) > 0 Then
        CoerceCsvValue = ParseDateTimeFlexible(s)
    ElseIf IsNumericFlexible(s) Then
        CoerceCsvValue = ToDoubleFlexible(s)
    Else
        CoerceCsvValue = s
    End If
End Function

Public Function IsNumericFlexible(ByVal s As String) As Boolean
    On Error GoTo Bad
    Dim d As Double: d = ToDoubleFlexible(s)
    IsNumericFlexible = True
    Exit Function
Bad:
    IsNumericFlexible = False
End Function

Public Function ToDoubleFlexible(ByVal s As String) As Double
    Dim t As String: t = Trim$(s)
    If InStr(t, ",") > 0 And InStr(t, ".") > 0 Then
        t = Replace(t, " ", "")
        If InStrRev(t, ",") > InStrRev(t, ".") Then
            t = Replace(t, ".", "")
            t = Replace(t, ",", Application.DecimalSeparator)
        Else
            t = Replace(t, ",", "")
            t = Replace(t, ".", Application.DecimalSeparator)
        End If
    Else
        t = Replace(t, ",", Application.DecimalSeparator)
        t = Replace(t, ".", Application.DecimalSeparator)
    End If
    ToDoubleFlexible = CDbl(t)
End Function

Public Function ParseDateTimeFlexible(ByVal s As String) As Variant
    On Error GoTo Bad
    ParseDateTimeFlexible = CDate(Replace(s, "T", " "))
    Exit Function
Bad:
    ParseDateTimeFlexible = s
End Function

Public Function ToDoubleOrZero(ByVal value As Variant) As Double
    On Error GoTo Bad
    If Len(Trim$(CStr(value))) = 0 Then Exit Function
    ToDoubleOrZero = ToDoubleFlexible(CStr(value))
    Exit Function
Bad:
    ToDoubleOrZero = 0
End Function

Public Sub FillPriceUsed()
    Dim lo As ListObject: Set lo = ThisWorkbook.Worksheets("MT5_CENY").ListObjects("tblMT5Ceny")
    If lo.DataBodyRange Is Nothing Then Exit Sub
    Dim r As ListRow, bid As Double, ask As Double, last As Double
    For Each r In lo.ListRows
        bid = ToDoubleOrZero(r.Range.Cells(1, 3).Value)
        ask = ToDoubleOrZero(r.Range.Cells(1, 4).Value)
        last = ToDoubleOrZero(r.Range.Cells(1, 5).Value)
        If last > 0 Then
            r.Range.Cells(1, 9).Value = last
        ElseIf bid > 0 And ask > 0 Then
            r.Range.Cells(1, 9).Value = (bid + ask) / 2
        ElseIf bid > 0 Then
            r.Range.Cells(1, 9).Value = bid
        Else
            r.Range.Cells(1, 9).ClearContents
        End If
    Next r
End Sub
