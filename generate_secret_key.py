#!/usr/bin/env python3
"""
Script para gerar SECRET_KEY segura para Flask
"""

import secrets
import os

def generate_secret_key():
    """Gera uma SECRET_KEY segura"""
    # Método 1: token_urlsafe (recomendado)
    key1 = secrets.token_urlsafe(64)
    
    # Método 2: hex
    key2 = os.urandom(32).hex()
    
    # Método 3: token_hex
    key3 = secrets.token_hex(32)
    
    print("🔐 SECRET_KEY geradas com segurança:")
    print("=" * 60)
    print(f"Opção 1 (URL-safe): {key1}")
    print(f"Opção 2 (Hex):      {key2}")
    print(f"Opção 3 (Token):    {key3}")
    print("=" * 60)
    print("\n📝 Escolha qualquer uma das opções acima")
    print("⚠️  NUNCA compartilhe esta chave publicamente!")
    print("🚀 Configure no Railway: Variables → SECRET_KEY")
    
    return key1

if __name__ == "__main__":
    generate_secret_key() 