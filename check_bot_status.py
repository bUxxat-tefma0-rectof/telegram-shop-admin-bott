#!/usr/bin/env python3
"""
Script para verificar se os bots estão funcionando com os novos tokens
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_bot_connection():
    """Testa conexão com os bots"""
    
    try:
        from telegram import Bot
        
        # Tokens dos bots
        admin_token = os.getenv('ADMIN_BOT_TOKEN')
        store_token = os.getenv('STORE_BOT_TOKEN')
        
        print("🔄 Testando conexão com os bots...")
        
        # Testa bot admin
        admin_bot = Bot(token=admin_token)
        admin_info = await admin_bot.get_me()
        print(f"✅ Bot Admin conectado: @{admin_info.username}")
        
        # Testa bot loja
        store_bot = Bot(token=store_token)
        store_info = await store_bot.get_me()
        print(f"✅ Bot Loja conectado: @{store_info.username}")
        
        print("\n🎉 AMBOS OS BOTS ESTÃO FUNCIONANDO!")
        print(f"\n📱 Seus bots:")
        print(f"   🔧 Admin: @{admin_info.username}")
        print(f"   🛍️ Loja: @{store_info.username}")
        print(f"\n✅ Você pode testar agora enviando /start para qualquer um dos bots!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar bots: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_bot_connection())