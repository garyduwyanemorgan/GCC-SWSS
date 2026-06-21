# Starts the GCC-SWSS Next.js dashboard at http://localhost:3000
# Reads web/.env.local (NEXT_PUBLIC_API_URL=http://localhost:8078).
Set-Location "$PSScriptRoot\web"
if (-not (Test-Path ".env.local")) { Copy-Item ".env.local.example" ".env.local" }
npm run dev
