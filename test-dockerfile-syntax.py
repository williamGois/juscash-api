#!/usr/bin/env python3

import re

def validate_dockerfile():
    """Valida a sintaxe básica do Dockerfile"""
    print("🔍 Validando sintaxe do Dockerfile...")
    
    try:
        with open('Dockerfile', 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        issues = []
        
        # Verificar estrutura básica
        if not content.startswith('FROM'):
            issues.append("❌ Dockerfile deve começar com FROM")
        
        # Verificar comandos RUN com continuação
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('RUN') and '\\' in line:
                # Verificar se linhas de continuação estão corretas
                if not line.rstrip().endswith('\\'):
                    continue
                
                # Encontrar o final do comando RUN
                j = i
                while j < len(lines) and lines[j-1].rstrip().endswith('\\'):
                    j += 1
                
                run_block = '\n'.join(lines[i-1:j])
                if '&&' not in run_block:
                    issues.append(f"⚠️  Linha {i}: Comando RUN longo sem && pode falhar")
        
        # Verificar pacotes duplicados
        run_lines = [line for line in lines if 'apt-get install' in line]
        all_packages = []
        
        for line in run_lines:
            # Extrair pacotes da linha
            packages = re.findall(r'[a-z0-9\-\.]+', line)
            packages = [p for p in packages if not p in ['apt', 'get', 'install', 'no', 'install', 'recommends']]
            all_packages.extend(packages)
        
        duplicates = set([p for p in all_packages if all_packages.count(p) > 1])
        if duplicates:
            issues.append(f"⚠️  Pacotes duplicados encontrados: {', '.join(duplicates)}")
        
        # Verificar comandos essenciais
        essential_commands = ['WORKDIR', 'COPY', 'EXPOSE']
        for cmd in essential_commands:
            if cmd not in content:
                issues.append(f"⚠️  Comando {cmd} não encontrado")
        
        if issues:
            print("🚨 Problemas encontrados:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("✅ Dockerfile parece estar correto!")
            
            # Mostrar resumo
            print("\n📋 Resumo do Dockerfile:")
            print(f"  - Base image: {lines[0].split()[1]}")
            
            run_count = len([l for l in lines if l.strip().startswith('RUN')])
            print(f"  - Comandos RUN: {run_count}")
            
            copy_count = len([l for l in lines if l.strip().startswith('COPY')])
            print(f"  - Comandos COPY: {copy_count}")
            
            if 'google-chrome-stable' in content:
                print("  - ✅ Google Chrome será instalado")
            
            if 'xvfb' in content:
                print("  - ✅ Display virtual (xvfb) será instalado")
            
            return True
            
    except FileNotFoundError:
        print("❌ Arquivo Dockerfile não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao validar Dockerfile: {e}")
        return False

def show_docker_commands():
    """Mostra os comandos Docker para testar"""
    print("\n🐳 Comandos para testar (execute quando o Docker estiver disponível):")
    print("""
# 1. Build da imagem
docker compose build web

# 2. Ou build individual
docker build -t juscash-api .

# 3. Testar apenas a instalação do Chrome
docker run --rm juscash-api google-chrome --version

# 4. Subir todos os serviços
docker compose up --build

# 5. Ver logs se houver problemas
docker compose logs web
docker compose logs worker
""")

def main():
    print("🧪 Teste do Dockerfile - JusCash API\n")
    
    if validate_dockerfile():
        show_docker_commands()
        print("\n✅ Dockerfile validado com sucesso!")
        print("💡 Agora você pode executar os comandos Docker listados acima.")
    else:
        print("\n❌ Corrija os problemas no Dockerfile antes de continuar.")

if __name__ == "__main__":
    main() 