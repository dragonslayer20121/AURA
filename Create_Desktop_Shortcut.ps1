$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $root "dist\AURA\AURA.exe"
if (-not (Test-Path $exe)) {
    throw "AURA.exe was not found. Run Build_AURA.bat first."
}
$desktop = [Environment]::GetFolderPath("Desktop")
$linkPath = Join-Path $desktop "AURA.lnk"
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut($linkPath)
$link.TargetPath = $exe
$link.WorkingDirectory = (Split-Path -Parent $exe)
$link.IconLocation = "$exe,0"
$link.Description = "AURA desktop customization"
$link.Save()
Write-Host "Created shortcut: $linkPath"
