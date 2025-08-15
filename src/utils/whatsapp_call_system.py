#!/usr/bin/env python3
"""
Sistema de ligação automática via WhatsApp CallMeBot
"""

import requests
import logging
import urllib.parse
import re
from typing import Optional

logger = logging.getLogger(__name__)

class WhatsAppCallSystem:
    """Sistema de ligação automática via WhatsApp"""
    
    def __init__(self, call_phone: str, call_api_key: str):
        self.call_phone = call_phone
        self.call_api_key = call_api_key
        self.call_url = "https://api.callmebot.com/whatsapp.php"
    
    def validate_phone_number(self, phone: str) -> tuple[bool, str]:
        """Valida e formata número de telefone brasileiro"""
        # Remove todos os caracteres não numéricos
        clean_phone = re.sub(r'[^\d]', '', phone)
        
        logger.info(f"Validando número: '{phone}' → '{clean_phone}' (len: {len(clean_phone)})")
        
        # Verifica formatos válidos
        if len(clean_phone) == 13 and clean_phone.startswith('55'):
            # Já tem código do país (formato completo)
            return True, clean_phone
        
        elif len(clean_phone) == 12 and clean_phone.startswith('55'):
            # Com código do país mas sem o 9 (adiciona 9 se necessário)
            if clean_phone[4] != '9':  # Se não tem o 9 do celular
                formatted = f"{clean_phone[:4]}9{clean_phone[4:]}"
                return True, formatted
            return True, clean_phone
        
        elif len(clean_phone) == 11:
            # 11 dígitos - número completo brasileiro sem código do país
            formatted = f"55{clean_phone}"
            return True, formatted
        
        elif len(clean_phone) == 10:
            # 10 dígitos - pode ser celular sem 9 ou fixo
            # Assume que é celular e adiciona 9
            ddd = clean_phone[:2]
            number = clean_phone[2:]
            formatted = f"55{ddd}9{number}"
            return True, formatted
        
        elif len(clean_phone) == 9 and clean_phone.startswith('9'):
            # Apenas o número sem DDD (assumir DDD 11 como padrão)
            formatted = f"5511{clean_phone}"
            return True, formatted
        
        elif len(clean_phone) == 8:
            # Telefone fixo sem DDD (assumir DDD 11)
            formatted = f"5511{clean_phone}"
            return True, formatted
        
        else:
            logger.error(f"Formato de número não reconhecido: {clean_phone}")
            return False, ""
    
    async def initiate_support_call(self, customer_phone: str, customer_name: str = "Cliente") -> bool:
        """Inicia ligação de suporte para o cliente"""
        
        logger.info(f"Tentando iniciar ligação para {customer_phone}")
        
        # Valida número do cliente
        is_valid, formatted_phone = self.validate_phone_number(customer_phone)
        if not is_valid:
            logger.error(f"Número inválido para ligação: {customer_phone}")
            return False
        
        logger.info(f"Número validado: {customer_phone} → {formatted_phone}")
        
        try:
            # Mensagem simplificada para evitar problemas de encoding
            robot_message = f"""🤖 SUPORTE AUTOMÁTICO

Olá {customer_name}!

Chamada automática do nosso suporte.

Nossa equipe entrará em contato em breve.

Horário: Segunda a Sexta 08:00-18:00

Para falar conosco digite: ATENDENTE

Aguarde nosso contato!"""

            logger.info(f"Enviando mensagem para {formatted_phone}")
            
            # Envia mensagem via WhatsApp que funciona como "ligação"
            success = await self._send_call_message(formatted_phone, robot_message)
            
            logger.info(f"Resultado do envio: {success}")
            
            if success:
                # Notifica administradores sobre a solicitação (mensagem simplificada)
                admin_message = f"""📞 SOLICITAÇÃO DE LIGAÇÃO

Cliente: {customer_name}
Número: {formatted_phone}
Horário: {self._get_current_time()}

Robô enviou mensagem.
Cliente aguarda contato."""

                # Envia para os admins
                await self._notify_admins(admin_message)
                
                logger.info(f"Ligação iniciada com sucesso para {formatted_phone}")
                return True
            else:
                logger.error(f"Falha ao enviar mensagem para {formatted_phone}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar ligação para {customer_phone}: {e}")
            return False
    
    async def _send_call_message(self, phone: str, message: str) -> bool:
        """Envia mensagem via WhatsApp (simula ligação)"""
        try:
            # Codifica a mensagem para URL
            encoded_message = urllib.parse.quote(message)
            
            # Monta a URL da API
            url = f"{self.call_url}?phone={phone}&text={encoded_message}&apikey={self.call_api_key}"
            
            logger.info(f"Enviando para: {phone} com API key: {self.call_api_key}")
            logger.info(f"URL: {url[:100]}...")  # Log parcial da URL
            
            # Envia a requisição
            response = requests.get(url, timeout=15)
            
            logger.info(f"Status da resposta: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"Mensagem de ligação enviada com sucesso para {phone}")
                return True
            else:
                logger.error(f"Erro ao enviar ligação para {phone}: {response.status_code}")
                logger.error(f"Resposta: {response.text[:200]}...")  # Log parcial da resposta
                
                # Para APIs CallMeBot, mesmo com erro 203, a mensagem pode ser enviada
                if response.status_code == 203:
                    logger.info("Status 203 - mensagem pode ter sido enviada mesmo assim")
                    return True
                
                return False
                
        except requests.RequestException as e:
            logger.error(f"Erro na requisição de ligação para {phone}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado na ligação para {phone}: {e}")
            return False
    
    async def _notify_admins(self, message: str) -> bool:
        """Notifica administradores sobre solicitação de ligação"""
        try:
            # Envia para o telefone principal do admin
            encoded_message = urllib.parse.quote(message)
            url = f"{self.call_url}?phone={self.call_phone}&text={encoded_message}&apikey={self.call_api_key}"
            
            response = requests.get(url, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erro ao notificar admins: {e}")
            return False
    
    async def send_followup_message(self, phone: str, customer_name: str) -> bool:
        """Envia mensagem de follow-up após alguns minutos"""
        followup_message = f"""🔄 FOLLOW-UP AUTOMÁTICO

Olá {customer_name}!

Nossa equipe ainda não conseguiu te contactar.

📞 Opções disponíveis:

1️⃣ AGUARDAR CONTATO
   Nossa equipe ligará em breve

2️⃣ CHAT WHATSAPP  
   Digite: QUERO CHAT

3️⃣ REAGENDAR
   Digite: REAGENDAR

4️⃣ URGENTE
   Digite: URGENTE

Escolha uma opção digitando o número ou texto correspondente."""

        return await self._send_call_message(phone, followup_message)
    
    def _get_current_time(self) -> str:
        """Retorna o horário atual formatado"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    def test_call_system(self) -> bool:
        """Testa o sistema de ligação"""
        try:
            test_message = "🧪 Teste do sistema de ligação automática - Funcionando!"
            url = f"{self.call_url}?phone={self.call_phone}&text={urllib.parse.quote(test_message)}&apikey={self.call_api_key}"
            
            response = requests.get(url, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erro no teste do sistema de ligação: {e}")
            return False

# Instância global do sistema de ligação
call_system = None

def initialize_call_system(call_phone: str, call_api_key: str):
    """Inicializa o sistema de ligação"""
    global call_system
    if call_phone and call_api_key:
        call_system = WhatsAppCallSystem(call_phone, call_api_key)
    return call_system