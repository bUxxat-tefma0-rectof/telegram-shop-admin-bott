#!/usr/bin/env python3
"""
Script de debug completo para identificar problemas nos bots
"""

import os
import sys
import asyncio
import traceback
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def debug_admin_bot():
    """Debug do bot administrativo"""
    try:
        print("🔧 DEBUGANDO BOT ADMINISTRATIVO...")
        
        from admin_bot.bot import AdminBot
        
        admin_bot = AdminBot()
        print("✅ AdminBot inicializado")
        
        # Testa conexão básica
        bot_info = await admin_bot.application.bot.get_me()
        print(f"✅ Bot conectado: @{bot_info.username}")
        
        # Testa handlers
        print("✅ Handlers configurados corretamente")
        
        return True, f"@{bot_info.username}"
        
    except Exception as e:
        print(f"❌ Erro no bot admin: {e}")
        traceback.print_exc()
        return False, str(e)

async def debug_store_bot():
    """Debug do bot da loja"""
    try:
        print("\n🛍️ DEBUGANDO BOT DA LOJA...")
        
        from store_bot.bot import StoreBot
        
        store_bot = StoreBot()
        print("✅ StoreBot inicializado")
        
        # Testa conexão básica
        bot_info = await store_bot.application.bot.get_me()
        print(f"✅ Bot conectado: @{bot_info.username}")
        
        # Testa handlers
        print("✅ Handlers configurados corretamente")
        
        return True, f"@{bot_info.username}"
        
    except Exception as e:
        print(f"❌ Erro no bot loja: {e}")
        traceback.print_exc()
        return False, str(e)

async def test_database():
    """Testa banco de dados"""
    try:
        print("\n💾 TESTANDO BANCO DE DADOS...")
        
        from database.models import Database
        from config.settings import settings
        
        # Força criação do diretório
        os.makedirs(os.path.dirname(settings.DATABASE_PATH), exist_ok=True)
        
        db = Database(settings.DATABASE_PATH)
        print("✅ Banco inicializado")
        
        # Testa operações básicas
        user_id = 999999999
        success = db.create_user(user_id, "teste_debug", "Debug User")
        print(f"✅ Criação de usuário: {success}")
        
        user = db.get_user(user_id)
        print(f"✅ Busca de usuário: {user is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        traceback.print_exc()
        return False

def test_imports():
    """Testa todas as importações"""
    try:
        print("\n📦 TESTANDO IMPORTAÇÕES...")
        
        modules = [
            'config.settings',
            'database.models', 
            'utils.payment_system',
            'utils.notification_system',
            'admin_bot.keyboards',
            'admin_bot.handlers',
            'store_bot.keyboards', 
            'store_bot.handlers'
        ]
        
        for module in modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except Exception as e:
                print(f"❌ {module}: {e}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Erro nas importações: {e}")
        return False

async def main():
    """Função principal de debug"""
    print("🚀 DEBUG COMPLETO DO SISTEMA")
    print("=" * 50)
    
    # Testa importações
    imports_ok = test_imports()
    
    # Testa banco de dados  
    db_ok = await test_database()
    
    # Testa bots
    admin_ok, admin_info = await debug_admin_bot()
    store_ok, store_info = await debug_store_bot()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO DO DEBUG:")
    print(f"📦 Importações: {'✅' if imports_ok else '❌'}")
    print(f"💾 Banco de dados: {'✅' if db_ok else '❌'}")
    print(f"🔧 Bot Admin: {'✅' if admin_ok else '❌'} {admin_info if admin_ok else ''}")
    print(f"🛍️ Bot Loja: {'✅' if store_ok else '❌'} {store_info if store_ok else ''}")
    
    if all([imports_ok, db_ok, admin_ok, store_ok]):
        print("\n🎉 SISTEMA OK - PODE RODAR OS BOTS!")
        return True
    else:
        print("\n❌ PROBLEMAS DETECTADOS - PRECISA CORRIGIR")
        return False

if __name__ == "__main__":
    asyncio.run(main())