#!/usr/bin/env python3
"""
Debug específico para o bot da loja
"""

import os
import sys
import asyncio
import logging
import traceback
from dotenv import load_dotenv

# Carrega configurações
load_dotenv()

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configuração de logging detalhado
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

async def debug_store_bot():
    """Debug detalhado do bot da loja"""
    try:
        print("🛍️ DEBUGANDO BOT DA LOJA...")
        
        # Importa os módulos necessários
        from store_bot.bot import StoreBot
        from store_bot.handlers import StoreHandlers
        from database.models import Database
        from config.settings import settings
        
        # Testa banco
        print("💾 Testando banco de dados...")
        db = Database(settings.DATABASE_PATH)
        user_test = db.create_user(123456789, "test_user", "Test User")
        print(f"✅ Banco funcionando: {user_test}")
        
        # Cria bot
        print("🔧 Criando instância do bot...")
        store_bot = StoreBot()
        
        # Testa conexão
        print("📡 Testando conexão...")
        bot_info = await store_bot.application.bot.get_me()
        print(f"✅ Bot conectado: @{bot_info.username}")
        
        # Testa handlers
        print("🎛️ Testando handlers...")
        handlers = store_bot.handlers
        print(f"✅ Handlers criados: {type(handlers)}")
        
        # Testa sistema de notificações
        print("🔔 Testando notificações...")
        notification = handlers.notification_system
        print(f"✅ Notificações: {type(notification)}")
        
        # Testa configurações
        print("⚙️ Testando configurações...")
        print(f"Admin ID: {settings.ADMIN_USER_ID}")
        print(f"Canal: {settings.SALES_CHANNEL_ID}")
        print(f"Suporte: {settings.SUPPORT_LINK}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ENCONTRADO: {e}")
        print("🔍 TRACEBACK COMPLETO:")
        traceback.print_exc()
        return False

async def test_start_command():
    """Testa especificamente o comando /start"""
    try:
        print("\n📍 TESTANDO COMANDO /start...")
        
        from store_bot.handlers import StoreHandlers
        from database.models import Database
        from utils.payment_system import PaymentSystem, ManualPaymentSystem
        from config.settings import settings
        
        # Mock do update e context
        class MockUser:
            def __init__(self):
                self.id = 123456789
                self.username = "test_user"
                self.first_name = "Test User"
        
        class MockMessage:
            def __init__(self):
                self.reply_photo = self._mock_reply_photo
                self.reply_text = self._mock_reply_text
            
            async def _mock_reply_photo(self, *args, **kwargs):
                print(f"📸 Mock reply_photo: {args}, {kwargs}")
            
            async def _mock_reply_text(self, *args, **kwargs):
                print(f"💬 Mock reply_text: {args}, {kwargs}")
        
        class MockUpdate:
            def __init__(self):
                self.effective_user = MockUser()
                self.message = MockMessage()
        
        class MockContext:
            pass
        
        # Cria handlers
        db = Database(settings.DATABASE_PATH)
        payment_system = PaymentSystem(settings.MERCADO_PAGO_TOKEN) if settings.MERCADO_PAGO_TOKEN else None
        manual_payment = ManualPaymentSystem()
        
        handlers = StoreHandlers(db, payment_system, manual_payment)
        
        # Testa comando
        update = MockUpdate()
        context = MockContext()
        
        await handlers.start_command(update, context)
        print("✅ Comando /start executado sem erros")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO no comando /start: {e}")
        traceback.print_exc()
        return False

async def main():
    """Função principal de debug"""
    print("🚀 DEBUG DETALHADO BOT DA LOJA")
    print("=" * 50)
    
    # Debug geral
    general_ok = await debug_store_bot()
    
    # Debug comando /start
    start_ok = await test_start_command()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO:")
    print(f"🔧 Bot Geral: {'✅' if general_ok else '❌'}")
    print(f"📍 Comando /start: {'✅' if start_ok else '❌'}")
    
    if general_ok and start_ok:
        print("\n🎉 BOT DA LOJA OK!")
    else:
        print("\n❌ PROBLEMAS ENCONTRADOS")

if __name__ == "__main__":
    asyncio.run(main())