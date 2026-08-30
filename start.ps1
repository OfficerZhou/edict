# ══════════════════════════════════════════════════════════
# 三省六部 · 看板服务一键启动 (Windows/PowerShell)
# 与 start.sh 行为一致：初始化 data/ → 启动看板服务器(7891)
# 检测到 openclaw CLI 才附加数据刷新循环，否则只读模式。
#
# 用法:
#   .\start.ps1            # 启动（Ctrl+C 关闭）
#   .\start.ps1 -Port 8080 # 指定端口
# ══════════════════════════════════════════════════════════
param([int]$Port = 7891)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
Set-Location $Root

# ── 解析 Python 3.10+（EDICT_PYTHON > python > python3 > py 启动器）──
function Get-PythonArgs {
    if ($env:EDICT_PYTHON) { return ,@($env:EDICT_PYTHON) }
    $pyVer = 'import sys;print(sys.version_info[0]*10+sys.version_info[1])'
    foreach ($c in @('python', 'python3')) {
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        try { $v = (& $cmd.Source -c $pyVer 2>$null) } catch { continue }
        $v = ([string]$v).Trim()
        if ($v -match '^\d+$' -and [int]$v -ge 310) { return ,@($cmd.Source) }
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return ,@('py', '-3') }
    throw '未找到 Python 3.10+（请安装 Python 或设置 EDICT_PYTHON 环境变量）'
}

$pyArgs = Get-PythonArgs

# ── 初始化必需的数据文件（不存在时建空壳）──
New-Item -ItemType Directory -Force -Path (Join-Path $Root 'data') | Out-Null
foreach ($f in @('live_status.json','agent_config.json','model_change_log.json','sync_status.json',
                 'pending_model_changes.json','tasks_source.json','tasks.json','officials.json',
                 'officials_stats.json')) {
    $p = Join-Path $Root "data\$f"
    if (-not (Test-Path $p)) {
        $init = if ($f -in @('pending_model_changes.json','tasks_source.json','tasks.json','officials.json')) { '[]' } else { '{}' }
        Set-Content -Path $p -Value $init -Encoding utf8
    }
}

$server = $null; $loop = $null
try {
    Write-Host "═══ 三省六部 · 服务启动中 ═══"

    # ── 数据刷新循环 ──
    if (Get-Command openclaw -ErrorAction SilentlyContinue) {
        Write-Host "▶ 启动数据刷新循环（OpenClaw 同步模式）..."
        $loop = Start-Process powershell -ArgumentList '-NoProfile','-File',(Join-Path $Root 'scripts\run_loop.ps1') -PassThru
    } else {
        Write-Host "▶ 启动数据刷新循环（通用模式：每 15 秒刷新看板数据）..."
        $pyExe = $pyArgs[0]
        $pyExtra = @()
        if ($pyArgs.Length -gt 1) { $pyExtra = @($pyArgs[1..($pyArgs.Length-1)]) | ForEach-Object { "'$_'" } }
        $loopCmd = "while (`$true) { & '$pyExe' " + ($pyExtra -join ' ') +
                   " '$(Join-Path $Root 'scripts\refresh_live_data.py')' 2>`$null; Start-Sleep -Seconds 15 }"
        $loop = Start-Process powershell -ArgumentList '-NoProfile','-Command',$loopCmd -PassThru
    }

    # ── 看板服务器 ──
    $extraArgs = @()
    if ($pyArgs.Length -gt 1) { $extraArgs = @($pyArgs[1..($pyArgs.Length-1)]) }
    $serverArgs = $extraArgs + @((Join-Path 'dashboard' 'server.py'), '--port', "$Port")
    Write-Host "▶ 启动看板服务器 (Python: $($pyArgs -join ' '))..."
    $server = Start-Process -FilePath $pyArgs[0] -ArgumentList $serverArgs -PassThru

    Write-Host "✅ 服务已启动！看板地址: http://127.0.0.1:$Port  （Ctrl+C 关闭）"
    Start-Process "http://127.0.0.1:$Port"

    # ── 等待；若服务器进程退出则整体退出 ──
    while ($true) {
        Start-Sleep -Seconds 2
        if ($server.HasExited) {
            Write-Host "看板服务器已退出 (code=$($server.ExitCode))"
            break
        }
    }
}
finally {
    foreach ($p in @($loop, $server)) {
        if ($p) { try { if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force } } catch {} }
    }
    Write-Host "已关闭"
}
