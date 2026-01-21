
# install_vscode_extensions.ps1
# Usage: .\scripts\install_vscode_extensions.ps1

$ErrorActionPreference = "Stop"

if (-Not (Get-Command code -ErrorAction SilentlyContinue)) {
  Write-Host "❌ VS Code 'code' CLI not found."
  Write-Host "In VS Code: Ctrl+Shift+P -> 'Shell Command: Install code command in PATH' -> restart terminal."
  exit 1
}

$extFile = ".\extensions.txt"

if (-Not (Test-Path $extFile)) {
  Write-Host "❌ extensions.txt not found at $extFile"
  Write-Host "Create it in the project root (ai-arch-designer-ml\extensions.txt)."
  exit 1
}

Write-Host "==> Installing extensions from extensions.txt..."

Get-Content $extFile |
Where-Object { $_ -and -not $_.StartsWith("#") } |
ForEach-Object {
  $ext = $_.Trim()
  if ($ext) {
    Write-Host "Installing: $ext"
    code --install-extension $ext
  }
}

Write-Host "✅ Done installing extensions."
