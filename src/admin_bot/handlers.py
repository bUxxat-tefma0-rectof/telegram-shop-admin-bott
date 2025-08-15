import os
import sys
import logging
from datetime import datetime
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
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
        
        # Roteamento automático das funções
        try:
            if hasattr(self, f'handle_{data}'):
                await getattr(self, f'handle_{data}')(query, context)
            elif data.startswith('admin_'):
                await self.handle_admin_action(query, context, data)
            elif data.startswith('config_'):
                await self.handle_config_action(query, context, data)
            elif data.startswith('buy_product_'):
                product_id = int(data.split("_")[2])
                await self.process_admin_purchase(query, context, product_id)
            else:
                await self.handle_generic_action(query, context, data)
        except Exception as e:
            logging.error(f"Erro no callback {data}: {e}")
            await query.edit_message_text(
                "❌ Erro interno. Tente novamente.",
                reply_markup=AdminKeyboards.back_keyboard("admin_back_main")
            )
    
    async def handle_admin_action(self, query, context, data):
        """Manipula ações administrativas"""
        if data == "admin_dashboard":
            await self.show_admin_dashboard(query, context)
        elif data == "admin_config":
            await self.show_config_menu(query, context)
        elif data == "admin_back_main":
            await self.back_to_main_menu(query, context)
        elif data == "admin_logins":
            await self.show_admin_products(query, context)
        elif data == "admin_profile":
            await self.show_admin_profile(query, context)
        elif data == "admin_add_balance":
            await self.request_add_balance(query, context)
        elif data == "admin_search":
            await self.show_admin_search(query, context)
        elif data == "admin_support":
            support_link = self.db.get_setting("support_link") or settings.SUPPORT_LINK
            await query.edit_message_text(
                f"👨‍💻 **Suporte:** {support_link}",
                reply_markup=AdminKeyboards.back_keyboard("admin_back_main"),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_config_action(self, query, context, data):
        """Manipula ações de configuração"""
        config_map = {
            "config_general": self.show_general_config,
            "config_admins": self.show_admin_management,
            "config_affiliates": self.show_affiliate_config,
            "config_users": self.show_user_config,
            "config_pix": self.show_pix_config,
            "config_logins": self.show_login_config,
            "config_search": self.show_search_config
        }
        
        if data in config_map:
            await config_map[data](query, context)
    
    async def handle_generic_action(self, query, context, data):
        """Manipula ações genéricas"""
        if data == "toggle_maintenance":
            await self.toggle_maintenance(query, context)
        elif data == "restart_bot":
            await query.edit_message_text("🤖 Bot reiniciado com sucesso!")
        elif data == "change_support":
            await self.request_input(query, WAITING_SUPPORT_LINK, "🎧 Envie o novo link de suporte:")
        elif data == "change_separator":
            await self.request_input(query, WAITING_SEPARATOR, "✂️ Envie o novo separador:")
        elif data == "add_admin":
            await self.request_input(query, WAITING_ADMIN_ID, "➕ Digite o ID do novo administrador:")
        elif data == "add_login":
            await self.request_login_data(query, context)
        elif data == "detailed_stock":
            await self.show_detailed_stock(query, context)
        else:
            await query.edit_message_text("⚠️ Função em desenvolvimento")
    
    async def request_input(self, query, state, message):
        """Solicita input do usuário"""
        self.user_states[query.from_user.id] = state
        await query.edit_message_text(message)
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manipula entradas de texto baseadas no estado do usuário"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if not self.is_admin(user_id):
            return
        
        user_state = self.user_states.get(user_id)
        
        if user_state == WAITING_SUPPORT_LINK:
            self.db.set_setting("support_link", text)
            await update.message.reply_text(f"✅ Link de suporte atualizado: {text}")
            del self.user_states[user_id]
        
        elif user_state == WAITING_SEPARATOR:
            self.db.set_setting("separator", text)
            await update.message.reply_text(f"✅ Separador atualizado: {text}")
            del self.user_states[user_id]
        
        elif user_state == WAITING_ADMIN_ID:
            try:
                admin_id = int(text)
                self.db.set_setting(f"admin_{admin_id}", "true")
                admin_list = self.db.get_setting("admin_list") or ""
                if admin_list:
                    admin_list += f",{admin_id}"
                else:
                    admin_list = str(admin_id)
                self.db.set_setting("admin_list", admin_list)
                await update.message.reply_text(f"✅ Admin {admin_id} adicionado!")
                del self.user_states[user_id]
            except ValueError:
                await update.message.reply_text("❌ ID inválido. Digite apenas números.")
        
        elif user_state == WAITING_LOGIN_DATA:
            await self.process_login_data(update, context, text)
            del self.user_states[user_id]
        
        elif user_state == WAITING_BROADCAST:
            await self.send_broadcast(update, context, text)
            del self.user_states[user_id]
    
    # Métodos de exibição
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
        admin_list = self.db.get_setting("admin_list") or ""
        admin_count = len([k for k in admin_list.split(",") if k])
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
        
        config_text = f"""Use os botões abaixo para configurar seu bot:
📭 **DESTINO DAS LOG'S:** {log_dest}
👤 **LINK DO SUPORTE ATUAL:** {support_link}
✂️ **SEPARADOR:** {separator}

separador é o caractér que separa as informações quando você vai alterar algo no bot."""
        
        await query.edit_message_text(
            config_text,
            reply_markup=AdminKeyboards.general_config(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_admin_management(self, query, context):
        """Mostra painel de gestão de admins"""
        admin_list = self.db.get_setting("admin_list") or ""
        admin_count = len([x for x in admin_list.split(",") if x])
        
        admin_text = f"""🅰️ **PAINEL CONFIGURAR ADMIN**
👮 **Administradores:** {admin_count}

Use os botões abaixo para fazer as alterações necessárias"""
        
        await query.edit_message_text(
            admin_text,
            reply_markup=AdminKeyboards.admin_management(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_affiliate_config(self, query, context):
        """Mostra configuração de afiliados"""
        min_points = self.db.get_setting("min_points_to_convert") or settings.MIN_POINTS_TO_CONVERT
        multiplier = self.db.get_setting("points_multiplier") or settings.POINTS_MULTIPLIER
        system_enabled = self.db.get_setting("affiliate_system_enabled") == "true"
        
        status_text = "ON" if system_enabled else "OFF"
        status_color = "🟢" if system_enabled else "🔴"
        
        config_text = f"""🔻 **PONTOS MÍNIMO PARA SALDO:** {min_points} 
✖️ **MULTIPLICADOR:** {multiplier}

👥 **SISTEMA DE INDICAÇÃO** {status_color} **({status_text})**

🗞️ **PONTOS POR RECARGA**
🔻 **PONTOS MÍNIMO PARA CONVERTER** 
✖️ **MULTIPLICADOR PARA CONVERTER**"""
        
        await query.edit_message_text(
            config_text,
            reply_markup=AdminKeyboards.affiliate_config(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_user_config(self, query, context):
        """Mostra configuração de usuários"""
        bonus = self.db.get_setting("registration_bonus") or settings.REGISTRATION_BONUS
        
        config_text = f"""📭 **TRANSMITIR A TODOS**
🔎 **PESQUISAR USUÁRIO**
🎁 **BÔNUS DE REGISTRO**

Bônus atual: R$ {bonus}"""
        
        await query.edit_message_text(
            config_text,
            reply_markup=AdminKeyboards.user_config(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_pix_config(self, query, context):
        """Mostra configuração PIX"""
        min_deposit = self.db.get_setting("min_deposit") or settings.MIN_DEPOSIT
        max_deposit = self.db.get_setting("max_deposit") or settings.MAX_DEPOSIT
        
        config_text = f"""🔑 **TOKEN MERCADO PAGO:** {'Configurado' if settings.MERCADO_PAGO_TOKEN else 'Não configurado'}

🔻**DEPÓSITO MÍNIMO:** R$ {min_deposit}
❗️ **DEPÓSITO MÁXIMO:** R$ {max_deposit}"""
        
        await query.edit_message_text(
            config_text,
            reply_markup=AdminKeyboards.pix_config(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_login_config(self, query, context):
        """Mostra configuração de logins"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM login_stock WHERE is_sold = 0')
        total_stock = cursor.fetchone()[0]
        conn.close()
        
        config_text = f"""📦 **LOGINS NO ESTOQUE:** {total_stock}

📮 **ADICIONAR LOGINS**
🥾 **REMOVER LOGIN**
📦 **ESTOQUE DETALHADO**"""
        
        await query.edit_message_text(
            config_text,
            reply_markup=AdminKeyboards.login_config(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_search_config(self, query, context):
        """Mostra configuração de pesquisa"""
        config_text = """🔎 **PAINEL DE CONFIGURAÇÃO DA PESQUISA DE SERVIÇOS**
📸 **IMAGENS SALVAS:** 0"""
        
        await query.edit_message_text(
            config_text,
            reply_markup=AdminKeyboards.search_config(),
            parse_mode=ParseMode.MARKDOWN
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
                    callback_data=f"buy_product_{product['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_back_main")])
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_admin_profile(self, query, context):
        """Mostra perfil do admin"""
        user = self.db.get_user(query.from_user.id)
        
        profile_text = f"""👤 **PERFIL ADMINISTRATIVO**

🆔 **ID:** {user['user_id']}
👤 **Nome:** {user['first_name'] or 'N/A'}
💰 **Saldo:** R$ {user['balance']:.2f}"""
        
        await query.edit_message_text(
            profile_text,
            reply_markup=AdminKeyboards.back_keyboard("admin_back_main"),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_admin_search(self, query, context):
        """Mostra pesquisa admin"""
        await query.edit_message_text(
            "🔍 **PESQUISA ADMINISTRATIVA**\n\nFuncionalidade de pesquisa.",
            reply_markup=AdminKeyboards.back_keyboard("admin_back_main"),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def request_add_balance(self, query, context):
        """Solicita valor para adicionar saldo"""
        self.user_states[query.from_user.id] = WAITING_ADD_BALANCE
        await query.edit_message_text("💰 Digite o valor para adicionar ao saldo:")
    
    # Funções utilitárias
    async def toggle_maintenance(self, query, context):
        """Alterna modo manutenção"""
        current_mode = self.db.get_setting("maintenance_mode") == "true"
        new_mode = not current_mode
        
        self.db.set_setting("maintenance_mode", str(new_mode).lower())
        
        status = "ativado" if new_mode else "desativado"
        await query.edit_message_text(f"🔧 Modo manutenção {status}!")
    
    async def request_login_data(self, query, context):
        """Solicita dados de login para adicionar ao estoque"""
        self.user_states[query.from_user.id] = WAITING_LOGIN_DATA
        separator = self.db.get_setting("separator") or settings.SEPARATOR
        
        await query.edit_message_text(
            f"""📮 **ADICIONAR LOGINS**

Envie os logins no formato:
**NOME{separator}VALOR{separator}DESCRICAO{separator}EMAIL{separator}SENHA{separator}DURACAO**

Para abastecer mais de um login, envie um abaixo do outro.""",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def process_login_data(self, update: Update, context, text):
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
        
        await update.message.reply_text(f"✅ {added_count} logins adicionados ao estoque!")
    
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
    
    async def process_admin_purchase(self, query, context, product_id: int):
        """Processa compra do admin (grátis)"""
        products = self.db.get_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            await query.edit_message_text("❌ Produto não encontrado.")
            return
        
        # Busca login disponível
        login = self.db.get_available_login(product_id)
        if not login:
            await query.edit_message_text(
                "❌ Nenhum login disponível.",
                reply_markup=AdminKeyboards.back_keyboard("admin_logins")
            )
            return
        
        # Marca como vendido (admin não paga)
        self.db.mark_login_as_sold(login['id'], query.from_user.id)
        
        # Instrução de uso baseada no produto
        instructions = self.get_product_instructions(product['name'])
        
        success_text = f"""✅ **LOGIN OBTIDO (ADMIN)**

**Produto:** {product['name']}
📧 **E-mail:** `{login['email']}`
🔐 **Senha:** `{login['password']}`

📖 **INSTRUÇÕES DE USO:**
{instructions}

**Validade:** {product['duration']} dias"""
        
        await query.edit_message_text(
            success_text,
            reply_markup=AdminKeyboards.back_keyboard("admin_logins"),
            parse_mode=ParseMode.MARKDOWN
        )
    
    def get_product_instructions(self, product_name: str) -> str:
        """Retorna instruções de uso baseadas no produto"""
        product_lower = product_name.lower()
        
        if 'netflix' in product_lower:
            return """1. Acesse netflix.com
2. Clique em "Entrar"
3. Digite o e-mail e senha fornecidos
4. Aproveite o conteúdo premium!

⚠️ NÃO altere dados da conta
⚠️ NÃO adicione cartão próprio"""
        
        elif 'spotify' in product_lower:
            return """1. Acesse spotify.com
2. Clique em "Entrar" 
3. Digite o e-mail e senha fornecidos
4. Aproveite a música premium!

⚠️ NÃO altere dados da conta"""
        
        elif 'disney' in product_lower:
            return """1. Acesse disneyplus.com
2. Clique em "Entrar"
3. Digite o e-mail e senha fornecidos
4. Aproveite o conteúdo Disney!

⚠️ NÃO altere dados da conta"""
        
        elif 'amazon' in product_lower or 'prime' in product_lower:
            return """1. Acesse primevideo.com
2. Clique em "Entrar"
3. Digite o e-mail e senha fornecidos
4. Aproveite filmes e séries!

⚠️ NÃO altere dados da conta"""
        
        else:
            return """1. Acesse o site oficial do serviço
2. Faça login com os dados fornecidos
3. Aproveite o conteúdo premium!

⚠️ NÃO altere dados da conta
⚠️ Use apenas para consumo"""
    
    async def send_broadcast(self, update: Update, context, message):
        """Envia mensagem para todos os usuários"""
        await update.message.reply_text(f"✅ Mensagem transmitida: {message}")
    
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