# deploy/azure_set_ui_env.ps1
# Sets environment variables for the UI Web App (Streamlit)

param(
    [Parameter(Mandatory = $false)]
    [string]$ResourceGroup = "ai-arch-designer-rg",

    [Parameter(Mandatory = $false)]
    [string]$UiAppName = "ai-arch-ui-prod",

    # IMPORTANT: put your API base url here (custom domain OR azurewebsites.net)
    [Parameter(Mandatory = $false)]
    [string]$ApiBaseUrl = "https://arch-api.ai-coach-lab.com"
)

$ErrorActionPreference = "Stop"

Write-Host "Setting UI env vars on Azure..." -ForegroundColor Cyan
Write-Host "  RG: $ResourceGroup"
Write-Host "  UI: $UiAppName"
Write-Host "  API_BASE_URL: $ApiBaseUrl"

# For Linux containers, many examples set BOTH PORT and WEBSITES_PORT.
# Your container must listen on the same port Azure routes to.
az webapp config appsettings set `
    -g $ResourceGroup `
    -n $UiAppName `
    --settings `
    API_BASE_URL=$ApiBaseUrl `
    PORT=8000 `
    WEBSITES_PORT=8000 | Out-Null

Write-Host "✅ Env vars set." -ForegroundColor Green

Write-Host "Current values (sanity check):" -ForegroundColor Yellow
az webapp config appsettings list `
    -g $ResourceGroup `
    -n $UiAppName `
    --query "[?name=='API_BASE_URL' || name=='PORT' || name=='WEBSITES_PORT'].[name,value]" `
    -o table
