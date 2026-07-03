Attribute VB_Name = "modAnalysisScoring"
Option Explicit

Public Sub RebuildAnalysisResults()
    Dim src As ListObject: Set src = ThisWorkbook.Worksheets("ANALYZY").ListObjects("tblAnalyzy")
    Dim dst As ListObject: Set dst = ThisWorkbook.Worksheets("VYSLEDKY_ANALYZ").ListObjects("tblVysledkyAnalyz")
    ClearBody dst
    If src.DataBodyRange Is Nothing Then Exit Sub
    Dim r As ListRow, out As ListRow, startPrice As Double, horizonDays As Long, verdict As String, sym As String, t As Date
    For Each r In src.ListRows
        If Len(Trim$(CStr(r.Range.Cells(1, 1).Value))) > 0 Then
            Set out = dst.ListRows.Add
            sym = Trim$(CStr(r.Range.Cells(1, 3).Value))
            verdict = UCase$(Trim$(CStr(r.Range.Cells(1, 4).Value)))
            t = r.Range.Cells(1, 2).Value
            horizonDays = CLng(IIf(ToDoubleOrZero(r.Range.Cells(1, 5).Value) > 0, ToDoubleOrZero(r.Range.Cells(1, 5).Value), ToDoubleOrZero(GetConfigValue("DefaultHorizonDays", "14"))))
            startPrice = ToDoubleOrZero(r.Range.Cells(1, 6).Value)
            If startPrice <= 0 Then startPrice = FirstPriceAtOrAfter(sym, t)
            WriteAnalysisRow out, r.Range.Cells(1, 1).Value, t, sym, verdict, horizonDays, startPrice
        End If
    Next r
End Sub

Private Sub WriteAnalysisRow(ByVal out As ListRow, ByVal id As Variant, ByVal t As Date, ByVal sym As String, ByVal verdict As String, ByVal horizonDays As Long, ByVal startPrice As Double)
    Dim pCur As Double, p1 As Double, p5 As Double, p14 As Double, ph As Double, hr As Double, rawHr As Double
    pCur = LatestPrice(sym): p1 = FirstPriceAtOrAfter(sym, t + 1): p5 = FirstPriceAtOrAfter(sym, t + 5): p14 = FirstPriceAtOrAfter(sym, t + 14): ph = FirstPriceAtOrAfter(sym, t + horizonDays)
    out.Range.Cells(1, 1).Resize(1, 6).Value = Array(id, t, sym, verdict, horizonDays, startPrice)
    out.Range.Cells(1, 7).Value = pCur: out.Range.Cells(1, 8).Value = ReturnPct(verdict, startPrice, pCur)
    out.Range.Cells(1, 9).Value = p1: out.Range.Cells(1, 10).Value = ReturnPct(verdict, startPrice, p1)
    out.Range.Cells(1, 11).Value = p5: out.Range.Cells(1, 12).Value = ReturnPct(verdict, startPrice, p5)
    out.Range.Cells(1, 13).Value = p14: out.Range.Cells(1, 14).Value = ReturnPct(verdict, startPrice, p14)
    out.Range.Cells(1, 15).Value = ph: hr = ReturnPct(verdict, startPrice, ph): rawHr = RawReturnPct(startPrice, ph)
    out.Range.Cells(1, 16).Value = hr
    out.Range.Cells(1, 17).Value = MaxRawReturn(sym, t, t + horizonDays, startPrice, True)
    out.Range.Cells(1, 18).Value = MaxRawReturn(sym, t, t + horizonDays, startPrice, False)
    out.Range.Cells(1, 19).Value = ScoreResult(verdict, hr, rawHr)
    out.Range.Cells(1, 20).Value = "Vyhodnoceno proti první dostupné ceně v horizontu nebo později."
End Sub

Public Function FirstPriceAtOrAfter(ByVal sym As String, ByVal t As Date) As Double
    Dim lo As ListObject: Set lo = ThisWorkbook.Worksheets("MT5_CENY").ListObjects("tblMT5Ceny")
    If lo.DataBodyRange Is Nothing Then Exit Function
    Dim r As ListRow, bestT As Date, found As Boolean
    For Each r In lo.ListRows
        If StrComp(CStr(r.Range.Cells(1, 2).Value), sym, vbTextCompare) = 0 And IsDate(r.Range.Cells(1, 1).Value) Then
            If r.Range.Cells(1, 1).Value >= t And ToDoubleOrZero(r.Range.Cells(1, 9).Value) > 0 Then
                If Not found Or r.Range.Cells(1, 1).Value < bestT Then bestT = r.Range.Cells(1, 1).Value: FirstPriceAtOrAfter = r.Range.Cells(1, 9).Value: found = True
            End If
        End If
    Next r
End Function

Public Function LatestPrice(ByVal sym As String) As Double
    Dim lo As ListObject: Set lo = ThisWorkbook.Worksheets("MT5_CENY").ListObjects("tblMT5Ceny")
    If lo.DataBodyRange Is Nothing Then Exit Function
    Dim r As ListRow, bestT As Date
    For Each r In lo.ListRows
        If StrComp(CStr(r.Range.Cells(1, 2).Value), sym, vbTextCompare) = 0 And IsDate(r.Range.Cells(1, 1).Value) And ToDoubleOrZero(r.Range.Cells(1, 9).Value) > 0 Then
            If r.Range.Cells(1, 1).Value > bestT Then bestT = r.Range.Cells(1, 1).Value: LatestPrice = r.Range.Cells(1, 9).Value
        End If
    Next r
End Function

Private Function RawReturnPct(ByVal startPrice As Double, ByVal priceValue As Double) As Double
    If startPrice > 0 And priceValue > 0 Then RawReturnPct = (priceValue / startPrice - 1) * 100
End Function

Private Function ReturnPct(ByVal verdict As String, ByVal startPrice As Double, ByVal priceValue As Double) As Double
    If startPrice <= 0 Or priceValue <= 0 Then Exit Function
    If verdict = "SHORT" Then ReturnPct = (startPrice / priceValue - 1) * 100 Else ReturnPct = RawReturnPct(startPrice, priceValue)
End Function

Private Function ScoreResult(ByVal verdict As String, ByVal ret As Double, ByVal rawRet As Double) As String
    If verdict = "WATCH" Then ScoreResult = "WATCH ONLY": Exit Function
    If verdict = "BUY" Then ScoreResult = ThresholdScore(ret, ToDoubleOrZero(GetConfigValue("BuySuccessPct", "3")), ToDoubleOrZero(GetConfigValue("BuyFailPct", "-3"))): Exit Function
    If verdict = "SHORT" Then ScoreResult = ThresholdScore(ret, ToDoubleOrZero(GetConfigValue("ShortSuccessPct", "3")), ToDoubleOrZero(GetConfigValue("ShortFailPct", "-3"))): Exit Function
    If verdict = "AVOID" Then
        If rawRet >= ToDoubleOrZero(GetConfigValue("AvoidBadPct", "5")) Then
            ScoreResult = "MISS"
        ElseIf rawRet <= 0 Then
            ScoreResult = "HIT"
        Else
            ScoreResult = "NEUTRAL"
        End If
    End If
End Function

Private Function ThresholdScore(ByVal ret As Double, ByVal ok As Double, ByVal bad As Double) As String
    If ret >= ok Then
        ThresholdScore = "HIT"
    ElseIf ret <= bad Then
        ThresholdScore = "MISS"
    Else
        ThresholdScore = "NEUTRAL"
    End If
End Function

Private Function MaxRawReturn(ByVal sym As String, ByVal t1 As Date, ByVal t2 As Date, ByVal startPrice As Double, ByVal wantMax As Boolean) As Double
    Dim lo As ListObject: Set lo = ThisWorkbook.Worksheets("MT5_CENY").ListObjects("tblMT5Ceny")
    Dim r As ListRow, v As Double, found As Boolean
    If startPrice <= 0 Or lo.DataBodyRange Is Nothing Then Exit Function
    For Each r In lo.ListRows
        If StrComp(CStr(r.Range.Cells(1, 2).Value), sym, vbTextCompare) = 0 And r.Range.Cells(1, 1).Value >= t1 And r.Range.Cells(1, 1).Value <= t2 Then
            v = RawReturnPct(startPrice, ToDoubleOrZero(r.Range.Cells(1, 9).Value))
            If Not found Or (wantMax And v > MaxRawReturn) Or ((Not wantMax) And v < MaxRawReturn) Then MaxRawReturn = v: found = True
        End If
    Next r
End Function

Private Sub ClearBody(ByVal lo As ListObject)
    If Not lo.DataBodyRange Is Nothing Then lo.DataBodyRange.Delete
End Sub
