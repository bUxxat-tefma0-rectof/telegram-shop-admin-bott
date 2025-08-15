#!/usr/bin/env python3
"""
Debug do sistema de ligação
"""

import asyncio
import sys
import os

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import settings
from utils.whatsapp_call_system import WhatsAppCallSystem

async def debug_call():
    """Debug detalhado da ligação"""
    print("🔧 DEBUG SISTEMA DE LIGAÇÃO")
    print("=" * 50)
    
    # Configurações
    print(f"📱 Phone: {settings.WHATSAPP_CALL_PHONE}")
    print(f"🔑 API: {settings.WHATSAPP_CALL_API_KEY}")
    
    # Cria sistema
    call_system = WhatsAppCallSystem(
        settings.WHATSAPP_CALL_PHONE,
        settings.WHATSAPP_CALL_API_KEY
    )
    
    # Testa com seu próprio número (que você sabe que funciona)
    test_phone = settings.WHATSAPP_CALL_PHONE  # Usa o próprio número para teste
    print(f"\n🧪 Testando com número: {test_phone}")
    
    # Valida número
    is_valid, formatted = call_system.validate_phone_number(test_phone)
    print(f"Validação: {is_valid} → {formatted}")
    
    if is_valid:
        print(f"\n📞 Iniciando ligação para {formatted}")
        success = await call_system.initiate_support_call(formatted, "TESTE DEBUG")
        print(f"Resultado: {'✅ SUCESSO' if success else '❌ FALHOU'}")
        
        if not success:
            print("\n🔍 Testando envio direto...")
            direct_success = await call_system._send_call_message(
                formatted, 
                "🧪 Teste direto do sistema de ligação"
            )
            print(f"Envio direto: {'✅ SUCESSO' if direct_success else '❌ FALHOU'}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(debug_call())