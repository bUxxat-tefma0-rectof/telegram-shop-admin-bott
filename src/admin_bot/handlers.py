import os
import sys
import logging
from datetime import datetime
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Database
from config.settings import settings
from utils.payment_system import PaymentSystem, ManualPaymentSystem
from admin_bot.keyboards import AdminKeyboards

# Estados da conversa
WAITING_ADMIN_ID, WAITING_ADMIN_REMOVE, WAITING_SUPPORT_LINK, WAITING_SEPARATOR = range(4)
WAITING_LOG_DEST, WAITING_POINTS_RECHARGE, WAITING_MIN_POINTS, WAITING_MULTIPLIER = range(4, 8)
WAITING_REGISTRATION_BONUS, WAITING_BROADCAST, WAITING_USER_SEARCH, WAITING_MP_TOKEN = range(8, 12)
WAITING_MIN_DEPOSIT, WAITING_MAX_DEPOSIT, WAITING_EXPIRATION_TIME, WAITING_DEPOSIT_BONUS = range(12, 16)
WAITING_MIN_FOR_BONUS, WAITING_LOGIN_DATA, WAITING_REMOVE_LOGIN, WAITING_PLATFORM_REMOVE = range(16, 20)
WAITING_SERVICE_PRICE, WAITING_ALL_PRICES, WAITING_ADD_BALANCE = range(20, 23)

class AdminHandlers:
    def __init__(self, db: Database, payment_system: PaymentSystem, manual_payment: ManualPaymentSystem):
        self.db = db
        self.payment_system = payment_system
        self.manual_payment = manual_payment
        self.user_states = {}
    
    def is_admin(self, user_id: int) -> bool:
        """Verifica se o usuário é admin"""
        return user_id in [settings.ADMIN_USER_ID, settings.OWNER_USER_ID] or self.db.get_setting(f"admin_{user_id}") == "true"
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start para admins"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Você não tem permissão para usar este bot.")
            return
        
        # Registra ou atualiza usuário
        user = self.db.get_user(user_id)
        if not user:
            self.db.create_user(
                user_id=user_id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name
            )
            user = self.db.get_user(user_id)
        
        # Busca estatísticas para área de afiliados
        affiliate_stats = self.db.get_affiliate_stats(user_id)
        
        welcome_text = settings.MESSAGES['welcome_admin'].format(
            purchases=user['total_purchases'],
            giftcards=0,  # Implementar busca de gift cards
            affiliate_link=affiliate_stats.get('affiliate_link', 'N/A'),
            affiliates_count=affiliate_stats.get('affiliates_count', 0),
            points=affiliate_stats.get('points', 0)
        )
        
        # Adiciona imagem se configurada
        image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSltpwF6kTey6ImHK0Z76OBq2AmdNgMsS7irFzm7Xv4Ji9whMxq-eD6PO2Y&s=10"
        
        await update.message.reply_photo(
            photo=image_url,
            caption=welcome_text,
            reply_markup=AdminKeyboards.main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Define menu lateral
        await context.bot.set_chat_menu_button(
            chat_id=user_id,
            menu_button=None
        )
        
        await update.message.reply_text(
            "Menu lateral ativo:",
            reply_markup=AdminKeyboards.admin_menu_lateral()
        )
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /admin - Dashboard administrativo"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
            return
        
        # Busca estatísticas
        revenue_stats = self.db.get_revenue_stats()
        sales_stats = self.db.get_sales_stats()
        user_stats = self.db.get_user_stats()
        
        bot_info = await context.bot.get_me()
        
        dashboard_text = settings.MESSAGES['admin_dashboard'].format(
            bot_username=bot_info.username,
            expiration="Sem vencimento",  # Implementar sistema de vencimento
            vip_status="Ativo",
            version="1.0.0",
            total_users=user_stats['total_users'],
            total_revenue=revenue_stats['total_revenue'],
            monthly_revenue=revenue_stats['monthly_revenue'],
            daily_revenue=revenue_stats['daily_revenue'],
            total_sales=sales_stats['total_sales'],
            daily_sales=sales_stats['daily_sales']
        )
        
        await update.message.reply_text(
            dashboard_text,
            reply_markup=AdminKeyboards.admin_dashboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manipula todos os callbacks do bot admin"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if not self.is_admin(user_id):
            await query.edit_message_text("❌ Você não tem permissão para usar esta função.")
            return
        
        data = query.data
        
        # Navegação principal
        if data == "admin_dashboard":
            await self.show_admin_dashboard(query, context)
        elif data == "admin_config":
            await self.show_config_menu(query, context)
        elif data == "admin_back_main":
            await self.back_to_main_menu(query, context)
        
        # Configurações gerais
        elif data == "config_general":
            await self.show_general_config(query, context)
        elif data == "config_admins":
            await self.show_admin_management(query, context)
        elif data == "config_affiliates":
            await self.show_affiliate_config(query, context)
        elif data == "config_users":
            await self.show_user_config(query, context)
        elif data == "config_pix":
            await self.show_pix_config(query, context)
        elif data == "config_logins":
            await self.show_login_config(query, context)
        elif data == "config_search":
            await self.show_search_config(query, context)
        
        # Ações específicas
        elif data == "toggle_maintenance":
            await self.toggle_maintenance(query, context)
        elif data == "restart_bot":
            await self.restart_bot(query, context)
        elif data == "change_support":
            await self.request_support_change(query, context)
        elif data == "change_separator":
            await self.request_separator_change(query, context)
        elif data == "change_log_dest":
            await self.request_log_dest_change(query, context)
        
        # Gestão de admins
        elif data == "add_admin":
            await self.request_admin_add(query, context)
        elif data == "remove_admin":
            await self.request_admin_remove(query, context)
        elif data == "list_admins":
            await self.list_admins(query, context)
        
        # Configuração de afiliados
        elif data == "toggle_affiliate_system":
            await self.toggle_affiliate_system(query, context)
        elif data == "set_points_per_recharge":
            await self.request_points_per_recharge(query, context)
        elif data == "set_min_points":
            await self.request_min_points(query, context)
        elif data == "set_multiplier":
            await self.request_multiplier(query, context)
        
        # Configuração de usuários
        elif data == "broadcast_all":
            await self.request_broadcast(query, context)
        elif data == "search_user":
            await self.request_user_search(query, context)
        elif data == "set_registration_bonus":
            await self.request_registration_bonus(query, context)
        
        # Configuração PIX
        elif data == "set_pix_manual":
            await self.set_pix_mode(query, context, "manual")
        elif data == "set_pix_auto":
            await self.set_pix_mode(query, context, "auto")
        elif data == "change_mp_token":
            await self.request_mp_token(query, context)
        elif data == "change_min_deposit":
            await self.request_min_deposit(query, context)
        elif data == "change_max_deposit":
            await self.request_max_deposit(query, context)
        elif data == "change_expiration_time":
            await self.request_expiration_time(query, context)
        elif data == "change_deposit_bonus":
            await self.request_deposit_bonus(query, context)
        elif data == "change_min_for_bonus":
            await self.request_min_for_bonus(query, context)
        
        # Configuração de logins
        elif data == "add_login":
            await self.request_login_data(query, context)
        elif data == "remove_login":
            await self.request_remove_login(query, context)
        elif data == "remove_by_platform":
            await self.request_platform_remove(query, context)
        elif data == "detailed_stock":
            await self.show_detailed_stock(query, context)
        elif data == "clear_stock":
            await self.clear_stock(query, context)
        elif data == "change_service_price":
            await self.request_service_price(query, context)
        elif data == "change_all_prices":
            await self.request_all_prices(query, context)
        
        # Outros
        elif data == "admin_add_balance":
            await self.request_add_balance(query, context)
        elif data == "admin_logins":
            await self.show_admin_products(query, context)
        elif data == "admin_profile":
            await self.show_admin_profile(query, context)
        elif data == "admin_search":
            await self.show_admin_search(query, context)
        elif data.startswith("buy_product_"):
            product_id = int(data.split("_")[2])
            await self.process_admin_purchase(query, context, product_id)
    
    async def show_admin_dashboard(self, query, context):
        """Mostra dashboard administrativo"""
        revenue_stats = self.db.get_revenue_stats()
        sales_stats = self.db.get_sales_stats()
        user_stats = self.db.get_user_stats()
        
        bot_info = await context.bot.get_me()
        
        dashboard_text = settings.MESSAGES['admin_dashboard'].format(
            bot_username=bot_info.username,
            expiration="Sem vencimento",
            vip_status="Ativo",
            version="1.0.0",
            total_users=user_stats['total_users'],
            total_revenue=revenue_stats['total_revenue'],
            monthly_revenue=revenue_stats['monthly_revenue'],
            daily_revenue=revenue_stats['daily_revenue'],
            total_sales=sales_stats['total_sales'],
            daily_sales=sales_stats['daily_sales']
        )
        
        await query.edit_message_text(
            dashboard_text,
            reply_markup=AdminKeyboards.admin_dashboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_config_menu(self, query, context):
        """Mostra menu de configurações"""
        # Busca informações de admins
        admin_count = len([k for k in self.db.get_setting("admin_list") or "".split(",") if k])
        owner_info = self.db.get_user(settings.OWNER_USER_ID)
        
        config_text = f"""🔧 **MENU DE CONFIGURAÇÕES DO BOT**

👮‍♀️ **Admin:** {admin_count}
💼 **Dono:** {owner_info['first_name'] if owner_info else 'N/A'}"""
        
        await query.edit_message_text(
            config_text,
            reply_markup=AdminKeyboards.admin_config_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_general_config(self, query, context):
        """Mostra configurações gerais"""
        log_dest = self.db.get_setting("log_destination") or settings.LOG_DESTINATION
        support_link = self.db.get_setting("support_link") or settings.SUPPORT_LINK
        separator = self.db.get_setting("separator") or settings.SEPARATOR
        maintenance = self.db.get_setting("maintenance_mode") == "true"
        
        config_text = f"""Use os botões abaixo para configurar seu bot:
📭 **DESTINO DAS LOG'S:** {log_dest}
👤 **LINK DO SUPORTE ATUAL:** {support_link}
✂️ **SEPARADOR:** {separator}

separador é o caractér que separa as informações quando você vai alterar algo no bot. Ele é muito importante, então escolha um caractér que você não usa com frequencia para que o bot não fique confuso na hora de separar

**EX DO SEPARADOR EM AÇÃO:**
NOME{separator}VALOR"""
        
        await query.edit_message_text(
            config_text,
            reply_markup=AdminKeyboards.general_config(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def toggle_maintenance(self, query, context):
        """Alterna modo manutenção"""
        current_mode = self.db.get_setting("maintenance_mode") == "true"
        new_mode = not current_mode
        
        self.db.set_setting("maintenance_mode", str(new_mode).lower())
        
        status = "ativado" if new_mode else "desativado"
        await query.edit_message_text(
            f"🔧 Modo manutenção {status}!",
            reply_markup=AdminKeyboards.maintenance_toggle(new_mode)
        )
    
    async def show_admin_products(self, query, context):
        """Mostra produtos disponíveis para admin"""
        products = self.db.get_products()
        
        if not products:
            await query.edit_message_text(
                "📦 Nenhum produto cadastrado.",
                reply_markup=AdminKeyboards.back_keyboard("admin_back_main")
            )
            return
        
        text = "🎟️ **Logins Premium | Acesso Exclusivo**\n\n🏦 **Carteira**\n💸 **Saldo Atual:** R$∞\n\n"
        
        keyboard = []
        for product in products:
            text += f"**{product['name']}** - R$ {product['price']:.2f}\n"
            keyboard.append([
                InlineKeyboardButton(
                    f"{product['name']} - R$ {product['price']:.2f}",
                    callback_data=f"admin_product_{product['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_back_main")])
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Métodos para inputs do usuário
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manipula entradas de texto baseadas no estado do usuário"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if not self.is_admin(user_id):
            return
        
        user_state = self.user_states.get(user_id)
        
        if user_state == WAITING_SUPPORT_LINK:
            self.db.set_setting("support_link", text)
            await update.message.reply_text(
                f"✅ Link de suporte atualizado para: {text}",
                reply_markup=AdminKeyboards.back_keyboard("config_general")
            )
            del self.user_states[user_id]
        
        elif user_state == WAITING_SEPARATOR:
            self.db.set_setting("separator", text)
            await update.message.reply_text(
                f"✅ Separador atualizado para: {text}",
                reply_markup=AdminKeyboards.back_keyboard("config_general")
            )
            del self.user_states[user_id]
        
        elif user_state == WAITING_LOG_DEST:
            self.db.set_setting("log_destination", text)
            await update.message.reply_text(
                f"✅ Destino de logs atualizado para: {text}",
                reply_markup=AdminKeyboards.back_keyboard("config_general")
            )
            del self.user_states[user_id]
        
        elif user_state == WAITING_ADMIN_ID:
            try:
                admin_id = int(text)
                self.db.set_setting(f"admin_{admin_id}", "true")
                
                # Atualiza lista de admins
                admin_list = self.db.get_setting("admin_list") or ""
                if admin_list:
                    admin_list += f",{admin_id}"
                else:
                    admin_list = str(admin_id)
                self.db.set_setting("admin_list", admin_list)
                
                await update.message.reply_text(
                    f"✅ Administrador {admin_id} adicionado com sucesso!",
                    reply_markup=AdminKeyboards.back_keyboard("config_admins")
                )
                del self.user_states[user_id]
            except ValueError:
                await update.message.reply_text("❌ ID inválido. Digite apenas números.")
        
        elif user_state == WAITING_BROADCAST:
            await self.send_broadcast(update, context, text)
            del self.user_states[user_id]
        
        elif user_state == WAITING_LOGIN_DATA:
            await self.process_login_data(update, context, text)
            del self.user_states[user_id]
        
        # Adicionar outros estados conforme necessário
    
    async def request_support_change(self, query, context):
        """Solicita novo link de suporte"""
        self.user_states[query.from_user.id] = WAITING_SUPPORT_LINK
        await query.edit_message_text(
            "🎧 Envie o novo link de suporte:",
            reply_markup=AdminKeyboards.back_keyboard("config_general")
        )
    
    async def request_separator_change(self, query, context):
        """Solicita novo separador"""
        self.user_states[query.from_user.id] = WAITING_SEPARATOR
        await query.edit_message_text(
            "✂️ Envie o novo separador:",
            reply_markup=AdminKeyboards.back_keyboard("config_general")
        )
    
    async def request_admin_add(self, query, context):
        """Solicita ID do novo admin"""
        self.user_states[query.from_user.id] = WAITING_ADMIN_ID
        await query.edit_message_text(
            "➕ Digite o ID do Telegram do novo administrador:",
            reply_markup=AdminKeyboards.back_keyboard("config_admins")
        )
    
    async def request_broadcast(self, query, context):
        """Solicita mensagem para transmissão"""
        self.user_states[query.from_user.id] = WAITING_BROADCAST
        await query.edit_message_text(
            "📭 Digite a mensagem que deseja transmitir para todos os usuários:",
            reply_markup=AdminKeyboards.back_keyboard("config_users")
        )
    
    async def send_broadcast(self, update, context, message):
        """Envia mensagem para todos os usuários"""
        # Implementar envio em massa
        # Por agora, apenas confirma
        await update.message.reply_text(
            f"✅ Mensagem transmitida com sucesso!\n\nMensagem: {message}",
            reply_markup=AdminKeyboards.back_keyboard("config_users")
        )
    
    async def request_login_data(self, query, context):
        """Solicita dados de login para adicionar ao estoque"""
        self.user_states[query.from_user.id] = WAITING_LOGIN_DATA
        separator = self.db.get_setting("separator") or settings.SEPARATOR
        
        await query.edit_message_text(
            f"""📮 **ADICIONAR LOGINS**

Envie os logins no formato:
**NOME{separator}VALOR{separator}DESCRICAO{separator}EMAIL{separator}SENHA{separator}DURACAO**

Para abastecer mais de um login, envie desta mesma maneira um abaixo do outro, ou pulando linhas.""",
            reply_markup=AdminKeyboards.back_keyboard("config_logins"),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def process_login_data(self, update, context, text):
        """Processa dados de login recebidos"""
        separator = self.db.get_setting("separator") or settings.SEPARATOR
        lines = text.strip().split('\n')
        added_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(separator)
            if len(parts) >= 6:
                name, price, description, email, password, duration = parts[:6]
                
                try:
                    price = float(price)
                    duration = int(duration)
                    
                    # Cria ou busca produto
                    products = self.db.get_products()
                    product = next((p for p in products if p['name'].lower() == name.lower()), None)
                    
                    if not product:
                        product_id = self.db.create_product(name, price, description, duration)
                    else:
                        product_id = product['id']
                    
                    # Adiciona login ao estoque
                    if self.db.add_login_to_stock(product_id, email, password, ""):
                        added_count += 1
                        
                except (ValueError, IndexError):
                    continue
        
        await update.message.reply_text(
            f"✅ {added_count} logins adicionados ao estoque!",
            reply_markup=AdminKeyboards.back_keyboard("config_logins")
        )
    
    async def show_detailed_stock(self, query, context):
        """Mostra estoque detalhado"""
        products = self.db.get_products()
        
        if not products:
            await query.edit_message_text(
                "📦 Nenhum produto no estoque.",
                reply_markup=AdminKeyboards.back_keyboard("config_logins")
            )
            return
        
        stock_text = "📦 **ESTOQUE DETALHADO**\n\n"
        
        for product in products:
            stock_text += f"**{product['name']}**\n"
            stock_text += f"💰 Preço: R$ {product['price']:.2f}\n"
            stock_text += f"📦 Estoque: {product['stock_count']}\n"
            stock_text += f"🛒 Vendas: {product['total_sales']}\n\n"
        
        await query.edit_message_text(
            stock_text,
            reply_markup=AdminKeyboards.back_keyboard("config_logins"),
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Implementar métodos restantes conforme necessário...
    
    async def back_to_main_menu(self, query, context):
        """Volta ao menu principal"""
        user = self.db.get_user(query.from_user.id)
        affiliate_stats = self.db.get_affiliate_stats(query.from_user.id)
        
        welcome_text = settings.MESSAGES['welcome_admin'].format(
            purchases=user['total_purchases'],
            giftcards=0,
            affiliate_link=affiliate_stats.get('affiliate_link', 'N/A'),
            affiliates_count=affiliate_stats.get('affiliates_count', 0),
            points=affiliate_stats.get('points', 0)
        )
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=AdminKeyboards.main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )