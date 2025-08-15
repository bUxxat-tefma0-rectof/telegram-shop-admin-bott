#!/usr/bin/env python3
"""
Sistema de sincronização em tempo real entre admin e loja
"""

import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

class SyncSystem:
    """Sistema de sincronização entre bots"""
    
    def __init__(self, admin_bot=None, store_bot=None):
        self.admin_bot = admin_bot
        self.store_bot = store_bot
        self.sync_enabled = True
    
    def set_bots(self, admin_bot, store_bot):
        """Define as instâncias dos bots"""
        self.admin_bot = admin_bot
        self.store_bot = store_bot
    
    async def sync_setting_change(self, setting_name: str, new_value: Any):
        """Sincroniza mudança de configuração"""
        if not self.sync_enabled or not self.store_bot:
            return
        
        try:
            logger.info(f"Sincronizando configuração: {setting_name} = {new_value}")
            
            # Aqui podem ser adicionadas ações específicas de sincronização
            # Por exemplo, enviar notificações para admins da loja
            
            if setting_name == "support_link":
                await self.notify_support_change(new_value)
            elif setting_name == "maintenance_mode":
                await self.notify_maintenance_change(new_value)
            elif setting_name == "affiliate_system_enabled":
                await self.notify_affiliate_change(new_value)
            
        except Exception as e:
            logger.error(f"Erro na sincronização de {setting_name}: {e}")
    
    async def sync_product_change(self, action: str, product_data: dict):
        """Sincroniza mudanças em produtos"""
        if not self.sync_enabled or not self.store_bot:
            return
        
        try:
            logger.info(f"Sincronizando produto: {action} - {product_data}")
            
            # Aqui podem ser adicionadas ações específicas
            # Por exemplo, atualizar cache de produtos na loja
            
        except Exception as e:
            logger.error(f"Erro na sincronização de produto: {e}")
    
    async def sync_user_change(self, action: str, user_data: dict):
        """Sincroniza mudanças em usuários"""
        if not self.sync_enabled or not self.store_bot:
            return
        
        try:
            logger.info(f"Sincronizando usuário: {action} - {user_data}")
            
        except Exception as e:
            logger.error(f"Erro na sincronização de usuário: {e}")
    
    async def notify_support_change(self, new_support_link: str):
        """Notifica mudança no link de suporte"""
        logger.info(f"Link de suporte alterado: {new_support_link}")
        # A loja automaticamente pegará o novo link do banco de dados
    
    async def notify_maintenance_change(self, maintenance_mode: str):
        """Notifica mudança no modo manutenção"""
        logger.info(f"Modo manutenção: {maintenance_mode}")
        # A loja verificará o modo manutenção em cada callback
    
    async def notify_affiliate_change(self, enabled: str):
        """Notifica mudança no sistema de afiliados"""
        logger.info(f"Sistema de afiliados: {enabled}")
    
    def disable_sync(self):
        """Desabilita sincronização"""
        self.sync_enabled = False
        logger.info("Sincronização desabilitada")
    
    def enable_sync(self):
        """Habilita sincronização"""
        self.sync_enabled = True
        logger.info("Sincronização habilitada")

# Instância global do sistema de sincronização
sync_system = SyncSystem()