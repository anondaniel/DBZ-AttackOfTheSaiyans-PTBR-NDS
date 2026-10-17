# Verifica ortografia (pt-BR) de cada palavra unica usando o Word via COM.
# Nao salva nenhum documento.
param([string]$Entrada, [string]$Saida)
$ws = Get-Content -Encoding UTF8 $Entrada
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$doc = $w.Documents.Add()
$teste = @()
foreach ($t in @("você", "voce", "não", "nao")) {
    $teste += "$t=" + $w.CheckSpelling($t, $null, $false, "Português (Brasil)")
}
"teste: $($teste -join ' ')" | Out-File -Encoding utf8 $Saida
$ruins = New-Object System.Collections.Generic.List[string]
foreach ($p in $ws) {
    if ($p.Length -lt 2) { continue }
    $ok = $w.CheckSpelling($p, $null, $false, "Português (Brasil)")
    if (-not $ok) { $ruins.Add($p) }
}
$ruins | Out-File -Encoding utf8 -Append $Saida
$doc.Close(0)
$w.Quit()
"fim: $($ruins.Count) palavras nao reconhecidas"
