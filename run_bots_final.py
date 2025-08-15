#!/usr/bin/env python3
"""
Script Final - Roda ambos os bots de forma estável
"""

import os
import sys
import asyncio
import logging
import signal
from dotenv import load_dotenv

# Carrega configurações
load_dotenv()

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configuração de logging mais limpa
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING  # Menos verbose
)

# Variável global para controlar shutdown
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Handler para sinais de shutdown"""
    print("\n🛑 Parando bots...")
    shutdown_event.set()

async def run_admin_bot():
    """Executa o bot administrativo"""
    try:
        from admin_bot.bot import AdminBot
        
        print("🔧 Bot Admin: Iniciando...")
        admin_bot = AdminBot()
        
        # Testa conexão
        bot_info = await admin_bot.application.bot.get_me()
        print(f"✅ Bot Admin: @{bot_info.username} online")
        
        # Executa o bot
        await admin_bot.run()
        
    except Exception as e:
        print(f"❌ Erro no Bot Admin: {e}")

async def run_store_bot():
    """Executa o bot da loja"""
    try:
        from store_bot.bot import StoreBot
        
        print("🛍️ Bot Loja: Iniciando...")
        store_bot = StoreBot()
        
        # Testa conexão
        bot_info = await store_bot.application.bot.get_me()
        print(f"✅ Bot Loja: @{bot_info.username} online")
        
        # Executa o bot
        await store_bot.run()
        
    except Exception as e:
        print(f"❌ Erro no Bot Loja: {e}")

async def main():
    """Função principal que roda ambos os bots"""
    # Configura handlers de sinal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 INICIANDO SISTEMA DE BOTS")
    print("=" * 40)
    
    try:
        # Executa ambos os bots em paralelo
        tasks = [
            asyncio.create_task(run_admin_bot()),
            asyncio.create_task(run_store_bot())
        ]
        
        print("\n✅ AMBOS OS BOTS ESTÃO ONLINE!")
        print("📱 Você pode testar agora enviando /start para qualquer bot")
        print("🛑 Pressione Ctrl+C para parar")
        
        # Aguarda até receber sinal de shutdown
        await shutdown_event.wait()
        
        # Cancela todas as tasks
        for task in tasks:
            task.cancel()
        
        # Aguarda as tasks terminarem
        await asyncio.gather(*tasks, return_exceptions=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutdown solicitado")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
    finally:
        print("👋 Bots parados")

if __name__ == "__main__":
    asyncio.run(main())