Attribute VB_Name = "modPortfolioDashboard"
Option Explicit

Public Sub RebuildPortfolioLatest()
    Dim src As ListObject: Set src = ThisWorkbook.Worksheets("MT5_PORTFOLIO").ListObjects("tblMT5Portfolio")
    Dim dst As ListObject: Set dst = ThisWorkbook.Worksheets("PORTFOLIO").ListObjects("tblPortfolioLatest")
    If Not dst.DataBodyRange Is Nothing Then dst.DataBodyRange.Delete
    If src.DataBodyRange Is Nothing Then Exit Sub
    Dim dict As Object: Set dict = CreateObject("Scripting.Dictionary")
    Dim r As ListRow, ticket As String, snap As Date
    For Each r In src.ListRows
        ticket = CStr(r.Range.Cells(1, 5).Value)
        If Len(ticket) > 0 And IsDate(r.Range.Cells(1, 1).Value) Then
            snap = r.Range.Cells(1, 1).Value
            If Not dict.Exists(ticket) Then
                dict.Add ticket, r.Index
            ElseIf snap > src.ListRows(dict(ticket)).Range.Cells(1, 1).Value Then
                dict(ticket) = r.Index
            End If
        End If
    Next r
    Dim k As Variant, out As ListRow, rr As Range
    For Each k In dict.Keys
        Set rr = src.ListRows(dict(k)).Range
        Set out = dst.ListRows.Add
        out.Range.Cells(1, 1).Resize(1, 12).Value = Array(rr.Cells(1, 1).Value, rr.Cells(1, 4).Value, rr.Cells(1, 5).Value, rr.Cells(1, 6).Value, rr.Cells(1, 7).Value, rr.Cells(1, 8).Value, rr.Cells(1, 9).Value, rr.Cells(1, 10).Value, rr.Cells(1, 11).Value, rr.Cells(1, 12).Value, rr.Cells(1, 13).Value, rr.Cells(1, 15).Value)
    Next k
End Sub

Public Sub UpdateDashboard()
    Dim ws As Worksheet: Set ws = ThisWorkbook.Worksheets("DASHBOARD")
    ws.Range("B3:B15").ClearContents
    Dim res As ListObject: Set res = ThisWorkbook.Worksheets("VYSLEDKY_ANALYZ").ListObjects("tblVysledkyAnalyz")
    Dim port As ListObject: Set port = ThisWorkbook.Worksheets("PORTFOLIO").ListObjects("tblPortfolioLatest")
    ws.Range("B3").Value = CountRows(ThisWorkbook.Worksheets("ANALYZY").ListObjects("tblAnalyzy"))
    ws.Range("B4").Value = CountRows(res)
    ws.Range("B5").Value = HitRate(res, "BUY")
    ws.Range("B6").Value = HitRate(res, "SHORT")
    ws.Range("B7").Value = HitRate(res, "AVOID")
    ws.Range("B8").Value = CountResult(res, "HIT")
    ws.Range("B9").Value = CountResult(res, "MISS")
    ws.Range("B10").Value = CountResult(res, "NEUTRAL")
    ws.Range("B11").Value = CountResult(res, "WATCH ONLY")
    ws.Range("B12").Value = SumColumn(port, 10)
    ws.Range("B13").Value = CountRows(port)
    ws.Range("B14").Value = ExtremePosition(port, 9, True)
    ws.Range("B15").Value = ExtremePosition(port, 9, False)
End Sub

Private Function CountRows(ByVal lo As ListObject) As Long
    If lo.DataBodyRange Is Nothing Then CountRows = 0 Else CountRows = lo.ListRows.Count
End Function

Private Function CountResult(ByVal lo As ListObject, ByVal resultName As String) As Long
    Dim r As ListRow
    If lo.DataBodyRange Is Nothing Then Exit Function
    For Each r In lo.ListRows
        If UCase$(CStr(r.Range.Cells(1, 19).Value)) = UCase$(resultName) Then CountResult = CountResult + 1
    Next r
End Function

Private Function HitRate(ByVal lo As ListObject, ByVal verdict As String) As Double
    Dim r As ListRow, hit As Long, total As Long, resultName As String
    If lo.DataBodyRange Is Nothing Then Exit Function
    For Each r In lo.ListRows
        If UCase$(CStr(r.Range.Cells(1, 4).Value)) = verdict Then
            resultName = UCase$(CStr(r.Range.Cells(1, 19).Value))
            If resultName = "HIT" Or resultName = "MISS" Then total = total + 1
            If resultName = "HIT" Then hit = hit + 1
        End If
    Next r
    If total > 0 Then HitRate = hit / total
End Function

Private Function SumColumn(ByVal lo As ListObject, ByVal col As Long) As Double
    Dim r As ListRow
    If lo.DataBodyRange Is Nothing Then Exit Function
    For Each r In lo.ListRows: SumColumn = SumColumn + ToDoubleOrZero(r.Range.Cells(1, col).Value): Next r
End Function

Private Function ExtremePosition(ByVal lo As ListObject, ByVal col As Long, ByVal wantMax As Boolean) As String
    Dim r As ListRow, v As Double, best As Double, found As Boolean
    If lo.DataBodyRange Is Nothing Then Exit Function
    For Each r In lo.ListRows
        v = ToDoubleOrZero(r.Range.Cells(1, col).Value)
        If Not found Or (wantMax And v > best) Or ((Not wantMax) And v < best) Then
            best = v: found = True: ExtremePosition = CStr(r.Range.Cells(1, 2).Value) & " / " & CStr(r.Range.Cells(1, 3).Value) & " (" & Format(v, "0.00") & " %)"
        End If
    Next r
End Function
