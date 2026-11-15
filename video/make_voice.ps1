param([string]$Out, [string]$Voice = "Mark", [double]$Rate = 1.3)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, $type) { $t = $asTask.MakeGenericMethod($type).Invoke($null, @($op)); $t.Wait(-1) | Out-Null; $t.Result }
[void][Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media.SpeechSynthesis, ContentType = WindowsRuntime]
$all = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices
"VOICES: " + (($all | ForEach-Object { $_.DisplayName + '/' + $_.Language }) -join '; ')
$syn = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer; $syn.Options.SpeakingRate = $Rate
$v = $all | Where-Object { $_.DisplayName -like "*$Voice*" -and $_.Language -like 'en*' } | Select-Object -First 1
if ($v) { $syn.Voice = $v; "USING: " + $v.DisplayName }
$segs = @(
 'Fire has no up in space.',
 'What does that mean for a Moon base?',
 'Ember maps 24 NASA investigations and 255 cited claims.',
 'Lunar-base air?',
 'Forty-eight tests, all in microgravity.',
 'Zero in partial gravity.',
 'Outside that archive, NASA data shows materials burning at lower oxygen on the Moon.',
 'Ask a question.',
 'Ember answers with a page citation, or honestly refuses.',
 'Ember. Evidence, with its limits.')
$rates = @(1.1,1.1,1.15,1.1,1.1,1.1,1.1,1.1,1.1,1.3)
$i = 0
foreach ($s in $segs) {
  $i++
  $syn.Options.SpeakingRate = $rates[$i-1]
  $st = Await ($syn.SynthesizeTextToStreamAsync($s)) ([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
  $rs = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($st)
  $fs = [System.IO.File]::Create((Join-Path $Out ("seg{0:D2}.wav" -f $i)))
  $rs.CopyTo($fs); $fs.Close(); $rs.Close()
}
"DONE"
