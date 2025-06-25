# Script de configuração automática do ambiente JusCash API (Windows PowerShell)
# Gera SECRET_KEY automaticamente e cria arquivo .env se não existir

Write-Host "🔧 Configurando ambiente JusCash API..." -ForegroundColor Cyan

# Função para gerar SECRET_KEY
function Generate-SecretKey {
    return python -c "import secrets; print(secrets.token_urlsafe(64))"
}

# Verificar se .env existe
if (!(Test-Path ".env")) {
    Write-Host "📝 Criando arquivo .env..." -ForegroundColor Yellow
    
    # Gerar SECRET_KEY automaticamente
    $secretKey = Generate-SecretKey
    
    # Criar arquivo .env
    @"
# Configurações da aplicação
SECRET_KEY=$secretKey
FLASK_ENV=development

# Banco de dados PostgreSQL
DATABASE_URL=postgresql://juscash:juscash123@localhost:5432/juscash_db

# Redis para Celery
REDIS_URL=redis://localhost:6379/0

# Configurações do DJE
DJE_BASE_URL=https://dje.tjsp.jus.br/cdje

# Configurações Docker (para docker-compose)
POSTGRES_DB=juscash_db
POSTGRES_USER=juscash
POSTGRES_PASSWORD=juscash123
"@ | Out-File -FilePath ".env" -Encoding utf8
    
    Write-Host "✅ Arquivo .env criado com SECRET_KEY gerada automaticamente!" -ForegroundColor Green
    Write-Host "🔐 SECRET_KEY: $secretKey" -ForegroundColor Magenta
    
} else {
    Write-Host "📄 Arquivo .env já existe." -ForegroundColor Green
    
    # Verificar se SECRET_KEY existe no .env
    $envContent = Get-Content ".env" -ErrorAction SilentlyContinue
    if ($envContent -notmatch "SECRET_KEY=") {
        Write-Host "🔐 Adicionando SECRET_KEY ao .env existente..." -ForegroundColor Yellow
        $secretKey = Generate-SecretKey
        Add-Content -Path ".env" -Value "SECRET_KEY=$secretKey"
        Write-Host "✅ SECRET_KEY adicionada!" -ForegroundColor Green
        Write-Host "🔐 SECRET_KEY: $secretKey" -ForegroundColor Magenta
    } else {
        Write-Host "✅ SECRET_KEY já configurada no .env" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🚀 Configuração concluída!" -ForegroundColor Green
Write-Host "📋 Para usar:" -ForegroundColor Cyan
Write-Host "   Desenvolvimento local: python run.py" -ForegroundColor White
Write-Host "   Docker:               docker-compose up --build" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  NUNCA comite o arquivo .env no git!" -ForegroundColor Red 