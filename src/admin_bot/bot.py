#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from database.models import Database
from utils.payment_system import PaymentSystem, ManualPaymentSystem
from admin_bot.handlers import AdminHandlers

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AdminBot:
    def __init__(self):
        # Inicializa banco de dados
        self.db = Database(settings.DATABASE_PATH)
        
        # Inicializa sistemas de pagamento
        if settings.MERCADO_PAGO_TOKEN:
            self.payment_system = PaymentSystem(settings.MERCADO_PAGO_TOKEN)
        else:
            self.payment_system = None
            logger.warning("Token do Mercado Pago não configurado")
        
        self.manual_payment = ManualPaymentSystem()
        
        # Inicializa handlers
        self.handlers = AdminHandlers(self.db, self.payment_system, self.manual_payment)
        
        # Cria aplicação
        if not settings.ADMIN_BOT_TOKEN:
            raise ValueError("Token do bot administrativo não configurado")
        
        self.application = Application.builder().token(settings.ADMIN_BOT_TOKEN).build()
        
        # Registra handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configura todos os handlers do bot"""
        
        # Comandos
        self.application.add_handler(CommandHandler("start", self.handlers.start_command))
        self.application.add_handler(CommandHandler("admin", self.handlers.admin_command))
        
        # Callbacks
        self.application.add_handler(CallbackQueryHandler(self.handlers.handle_callback))
        
        # Mensagens de texto (para inputs do usuário)
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handlers.handle_text_input
            )
        )
        
        # Mensagens laterais (botões do teclado)
        self.application.add_handler(
            MessageHandler(
                filters.Regex("^⚔️ Menu Inicial$"),
                self.handle_menu_inicial
            )
        )
        
        self.application.add_handler(
            MessageHandler(
                filters.Regex("^🗡️ Menu Administrativo$"),
                self.handle_menu_admin
            )
        )
        
        # Handler para fotos (para sistema de imagens)
        self.application.add_handler(
            MessageHandler(
                filters.PHOTO,
                self.handle_photo
            )
        )
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def handle_menu_inicial(self, update: Update, context):
        """Manipula clique no Menu Inicial"""
        await self.handlers.start_command(update, context)
    
    async def handle_menu_admin(self, update: Update, context):
        """Manipula clique no Menu Administrativo"""
        await self.handlers.admin_command(update, context)
    
    async def handle_photo(self, update: Update, context):
        """Manipula fotos enviadas (para configuração de imagens)"""
        user_id = update.effective_user.id
        
        if not self.handlers.is_admin(user_id):
            return
        
        # Verifica se está aguardando imagem para pesquisa
        user_state = self.handlers.user_states.get(user_id)
        
        if user_state and "WAITING_SEARCH_IMAGE" in str(user_state):
            # Salva imagem para pesquisa
            photo = update.message.photo[-1]  # Maior resolução
            
            # Salva no banco de dados
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO search_images (file_id, description) VALUES (?, ?)",
                (photo.file_id, "Imagem de pesquisa")
            )
            conn.commit()
            conn.close()
            
            await update.message.reply_text(
                "✅ Imagem adicionada ao sistema de pesquisa!",
                reply_markup=AdminKeyboards.back_keyboard("config_search")
            )
            
            del self.handlers.user_states[user_id]
    
    async def error_handler(self, update: Update, context):
        """Manipula erros"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Tenta enviar mensagem de erro para o usuário
        try:
            if update and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Ocorreu um erro interno. Tente novamente."
                )
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de erro: {e}")
    
    async def send_notification(self, message: str, chat_id: int = None):
        """Envia notificação para administradores"""
        if not chat_id:
            chat_id = settings.LOG_DESTINATION or settings.ADMIN_USER_ID
        
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=f"🔔 NOTIFICAÇÃO ADMIN\n\n{message}",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
    
    async def run(self):
        """Executa o bot de forma async"""
        logger.info("🤖 Bot administrativo iniciando...")
        
        # Verifica configurações essenciais
        if not os.path.exists(os.path.dirname(settings.DATABASE_PATH)):
            os.makedirs(os.path.dirname(settings.DATABASE_PATH))
        
        # Configura administradores padrão
        if settings.ADMIN_USER_ID:
            self.db.set_setting(f"admin_{settings.ADMIN_USER_ID}", "true")
        
        if settings.OWNER_USER_ID and settings.OWNER_USER_ID != settings.ADMIN_USER_ID:
            self.db.set_setting(f"admin_{settings.OWNER_USER_ID}", "true")
        
        # Inicia o bot de forma async
        try:
            async with self.application:
                await self.application.start()
                await self.application.updater.start_polling()
                
                # Mantém rodando
                import asyncio
                await asyncio.Event().wait()
                
        except KeyboardInterrupt:
            logger.info("🛑 Bot administrativo parado pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro crítico: {e}")
            raise

def main():
    """Função principal"""
    try:
        bot = AdminBot()
        bot.run()
    except Exception as e:
        logger.error(f"Erro ao iniciar bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()