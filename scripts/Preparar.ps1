$ErrorActionPreference = 'Stop'
$raizProjeto = Split-Path -Parent $PSScriptRoot
Push-Location $raizProjeto
try {
    if (-not (Test-Path '.venv\Scripts\python.exe')) {
        py -3 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Instale Python 3.12 de python.org e tente novamente.' }
    }
    & '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar dependências.' }
    & '.\.venv\Scripts\python.exe' tools/download_voice.py
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao baixar o modelo de voz.' }
    & '.\.venv\Scripts\python.exe' tools/build_pack.py --out dist/release/AzerothVoz
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao gerar pacote; a saída deve ser uma pasta nova.' }
    Write-Host 'Pacote gerado em dist\release\AzerothVoz.'
} finally { Pop-Location }
