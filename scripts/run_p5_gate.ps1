$ErrorActionPreference = 'Continue'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root
$reportPath = Join-Path $root 'reports/qa/p5_gate_result.md'
New-Item -ItemType Directory -Force -Path (Split-Path $reportPath) | Out-Null
$python = $null
$prefix = @()
$localPython = Join-Path $root '.venv\Scripts\python.exe'
if (Test-Path -LiteralPath $localPython) { $python = $localPython }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $python = (Get-Command python).Source }
elseif (Get-Command py -ErrorAction SilentlyContinue) { $python = (Get-Command py).Source; $prefix = @('-3.12') }
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('# P5 gate results')
$lines.Add('')
$lines.Add("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')")
$lines.Add('')
$lines.Add('Gate status: **pending evidence** until every check below has a passing command result.')
$lines.Add('')
$checks = @(
    @{Name='Python dependency smoke test'; Args=@('scripts/smoke_test.py')},
    @{Name='Full repository test suite'; Args=@('-m','pytest','-q')},
    @{Name='TS-08/TS-09 for six algorithms'; Args=@('-m','pytest','-q','tests/coverage/test_p5_gate.py::test_ts08_ts09_full_and_constrained_coverage_for_each_algorithm')},
    @{Name='100 seeded movement invariants'; Args=@('-m','pytest','-q','tests/coverage/test_p5_gate.py::test_invariant_100_seeded_scenarios')},
    @{Name='Planning state immutability for six algorithms'; Args=@('-m','pytest','-q','tests/coverage/test_p5_gate.py::test_planning_preserves_robot_snapshot_for_each_algorithm')},
    @{Name='Event replay equivalence and schema version'; Args=@('-m','pytest','-q','tests/coverage/test_p5_gate.py::test_event_replay_equivalence_and_schema_version')},
    @{Name='Department-map coverage metrics and memory bound'; Args=@('-s','-m','pytest','-q','tests/coverage/test_p5_gate.py::test_department_headless_runs_report_metrics_and_bounded_memory')}
)
$departmentOutput = ''
if ($python) {
    $versionOutput = & $python @prefix --version 2>&1 | Out-String
    $lines.Add(('Interpreter: `{0} {1}` - {2}' -f $python, ($prefix -join ' '), $versionOutput.Trim()))
} else {
    $lines.Add('Interpreter: **not found** (searched repo .venv, PATH python, PATH py).')
}
$lines.Add('')
foreach ($check in $checks) {
    $lines.Add("## $($check.Name)")
    $args = @($prefix) + @($check.Args)
    $command = if ($python) { ('& "{0}" {1}' -f $python, ($args -join ' ')) } else { ('python ' + ($check.Args -join ' ')) }
    $lines.Add('')
    $lines.Add(('Command: `{0}`' -f $command))
    $lines.Add('')
    $lines.Add('```text')
    if ($python) {
        $output = & $python @args 2>&1 | Out-String
        $exit = $LASTEXITCODE
        if ($check.Name -like 'Department-map*') { $departmentOutput = $output }
        if ($output.Trim()) { $lines.Add($output.TrimEnd()) } else { $lines.Add('(no output)') }
        $status = if ($exit -eq 0) { 'PASS' } else { 'FAIL' }
    } else {
        $lines.Add('FAIL: NOT RUN — no interpreter is installed or discoverable.')
        $status = 'FAIL'
    }
    $lines.Add('```')
    $lines.Add('')
    $lines.Add("**$status**")
    $lines.Add('')
}
$lines.Add('## Department-map coverage table')
$lines.Add('')
$lines.Add('| Algorithm | Coverage % | Steps | Energy | Sim time (s) | Stop reason | Planner wall time (s) |')
$lines.Add('|---|---:|---:|---:|---:|---|---:|')
foreach ($name in @('bfs','dfs','ucs','greedy','astar','iddfs')) {
    $match = [regex]::Match($departmentOutput, "(?m)^$name,([^\r\n]+)$")
    if ($match.Success) {
        $values = $match.Groups[1].Value.Split(',')
        $lines.Add("| $name | $($values[0]) | $($values[1]) | $($values[2]) | $($values[3]) | $($values[4]) | $($values[5]) |")
    } else { $lines.Add("| $name | NOT RUN | NOT RUN | NOT RUN | NOT RUN | pending evidence | NOT RUN |") }
}
$lines.Add('')
$allPass = $python -and ($lines -join "`n") -notmatch '\*\*FAIL\*\*'
if ($allPass) { $lines[4] = 'Gate status: **PASS** - all recorded checks exited successfully.' }
else { $lines[4] = 'Gate status: **pending evidence** - one or more checks failed or could not run.' }
$lines | Set-Content -LiteralPath $reportPath -Encoding utf8
$lines | Write-Output
if (-not $allPass) { exit 1 }
