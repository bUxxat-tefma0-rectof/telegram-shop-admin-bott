#!/usr/bin/env python3
"""
Script para executar ambos os bots simultaneamente
"""

import os
import sys
import threading
import time

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from admin_bot.bot import AdminBot
from store_bot.bot import StoreBot

def run_admin_bot():
    """Executa o bot administrativo"""
    try:
        print("🤖 Iniciando Bot Administrativo...")
        admin_bot = AdminBot()
        admin_bot.run()
    except Exception as e:
        print(f"❌ Erro no Bot Administrativo: {e}")

def run_store_bot():
    """Executa o bot da loja"""
    try:
        print("🛒 Iniciando Bot da Loja...")
        store_bot = StoreBot()
        store_bot.run()
    except Exception as e:
        print(f"❌ Erro no Bot da Loja: {e}")

def main():
    """Executa ambos os bots em threads separadas"""
    print("🚀 Iniciando sistema completo de bots...")
    
    # Cria threads para cada bot
    admin_thread = threading.Thread(target=run_admin_bot, daemon=True)
    store_thread = threading.Thread(target=run_store_bot, daemon=True)
    
    # Inicia as threads
    admin_thread.start()
    time.sleep(2)  # Pequeno delay entre inicializações
    store_thread.start()
    
    print("✅ Ambos os bots foram iniciados!")
    print("💡 Pressione Ctrl+C para parar ambos os bots")
    
    try:
        # Mantém o programa principal rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Parando ambos os bots...")
        sys.exit(0)

if __name__ == "__main__":
    main()