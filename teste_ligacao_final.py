#!/usr/bin/env python3
"""
Teste final do sistema de ligação automática
"""

import asyncio
import sys
import os

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import settings
from utils.whatsapp_call_system import WhatsAppCallSystem

async def test_final():
    """Teste final com vários formatos de número"""
    print("🚀 TESTE FINAL - SISTEMA DE LIGAÇÃO")
    print("=" * 60)
    
    # Cria sistema
    call_system = WhatsAppCallSystem(
        settings.WHATSAPP_CALL_PHONE,
        settings.WHATSAPP_CALL_API_KEY
    )
    
    # Números de teste em vários formatos
    test_numbers = [
        "(11) 99999-9999",
        "11999999999", 
        "44998765432",
        "554498691568",  # Seu número
        "5544987654321"
    ]
    
    print(f"📱 Sistema configurado: {settings.WHATSAPP_CALL_PHONE}")
    print(f"🔑 API Key: {settings.WHATSAPP_CALL_API_KEY}")
    
    for i, number in enumerate(test_numbers, 1):
        print(f"\n🧪 TESTE {i}: {number}")
        
        # Valida
        is_valid, formatted = call_system.validate_phone_number(number)
        print(f"   Validação: {'✅' if is_valid else '❌'} → {formatted}")
        
        if is_valid:
            # Testa ligação apenas para o primeiro (não enviar para todos)
            if i == 1:
                print(f"   🔄 Testando ligação...")
                success = await call_system.initiate_support_call(formatted, f"Cliente Teste {i}")
                print(f"   Resultado: {'✅ SUCESSO' if success else '❌ FALHOU'}")
            else:
                print(f"   ⏭️ Validação OK - pulando envio")
    
    print(f"\n" + "=" * 60)
    print("🎉 SISTEMA DE LIGAÇÃO PRONTO!")
    print("\n📞 Como funciona:")
    print("1. Cliente clica 'Suporte' → 'Ligação Automática'")
    print("2. Digite número → Sistema valida automaticamente")
    print("3. Robô envia mensagem via WhatsApp")
    print("4. Você recebe notificação completa")
    print("\n🚀 TESTE NO BOT: @Lojaadm_bot")

if __name__ == "__main__":
    asyncio.run(test_final())