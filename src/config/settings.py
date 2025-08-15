import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Bot Tokens
    ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN')
    STORE_BOT_TOKEN = os.getenv('STORE_BOT_TOKEN')
    
    # Mercado Pago
    MERCADO_PAGO_TOKEN = os.getenv('MERCADO_PAGO_TOKEN')
    
    # Admin Users
    ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', 0))
    OWNER_USER_ID = int(os.getenv('OWNER_USER_ID', 0))
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', './database/bot_database.db')
    
    # General Settings
    SUPPORT_LINK = os.getenv('SUPPORT_LINK', 'https://t.me/suporte')
    SEPARATOR = os.getenv('SEPARATOR', '===')
    LOG_DESTINATION = os.getenv('LOG_DESTINATION', '')
    
    # Sales Channel
    SALES_CHANNEL_ID = os.getenv('SALES_CHANNEL_ID', '')
    if SALES_CHANNEL_ID and not SALES_CHANNEL_ID.startswith('-'):
        SALES_CHANNEL_ID = f'-{SALES_CHANNEL_ID}'
    
    # Payment Settings
    MIN_DEPOSIT = float(os.getenv('MIN_DEPOSIT', 1.00))
    MAX_DEPOSIT = float(os.getenv('MAX_DEPOSIT', 1000.00))
    PIX_EXPIRATION_TIME = int(os.getenv('PIX_EXPIRATION_TIME', 30))
    DEPOSIT_BONUS = float(os.getenv('DEPOSIT_BONUS', 0))
    MIN_DEPOSIT_FOR_BONUS = float(os.getenv('MIN_DEPOSIT_FOR_BONUS', 50.00))
    
    # Affiliate Settings
    MIN_POINTS_TO_CONVERT = int(os.getenv('MIN_POINTS_TO_CONVERT', 400))
    POINTS_MULTIPLIER = float(os.getenv('POINTS_MULTIPLIER', 0.01))
    POINTS_PER_RECHARGE = int(os.getenv('POINTS_PER_RECHARGE', 10))
    AFFILIATE_SYSTEM_ENABLED = os.getenv('AFFILIATE_SYSTEM_ENABLED', 'true').lower() == 'true'
    
    # Registration Settings
    REGISTRATION_BONUS = float(os.getenv('REGISTRATION_BONUS', 0.00))
    
    # Maintenance Mode
    MAINTENANCE_MODE = os.getenv('MAINTENANCE_MODE', 'false').lower() == 'true'
    
    # WhatsApp CallMeBot API - Primeiro número
    WHATSAPP_PHONE = os.getenv('WHATSAPP_PHONE', '')
    WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY', '')
    
    # WhatsApp CallMeBot API - Segundo número
    WHATSAPP_PHONE_2 = os.getenv('WHATSAPP_PHONE_2', '')
    WHATSAPP_API_KEY_2 = os.getenv('WHATSAPP_API_KEY_2', '')
    
    # WhatsApp Call API - Sistema de ligação automática
    WHATSAPP_CALL_PHONE = os.getenv('WHATSAPP_CALL_PHONE', '')
    WHATSAPP_CALL_API_KEY = os.getenv('WHATSAPP_CALL_API_KEY', '')
    
    # Bot Messages
    MESSAGES = {
        'welcome_admin': """
🛒 Compras feitas: {purchases}
🎁 GiftCard's resgatados: {giftcards}

Área afiliados
🎗️Seu link de afiliado: {affiliate_link}
🎭 Quantidade de afiliados: {affiliates_count}
🎖️ Pontos de indicação: {points}
""",
        'welcome_store': """🥇 BEM-VINDO À NOSSA LOJA!

Descubra produtos com o melhor preço e qualidade!

👥 Grupo De Clientes: Em breve
👨‍💻 Suporte: {support_link}

ℹ️ Seus Dados:
🆔 ID: {user_id}  
💸 Saldo: R${balance:.2f}
🪪 Usuário: {username}""",
        'admin_dashboard': """
⚙️ DASHBOARD @{bot_username}
📅 Vencimento: {expiration}
👑 Vip: {vip_status}
🤖 Software version: {version}

📔 Métrica do business
📊 User: {total_users}
📈 Receita total: R$ {total_revenue:.2f}
🗓️ Receita mensal: R$ {monthly_revenue:.2f}
💠 Receita de hoje: R$ {daily_revenue:.2f}
🥇 Vendas total: {total_sales}
🏆 Vendas hoje: {daily_sales}

🔧 Use os botões abaixo para me configurar
""",
        'insufficient_balance': """
Saldo insuficiente! Faltam R$ {missing:.2f}
Faça uma recarga e tente novamente.
Seu saldo: R$ {balance:.2f}
""",
        'payment_generated': """
💰 Comprar Saldo com Pix Automático:

⏱️ Expira em: {expiration}
💵 Valor: R$ {amount:.2f}
✨ ID da Recarga: {payment_id}

🗞️ Atenção: Este código é válido para apenas um único pagamento.
Se você utilizá-lo mais de uma vez, o saldo adicional será perdido sem direito a reembolso.

💎 Pix Copia e Cola:
{pix_code}

💡 Dica: Clique no código acima para copiar.

🇧🇷 Após o pagamento, seu saldo será liberado instantaneamente.
"""
    }

settings = Settings()