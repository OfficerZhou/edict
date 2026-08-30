# ══════════════════════════════════════════════════════════
# 三省六部 · 军机处看板一键启动 (Windows/PowerShell)
# 等价实现见 board/server.py（零依赖 stdlib）。
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

# ── 初始化必需的数据文件（看板只认这两个）──
New-Item -ItemType Directory -Force -Path (Join-Path $Root 'data') | Out-Null
foreach ($f in @('tasks_source.json', 'audit_log.json')) {
    $p = Join-Path $Root "data\$f"
    if (-not (Test-Path $p)) { Set-Content -Path $p -Value '[]' -Encoding utf8 }
}

$server = $null
try {
    Write-Host "═══ 军机处 · 服务启动中 ═══"
    $extraArgs = @()
    if ($pyArgs.Length -gt 1) { $extraArgs = @($pyArgs[1..($pyArgs.Length-1)]) }
    $serverArgs = $extraArgs + @((Join-Path 'board' 'server.py'), '--port', "$Port")
    Write-Host "▶ 启动看板服务 (Python: $($pyArgs -join ' '))..."
    $server = Start-Process -FilePath $pyArgs[0] -ArgumentList $serverArgs -PassThru

    Write-Host "✅ 已启动！看板: http://127.0.0.1:$Port  （Ctrl+C 关闭）"
    Start-Process "http://127.0.0.1:$Port"

    while ($true) {
        Start-Sleep -Seconds 2
        if ($server.HasExited) {
            Write-Host "看板服务已退出 (code=$($server.ExitCode))"
            break
        }
    }
}
finally {
    if ($server) { try { if (-not $server.HasExited) { Stop-Process -Id $server.Id -Force } } catch {} }
    Write-Host "已关闭"
}
