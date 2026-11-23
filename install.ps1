<#
.SYNOPSIS
    Instalador CyberLab para Windows (PowerShell 5.1+ o PowerShell 7+).

.DESCRIPTION
    Busca Python 3 y delega en install.py. Los parametros se reenvian tal cual.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install.ps1 -Profile core -Yes

.EXAMPLE
    .\install.ps1 -Profile lab -Yes -AuthorizeLab -Only docker,virtualbox
#>
[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$InstallerArgs
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Installer = Join-Path $ScriptDir 'install.py'
$PythonExe = $null
$PythonPrefix = @()

foreach ($candidate in @('py', 'python', 'python3')) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($null -eq $cmd) { continue }

    if ($candidate -eq 'py') {
        & py -3 --version 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $PythonExe = 'py'; $PythonPrefix = @('-3'); break }
    }
    else {
        & $candidate --version 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $PythonExe = $candidate; $PythonPrefix = @(); break }
    }
}

if ($null -eq $PythonExe) {
    Write-Error 'No se encontro Python 3. Instalalo desde https://www.python.org/downloads/ y marca "Add Python to PATH".'
    exit 2
}

# Transforma -Profile core -> --profile core para aceptar ambos estilos.
$Forward = @()
foreach ($arg in $InstallerArgs) {
    $Forward += $arg -replace '^-(Profile|Only|Skip|Check|DryRun|Yes|AuthorizeLab|NoSudo|PM|Log|Report|List|Verbose|Version)\b', '--$1'
}

Write-Host "CyberLab Setup -> $PythonExe $($PythonPrefix -join ' ') $Installer $($Forward -join ' ')"
& $PythonExe @PythonPrefix $Installer @Forward
exit $LASTEXITCODE
