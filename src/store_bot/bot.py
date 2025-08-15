#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, InlineQueryHandler
from telegram.constants import ParseMode

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from database.models import Database
from utils.payment_system import PaymentSystem, ManualPaymentSystem
from store_bot.handlers import StoreHandlers

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class StoreBot:
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
        self.handlers = StoreHandlers(self.db, self.payment_system, self.manual_payment)
        
        # Cria aplicação
        if not settings.STORE_BOT_TOKEN:
            raise ValueError("Token do bot da loja não configurado")
        
        self.application = Application.builder().token(settings.STORE_BOT_TOKEN).build()
        
        # Registra handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configura todos os handlers do bot"""
        
        # Comandos
        self.application.add_handler(CommandHandler("start", self.handlers.start_command))
        self.application.add_handler(CommandHandler("pix", self.handlers.pix_command))
        self.application.add_handler(CommandHandler("id", self.handlers.id_command))
        self.application.add_handler(CommandHandler("afiliados", self.handlers.afiliados_command))
        self.application.add_handler(CommandHandler("historico", self.historico_command))
        self.application.add_handler(CommandHandler("ranking", self.ranking_command))
        self.application.add_handler(CommandHandler("alertas", self.alertas_command))
        
        # Callbacks
        self.application.add_handler(CallbackQueryHandler(self.handlers.handle_callback))
        
        # Mensagens de texto
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handlers.handle_text_input
            )
        )
        
        # Inline queries para pesquisa
        self.application.add_handler(InlineQueryHandler(self.handle_inline_query))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def historico_command(self, update: Update, context):
        """Comando /historico"""
        user_id = update.effective_user.id
        user = self.db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ Usuário não encontrado.")
            return
        
        # Busca histórico de compras
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.name, pu.amount, pu.purchase_date 
            FROM purchases pu
            JOIN products p ON pu.product_id = p.id
            WHERE pu.user_id = ?
            ORDER BY pu.purchase_date DESC
            LIMIT 50
        ''', (user_id,))
        
        purchases = cursor.fetchall()
        
        # Busca histórico de recargas
        cursor.execute('''
            SELECT amount, created_date
            FROM transactions
            WHERE user_id = ? AND transaction_type = 'recharge' AND status = 'completed'
            ORDER BY created_date DESC
            LIMIT 50
        ''', (user_id,))
        
        recharges = cursor.fetchall()
        conn.close()
        
        # Gera arquivo de histórico
        bot_info = await context.bot.get_me()
        history_content = f"""HISTORICO DETALHADO
@{bot_info.username}
_______________________

COMPRAS:
"""
        
        if purchases:
            for purchase in purchases:
                history_content += f"- {purchase[0]} | R$ {purchase[1]:.2f} | {purchase[2]}\n"
        else:
            history_content += "Nenhuma compra realizada.\n"
        
        history_content += "\n_______________________\n\nPAGAMENTOS:\n"
        
        if recharges:
            for recharge in recharges:
                history_content += f"- R$ {recharge[0]:.2f} | {recharge[1]}\n"
        else:
            history_content += "Nenhuma recarga realizada.\n"
        
        # Salva arquivo temporário
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(history_content)
            temp_path = f.name
        
        try:
            # Envia arquivo
            with open(temp_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=f"historico_{user_id}.txt",
                    caption="📊 Seu histórico detalhado"
                )
        finally:
            # Remove arquivo temporário
            os.unlink(temp_path)
    
    async def ranking_command(self, update: Update, context):
        """Comando /ranking"""
        await self.handlers.show_ranking_menu(update, context)
    
    async def alertas_command(self, update: Update, context):
        """Comando /alertas"""
        products = self.db.get_products()
        
        if not products:
            await update.message.reply_text("📦 Nenhum produto disponível para alertas.")
            return
        
        alerts_text = "🔔 **Sistema de Alertas**\n\nClique em um produto para ativar/desativar alertas:\n\n"
        
        keyboard = []
        for product in products:
            # Verifica se usuário tem alerta ativo para este produto
            user_id = update.effective_user.id
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT 1 FROM user_alerts WHERE user_id = ? AND product_id = ?',
                (user_id, product['id'])
            )
            has_alert = cursor.fetchone() is not None
            conn.close()
            
            status_icon = "🔔" if has_alert else "🔕"
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_icon} {product['name']}",
                    callback_data=f"alert_toggle_{product['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("↩️ Voltar", callback_data="back_main")])
        
        await update.message.reply_text(
            alerts_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_inline_query(self, update: Update, context):
        """Manipula consultas inline para pesquisa de produtos"""
        query = update.inline_query.query
        
        if not query:
            return
        
        # Busca produtos
        products = self.db.search_products(query)
        
        results = []
        for product in products[:10]:  # Limita a 10 resultados
            description = f"R$ {product['price']:.2f} - Estoque: {product['stock_count']}"
            if len(product['description']) > 0:
                description += f"\n{product['description'][:100]}..."
            
            results.append(
                InlineQueryResultArticle(
                    id=str(product['id']),
                    title=product['name'],
                    description=description,
                    input_message_content=InputTextMessageContent(
                        f"Produto: {product['name']}\nPreço: R$ {product['price']:.2f}"
                    )
                )
            )
        
        await update.inline_query.answer(results)
    
    async def error_handler(self, update: Update, context):
        """Manipula erros"""
        import traceback
        
        error_msg = f"Exception while handling an update: {context.error}"
        logger.error(error_msg)
        logger.error("Traceback:")
        logger.error(traceback.format_exc())
        
        # Tenta enviar mensagem de erro para o usuário
        try:
            if update and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Erro interno detectado:\n\n`{str(context.error)[:100]}...`\n\nTente novamente em alguns momentos.",
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de erro: {e}")
            
            # Fallback - tenta enviar sem markdown
            try:
                if update and update.effective_chat:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="❌ Ocorreu um erro interno. Tente novamente."
                    )
            except:
                pass
    
    async def send_stock_alert(self, product_name: str):
        """Envia alerta de estoque abastecido"""
        # Busca usuários com alerta ativo para este produto
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT u.user_id 
            FROM users u
            JOIN user_alerts ua ON u.user_id = ua.user_id
            JOIN products p ON ua.product_id = p.id
            WHERE p.name = ?
        ''', (product_name,))
        
        users_to_notify = cursor.fetchall()
        conn.close()
        
        # Envia notificação
        alert_message = f"🤖 **{product_name.upper()} ABASTECIDO NO BOT**"
        
        for user_row in users_to_notify:
            try:
                await self.application.bot.send_message(
                    chat_id=user_row[0],
                    text=alert_message,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Erro ao enviar alerta para {user_row[0]}: {e}")
    
    async def run(self):
        """Executa o bot de forma async"""
        logger.info("🛒 Bot da loja iniciando...")
        
        # Verifica configurações essenciais
        if not os.path.exists(os.path.dirname(settings.DATABASE_PATH)):
            os.makedirs(os.path.dirname(settings.DATABASE_PATH))
        
        # Cria tabela de alertas se não existir
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_alerts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (product_id) REFERENCES products (id),
                UNIQUE(user_id, product_id)
            )
        ''')
        conn.commit()
        conn.close()
        
        # Inicia o bot de forma async
        try:
            async with self.application:
                await self.application.start()
                await self.application.updater.start_polling()
                
                # Mantém rodando
                import asyncio
                await asyncio.Event().wait()
                
        except KeyboardInterrupt:
            logger.info("🛑 Bot da loja parado pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro crítico: {e}")
            raise

def main():
    """Função principal"""
    try:
        bot = StoreBot()
        bot.run()
    except Exception as e:
        logger.error(f"Erro ao iniciar bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()