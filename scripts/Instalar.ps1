param([Parameter(Mandatory=$true)][string]$PastaWoW)
$ErrorActionPreference = 'Stop'
$raizProjeto = Split-Path -Parent $PSScriptRoot
$origemAddon = Join-Path $raizProjeto 'dist\release\AzerothVoz'
if (-not (Test-Path -LiteralPath (Join-Path $origemAddon 'Pack.lua'))) { throw 'Gere o pacote primeiro. Leia o README.' }
$wowResolvido = (Resolve-Path -LiteralPath $PastaWoW).Path
if (-not (Test-Path -LiteralPath (Join-Path $wowResolvido 'WoW.exe'))) { throw 'A pasta deve conter WoW.exe.' }
if (Get-Process -Name WoW -ErrorAction SilentlyContinue) { throw 'Feche o jogo antes de instalar.' }
$pastaAddons = Join-Path $wowResolvido 'Interface\AddOns'
$destinoAddon = Join-Path $pastaAddons 'AzerothVoz'
if (Test-Path -LiteralPath $destinoAddon) { throw 'AzerothVoz já existe. Preserve a instalação e confirme uma atualização manual antes de substituí-la.' }
Write-Host "Origem: $origemAddon"
Write-Host "Destino: $destinoAddon"
$confirmacao = Read-Host 'Digite INSTALAR para confirmar a alteração na instalação do jogo'
if ($confirmacao -cne 'INSTALAR') { Write-Host 'Cancelado.'; exit 0 }
New-Item -ItemType Directory -Path $pastaAddons -Force | Out-Null
Copy-Item -LiteralPath $origemAddon -Destination $destinoAddon -Recurse
Write-Host 'Instalado. Ative AzerothVoz na seleção de personagens e teste /avoz demo.'
