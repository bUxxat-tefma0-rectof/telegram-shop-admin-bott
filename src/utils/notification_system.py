import logging
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from config.settings import settings

logger = logging.getLogger(__name__)

class NotificationSystem:
    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token)
        self.sales_channel_id = settings.SALES_CHANNEL_ID
    
    async def send_sale_notification(self, user_info: dict, product_info: dict, purchase_info: dict):
        """Envia notificação de venda para o canal"""
        if not self.sales_channel_id:
            logger.warning("Canal de vendas não configurado")
            return False
        
        try:
            # Monta a mensagem de venda
            sale_message = self._build_sale_message(user_info, product_info, purchase_info)
            
            # Envia para o canal
            await self.bot.send_message(
                chat_id=self.sales_channel_id,
                text=sale_message)
            
            logger.info(f"Notificação de venda enviada para o canal: {purchase_info['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de venda: {e}")
            return False
    
    def _build_sale_message(self, user_info: dict, product_info: dict, purchase_info: dict) -> str:
        """Constrói a mensagem de notificação de venda"""
        
        # Emoji para o produto baseado no nome
        product_emoji = self._get_product_emoji(product_info['name'])
        
        # Data/hora da venda
        sale_time = datetime.now().strftime("%d/%m/%Y às %H:%M")
        
        message = f"""🎉 **NOVA VENDA REALIZADA!** 🎉

{product_emoji} **Produto:** {product_info['name']}
💰 **Valor:** R$ {purchase_info['amount']:.2f}
🆔 **Cliente:** {user_info['first_name'] or 'Usuário'} (ID: {user_info['user_id']})
⏰ **Data/Hora:** {sale_time}
🔢 **ID da Compra:** #{purchase_info['id']}

📊 **Estatísticas do Produto:**
📦 **Estoque Restante:** {product_info['stock_count'] - 1}
🛒 **Total de Vendas:** {product_info['total_sales'] + 1}

🎯 **Loja João Store** | @Lojajoaostore_bot"""

        return message
    
    def _get_product_emoji(self, product_name: str) -> str:
        """Retorna emoji baseado no nome do produto"""
        product_name_lower = product_name.lower()
        
        emoji_map = {
            'netflix': '🎬',
            'spotify': '🎵',
            'amazon': '📦',
            'prime': '📺',
            'disney': '🏰',
            'globoplay': '📺',
            'youtube': '📹',
            'crunchyroll': '🎌',
            'hbo': '🎭',
            'max': '🎪',
            'paramount': '⭐',
            'apple': '🍎',
            'microsoft': '💻',
            'office': '📄',
            'canva': '🎨',
            'adobe': '🎨',
            'vpn': '🔒',
            'nordvpn': '🛡️',
            'minecraft': '⛏️',
            'steam': '🎮',
            'xbox': '🎮',
            'playstation': '🎮',
            'iptv': '📺',
            'telegram': '💬',
            'whatsapp': '💬',
            'tiktok': '🎵',
            'instagram': '📸',
            'facebook': '👥',
            'twitter': '🐦',
            'onlyfans': '🔞',
            'pornhub': '🔞',
            'chatgpt': '🤖',
            'midjourney': '🎨',
            'free fire': '🔫',
            'pubg': '🎯',
            'fortnite': '🏆',
            'roblox': '🎮',
            'mobile legends': '⚔️'
        }
        
        for keyword, emoji in emoji_map.items():
            if keyword in product_name_lower:
                return emoji
        
        return '🛍️'  # Emoji padrão
    
    async def send_recharge_notification(self, user_info: dict, amount: float, payment_method: str):
        """Envia notificação de recarga para o canal"""
        if not self.sales_channel_id:
            return False
        
        try:
            recharge_time = datetime.now().strftime("%d/%m/%Y às %H:%M")
            
            message = f"""💰 **NOVA RECARGA APROVADA!** 💰

💳 **Valor:** R$ {amount:.2f}
🆔 **Cliente:** {user_info['first_name'] or 'Usuário'} (ID: {user_info['user_id']})
💎 **Método:** {payment_method}
⏰ **Data/Hora:** {recharge_time}

🎯 **Loja João Store** | @Lojajoaostore_bot"""
            
            await self.bot.send_message(
                chat_id=self.sales_channel_id,
                text=message)
            
            logger.info(f"Notificação de recarga enviada para o canal: R$ {amount:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de recarga: {e}")
            return False
    
    async def send_new_user_notification(self, user_info: dict, referred_by: str = None):
        """Envia notificação de novo usuário para o canal"""
        if not self.sales_channel_id:
            return False
        
        try:
            register_time = datetime.now().strftime("%d/%m/%Y às %H:%M")
            
            message = f"""👋 **NOVO USUÁRIO REGISTRADO!** 👋

🆔 **Nome:** {user_info['first_name'] or 'Usuário'}
🔢 **ID:** {user_info['user_id']}
⏰ **Data/Hora:** {register_time}"""
            
            if referred_by:
                message += f"\n🎗️ **Indicado por:** {referred_by}"
            
            message += "\n\n🎯 **Loja João Store** | @Lojajoaostore_bot"
            
            await self.bot.send_message(
                chat_id=self.sales_channel_id,
                text=message)
            
            logger.info(f"Notificação de novo usuário enviada para o canal: {user_info['user_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de novo usuário: {e}")
            return False
    
    async def send_stock_alert(self, product_name: str, current_stock: int):
        """Envia alerta de estoque baixo"""
        if not self.sales_channel_id or current_stock > 5:
            return False
        
        try:
            alert_time = datetime.now().strftime("%d/%m/%Y às %H:%M")
            
            if current_stock == 0:
                message = f"""⚠️ **PRODUTO SEM ESTOQUE!** ⚠️

📦 **Produto:** {product_name}
📉 **Estoque:** {current_stock} unidades
⏰ **Data/Hora:** {alert_time}

🚨 **REABASTECER URGENTE!**

🎯 **Loja João Store** | @Admjoaostore_bot"""
            else:
                message = f"""⚠️ **ESTOQUE BAIXO!** ⚠️

📦 **Produto:** {product_name}
📉 **Estoque:** {current_stock} unidades restantes
⏰ **Data/Hora:** {alert_time}

💡 **Considere reabastecer em breve**

🎯 **Loja João Store** | @Admjoaostore_bot"""
            
            await self.bot.send_message(
                chat_id=self.sales_channel_id,
                text=message)
            
            logger.info(f"Alerta de estoque enviado para o canal: {product_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta de estoque: {e}")
            return False