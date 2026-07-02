Option Explicit

Private Sub Workbook_Open()
    If UCase$(Trim$(GetConfigValue("AutoRefreshOnOpen", "FALSE"))) = "TRUE" Then
        RefreshAllMT5Data
    End If
End Sub
