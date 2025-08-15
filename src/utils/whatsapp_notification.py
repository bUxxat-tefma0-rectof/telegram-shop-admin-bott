#!/usr/bin/env python3
"""
Sistema de notificação WhatsApp usando CallMeBot API
"""

import requests
import logging
import urllib.parse
from typing import Optional

logger = logging.getLogger(__name__)

class WhatsAppNotifier:
    """Sistema de notificação via WhatsApp"""
    
    def __init__(self, phone: str, api_key: str, phone2: str = None, api_key2: str = None):
        self.phone = phone
        self.api_key = api_key
        self.phone2 = phone2
        self.api_key2 = api_key2
        self.base_url = "https://api.callmebot.com/whatsapp.php"
    
    async def send_message(self, message: str) -> bool:
        """Envia mensagem via WhatsApp para um ou ambos os números"""
        success1 = await self._send_to_phone(message, self.phone, self.api_key)
        
        success2 = True
        if self.phone2 and self.api_key2:
            success2 = await self._send_to_phone(message, self.phone2, self.api_key2)
        
        return success1 and success2
    
    async def _send_to_phone(self, message: str, phone: str, api_key: str) -> bool:
        """Envia mensagem para um número específico"""
        try:
            # Codifica a mensagem para URL
            encoded_message = urllib.parse.quote(message)
            
            # Monta a URL da API
            url = f"{self.base_url}?phone={phone}&text={encoded_message}&apikey={api_key}"
            
            # Envia a requisição
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Mensagem WhatsApp enviada com sucesso para {phone}")
                return True
            else:
                logger.error(f"Erro ao enviar WhatsApp para {phone}: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Erro na requisição WhatsApp para {phone}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado no WhatsApp para {phone}: {e}")
            return False
    
    async def send_support_request(self, user_data: dict) -> bool:
        """Envia notificação de solicitação de suporte"""
        try:
            user_name = user_data.get('first_name', 'Usuário')
            username = user_data.get('username', 'Sem username')
            user_id = user_data.get('user_id', 'Desconhecido')
            balance = user_data.get('balance', 0)
            
            message = f"""🆘 NOVA SOLICITAÇÃO DE SUPORTE!

👤 Nome: {user_name}
📱 Username: @{username}
🆔 ID: {user_id}
💰 Saldo: R$ {balance:.2f}

⏰ {self._get_current_time()}

Responda pelo Telegram: @{username}"""
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de suporte: {e}")
            return False
    
    async def send_new_sale_notification(self, purchase_data: dict) -> bool:
        """Envia notificação de nova venda"""
        try:
            user_name = purchase_data.get('user_name', 'Usuário')
            product_name = purchase_data.get('product_name', 'Produto')
            price = purchase_data.get('price', 0)
            user_id = purchase_data.get('user_id', 'Desconhecido')
            
            message = f"""💰 NOVA VENDA REALIZADA!

👤 Cliente: {user_name}
🛒 Produto: {product_name}
💵 Valor: R$ {price:.2f}
🆔 ID Cliente: {user_id}

⏰ {self._get_current_time()}

🎉 Parabéns pela venda!"""
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de venda: {e}")
            return False
    
    async def send_new_recharge_notification(self, recharge_data: dict) -> bool:
        """Envia notificação de nova recarga"""
        try:
            user_name = recharge_data.get('user_name', 'Usuário')
            amount = recharge_data.get('amount', 0)
            user_id = recharge_data.get('user_id', 'Desconhecido')
            
            message = f"""💳 NOVA RECARGA CONFIRMADA!

👤 Cliente: {user_name}
💰 Valor: R$ {amount:.2f}
🆔 ID Cliente: {user_id}

⏰ {self._get_current_time()}

💵 Mais saldo na conta!"""
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de recarga: {e}")
            return False
    
    async def send_new_user_notification(self, user_data: dict) -> bool:
        """Envia notificação de novo usuário"""
        try:
            user_name = user_data.get('first_name', 'Usuário')
            username = user_data.get('username', 'Sem username')
            user_id = user_data.get('user_id', 'Desconhecido')
            referred_by = user_data.get('referred_by')
            
            message = f"""👋 NOVO USUÁRIO REGISTRADO!

👤 Nome: {user_name}
📱 Username: @{username}
🆔 ID: {user_id}"""

            if referred_by:
                message += f"\n🔗 Indicado por: {referred_by}"
            
            message += f"\n\n⏰ {self._get_current_time()}"
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de novo usuário: {e}")
            return False
    
    def _get_current_time(self) -> str:
        """Retorna o horário atual formatado"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    def test_connection(self) -> bool:
        """Testa a conexão com a API"""
        try:
            test_message = "🤖 Teste de conexão - Bot funcionando!"
            url = f"{self.base_url}?phone={self.phone}&text={urllib.parse.quote(test_message)}&apikey={self.api_key}"
            
            response = requests.get(url, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erro no teste de conexão WhatsApp: {e}")
            return False