# deploy/azure_tail_logs.ps1
# Tails live logs for the UI Web App (Streamlit) and optionally the API

param(
    [Parameter(Mandatory = $false)]
    [string]$ResourceGroup = "ai-arch-designer-rg",

    [Parameter(Mandatory = $false)]
    [string]$UiAppName = "ai-arch-ui-prod",

    [Parameter(Mandatory = $false)]
    [string]$ApiAppName = "ai-arch-api-prod",

    [Parameter(Mandatory = $false)]
    [ValidateSet("ui", "api")]
    [string]$Target = "ui"
)

$ErrorActionPreference = "Stop"

if ($Target -eq "ui") {
    Write-Host "Tailing UI logs: $UiAppName" -ForegroundColor Cyan
    az webapp log tail -g $ResourceGroup -n $UiAppName
}
else {
    Write-Host "Tailing API logs: $ApiAppName" -ForegroundColor Cyan
    az webapp log tail -g $ResourceGroup -n $ApiAppName
}
