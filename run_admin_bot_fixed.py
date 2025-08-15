#!/usr/bin/env python3
"""
Bot Administrativo - Versão Corrigida com Error Handling
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Carrega configurações
load_dotenv()

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Função principal do bot admin"""
    try:
        from admin_bot.bot import AdminBot
        
        print("🔧 Iniciando Bot Administrativo...")
        print(f"Token: {os.getenv('ADMIN_BOT_TOKEN')[:10]}...")
        
        # Cria instância do bot
        admin_bot = AdminBot()
        
        # Testa conexão
        bot_info = await admin_bot.application.bot.get_me()
        print(f"✅ Bot conectado: @{bot_info.username}")
        print(f"📋 ID do Bot: {bot_info.id}")
        print(f"👤 Nome: {bot_info.first_name}")
        
        # Inicia o bot
        print("🚀 Iniciando polling...")
        await admin_bot.run()
        
    except KeyboardInterrupt:
        print("\n⏹️ Bot parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal no bot admin: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())