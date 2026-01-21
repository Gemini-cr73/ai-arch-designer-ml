$RG = "ai-arch-designer-rg"
$UI = "ai-arch-ui-prod"

Write-Host "Setting UI startup command on Azure..."
Write-Host "RG: $RG"
Write-Host "UI: $UI"
Write-Host "Entry: ui/streamlit_app.py"

$CMD = "streamlit run ui/streamlit_app.py --server.port 8000 --server.address 0.0.0.0 --server.headless true"

az webapp config set `
    -g $RG `
    -n $UI `
    --startup-file $CMD

Write-Host "Startup command set."

