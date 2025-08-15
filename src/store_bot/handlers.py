import os
import sys
import logging
import re
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Database
from config.settings import settings
from utils.payment_system import PaymentSystem, ManualPaymentSystem
from utils.notification_system import NotificationSystem
from store_bot.keyboards import StoreKeyboards

# Estados da conversa
WAITING_RECHARGE_AMOUNT = 1
WAITING_SEARCH_TERM = 2
WAITING_GIFT_CODE = 3

class StoreHandlers:
    def __init__(self, db: Database, payment_system: PaymentSystem, manual_payment: ManualPaymentSystem):
        self.db = db
        self.payment_system = payment_system
        self.manual_payment = manual_payment
        self.user_states = {}
        self.pending_payments = {}
        # Sistema de notificações para o canal
        self.notification_system = NotificationSystem(settings.STORE_BOT_TOKEN)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start da loja"""
        user_id = update.effective_user.id
        
        # Verifica modo manutenção
        if self.db.get_setting("maintenance_mode") == "true":
            await update.message.reply_text(
                "🔧 **Sistema em manutenção**\n\nO bot está temporariamente indisponível. Tente novamente mais tarde.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Registra ou atualiza usuário
        user = self.db.get_user(user_id)
        if not user:
            # Verifica se veio por link de afiliado
            args = context.args
            referred_by = None
            if args:
                referred_by = args[0].upper()
            
            self.db.create_user(
                user_id=user_id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name
            )
            
            # Se veio por afiliado, configura
            if referred_by:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET referred_by = ? WHERE user_id = ?', (referred_by, user_id))
                conn.commit()
                conn.close()
            
            # Adiciona bônus de registro se configurado
            registration_bonus = float(self.db.get_setting("registration_bonus") or settings.REGISTRATION_BONUS)
            if registration_bonus > 0:
                self.db.update_user_balance(user_id, registration_bonus, "add")
                self.db.create_transaction(user_id, "bonus", registration_bonus)
            
            user = self.db.get_user(user_id)
            
            # Envia notificação de novo usuário para o canal
            await self.notification_system.send_new_user_notification(user, referred_by)
        
        # Busca link de suporte configurado
        support_link = self.db.get_setting("support_link") or settings.SUPPORT_LINK
        
        # Monta mensagem de boas-vindas
        welcome_text = settings.MESSAGES['welcome_store'].format(
            support_link=support_link,
            user_id=user_id,
            balance=user['balance'],
            username=user['first_name'] or user['username'] or 'Usuário'
        )
        
        # Adiciona imagem se configurada
        image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSltpwF6kTey6ImHK0Z76OBq2AmdNgMsS7irFzm7Xv4Ji9whMxq-eD6PO2Y&s=10"
        
        await update.message.reply_photo(
            photo=image_url,
            caption=welcome_text,
            reply_markup=StoreKeyboards.main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Define menu lateral
        await update.message.reply_text(
            "Menu de comandos disponível:",
            reply_markup=StoreKeyboards.side_menu()
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manipula todos os callbacks do bot da loja"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        # Verifica modo manutenção
        if self.db.get_setting("maintenance_mode") == "true":
            await query.edit_message_text(
                "🔧 Sistema em manutenção. Tente novamente mais tarde.",
                reply_markup=StoreKeyboards.back_main()
            )
            return
        
        # Navegação principal
        if data == "back_main":
            await self.show_main_menu(query, context)
        elif data == "store_products":
            await self.show_products(query, context)
        elif data == "store_profile":
            await self.show_profile(query, context)
        elif data == "store_recharge":
            await self.show_recharge_menu(query, context)
        elif data == "store_ranking":
            await self.show_ranking_menu(query, context)
        elif data == "store_support":
            await self.handle_support(query, context)
        elif data == "store_info":
            await self.show_info(query, context)
        elif data == "store_search":
            await self.request_search(query, context)
        
        # Produtos
        elif data.startswith("product_"):
            product_id = int(data.split("_")[1])
            await self.show_product_details(query, context, product_id)
        elif data.startswith("buy_"):
            product_id = int(data.split("_")[1])
            await self.initiate_purchase(query, context, product_id)
        elif data.startswith("confirm_buy_"):
            product_id = int(data.split("_")[2])
            await self.process_purchase(query, context, product_id)
        
        # Recarga
        elif data == "recharge_pix":
            await self.request_recharge_amount(query, context)
        elif data == "check_payment":
            await self.check_payment_status(query, context, user_id)
        
        # Perfil
        elif data == "purchase_history":
            await self.show_purchase_history(query, context)
        
        # Ranking
        elif data == "ranking_services":
            await self.show_ranking(query, context, "services")
        elif data == "ranking_recharges":
            await self.show_ranking(query, context, "recharges")
        elif data == "ranking_purchases":
            await self.show_ranking(query, context, "purchases")
        elif data == "ranking_giftcards":
            await self.show_ranking(query, context, "giftcards")
        elif data == "ranking_balance":
            await self.show_ranking(query, context, "balance")
        
        # Afiliados
        elif data == "convert_points":
            await self.convert_affiliate_points(query, context)
    
    async def show_ranking_menu(self, query, context):
        """Mostra menu de ranking"""
        ranking_text = """🏆 **RANKINGS DA LOJA**

Escolha uma categoria para ver o ranking:"""
        
        await query.edit_message_text(
            ranking_text,
            reply_markup=StoreKeyboards.ranking_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_support(self, query, context):
        """Redireciona para o suporte"""
        support_link = self.db.get_setting("support_link") or settings.SUPPORT_LINK
        
        await query.edit_message_text(
            f"👨‍💻 **Suporte**\n\nClique no link abaixo para falar com nosso suporte:\n\n{support_link}",
            reply_markup=StoreKeyboards.back_main(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_info(self, query, context):
        """Mostra informações do bot"""
        bot_info = await context.bot.get_me()
        
        info_text = f"""ℹ️ **SOFTWARE INFO:**
🤖**BOT:** @{bot_info.username}
🤖**VERSION:** 1.0.0

🛠️ **DEVELOPER INFO:**
O Desenvolvedor não possui responsabilidade alguma sobre este Bot e nem sobre o adm do mesmo, caso entre em contato para reclamar sobre material ou pedir para chamar o adm deste Bot ou algo do tipo, será bloqueado de imediato... Apenas o chame, caso queira conhecer os Bots disponíveis."""
        
        await query.edit_message_text(
            info_text,
            reply_markup=StoreKeyboards.back_main(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def request_search(self, query, context):
        """Solicita termo de pesquisa"""
        self.user_states[query.from_user.id] = WAITING_SEARCH_TERM
        
        await query.edit_message_text(
            "🔍 **Pesquisar Produtos**\n\nDigite o nome do produto que deseja buscar:",
            reply_markup=StoreKeyboards.back_main(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def process_search(self, update: Update, context, search_term: str):
        """Processa pesquisa de produtos"""
        user_id = update.effective_user.id
        
        products = self.db.search_products(search_term)
        
        if not products:
            await update.message.reply_text(
                f"❌ Nenhum produto encontrado para '{search_term}'",
                reply_markup=StoreKeyboards.back_main()
            )
            return
        
        search_text = f"🔍 **Resultados para '{search_term}':**\n\n"
        
        await update.message.reply_text(
            search_text,
            reply_markup=StoreKeyboards.search_results(products),
            parse_mode=ParseMode.MARKDOWN
        )
        
        del self.user_states[user_id]
    
    async def show_purchase_history(self, query, context):
        """Mostra histórico de compras do usuário"""
        user_id = query.from_user.id
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.name, pu.amount, pu.purchase_date 
            FROM purchases pu
            JOIN products p ON pu.product_id = p.id
            WHERE pu.user_id = ?
            ORDER BY pu.purchase_date DESC
            LIMIT 20
        ''', (user_id,))
        
        purchases = cursor.fetchall()
        conn.close()
        
        if not purchases:
            history_text = "📊 **Histórico de Compras**\n\nVocê ainda não realizou nenhuma compra."
        else:
            history_text = "📊 **Histórico de Compras**\n\n"
            
            for purchase in purchases:
                history_text += f"• {purchase[0]} - R$ {purchase[1]:.2f}\n  📅 {purchase[2]}\n\n"
        
        await query.edit_message_text(
            history_text,
            reply_markup=StoreKeyboards.back_keyboard("store_profile"),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def convert_affiliate_points(self, query, context):
        """Converte pontos de afiliado em saldo"""
        user_id = query.from_user.id
        user = self.db.get_user(user_id)
        
        min_points = int(self.db.get_setting("min_points_to_convert") or settings.MIN_POINTS_TO_CONVERT)
        multiplier = float(self.db.get_setting("points_multiplier") or settings.POINTS_MULTIPLIER)
        
        if user['affiliate_points'] < min_points:
            await query.edit_message_text(
                f"❌ Você precisa de pelo menos {min_points} pontos para converter.\n\nSeus pontos: {user['affiliate_points']}",
                reply_markup=StoreKeyboards.back_main()
            )
            return
        
        # Calcula valor da conversão
        conversion_value = user['affiliate_points'] * multiplier
        
        # Atualiza banco
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET affiliate_points = 0, balance = balance + ? WHERE user_id = ?',
            (conversion_value, user_id)
        )
        conn.commit()
        conn.close()
        
        # Registra transação
        self.db.create_transaction(user_id, "affiliate", conversion_value)
        
        await query.edit_message_text(
            f"✅ **Conversão realizada!**\n\n{user['affiliate_points']} pontos convertidos em R$ {conversion_value:.2f}",
            reply_markup=StoreKeyboards.back_main(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_main_menu(self, query, context):
        """Mostra menu principal"""
        user = self.db.get_user(query.from_user.id)
        support_link = self.db.get_setting("support_link") or settings.SUPPORT_LINK
        
        welcome_text = settings.MESSAGES['welcome_store'].format(
            support_link=support_link,
            user_id=query.from_user.id,
            balance=user['balance'],
            username=user['first_name'] or user['username'] or 'Usuário'
        )
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=StoreKeyboards.main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_products(self, query, context):
        """Mostra produtos disponíveis"""
        products = self.db.get_products()
        
        if not products:
            await query.edit_message_text(
                "📦 Nenhum produto disponível no momento.",
                reply_markup=StoreKeyboards.back_main()
            )
            return
        
        user = self.db.get_user(query.from_user.id)
        
        text = f"""🎟️ **Logins Premium | Acesso Exclusivo**

🏦 **Carteira**
💸 **Saldo Atual:** R$ {user['balance']:.2f}

**Produtos disponíveis:**"""
        
        # Filtra apenas produtos com estoque
        available_products = [p for p in products if p['stock_count'] > 0]
        
        if not available_products:
            await query.edit_message_text(
                f"{text}\n\n❌ Todos os produtos estão sem estoque.",
                reply_markup=StoreKeyboards.back_main(),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        await query.edit_message_text(
            text,
            reply_markup=StoreKeyboards.product_list(available_products),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_product_details(self, query, context, product_id: int):
        """Mostra detalhes de um produto"""
        # Busca produto
        products = self.db.get_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            await query.edit_message_text(
                "❌ Produto não encontrado.",
                reply_markup=StoreKeyboards.back_main()
            )
            return
        
        user = self.db.get_user(query.from_user.id)
        
        product_text = f"""⚜️**ACESSO:** {product['name']}

💵 **Preço:** R$ {product['price']:.2f}
💼 **Saldo Atual:** R$ {user['balance']:.2f}
📥 **Estoque Disponível:** {product['stock_count']}

🗒️ **Descrição:** {product['description']}

**Aviso Importante:**
O acesso é disponibilizado na hora. Não atendemos ligações nem ouvimos mensagens de áudio; pedimos que aguarde sua vez.
Informamos que não realizamos reembolsos via Pix, apenas em créditos no bot, correspondendo aos dias restantes até o vencimento.
Agradecemos pela compreensão e desejamos boas compras!

♻️ **Garantia:** {product['duration']} dias"""
        
        has_stock = product['stock_count'] > 0
        
        await query.edit_message_text(
            product_text,
            reply_markup=StoreKeyboards.product_details(product_id, has_stock),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def initiate_purchase(self, query, context, product_id: int):
        """Inicia processo de compra"""
        user = self.db.get_user(query.from_user.id)
        products = self.db.get_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            await query.edit_message_text("❌ Produto não encontrado.")
            return
        
        # Verifica saldo
        if user['balance'] < product['price']:
            missing = product['price'] - user['balance']
            await query.answer(
                settings.MESSAGES['insufficient_balance'].format(
                    missing=missing,
                    balance=user['balance']
                ),
                show_alert=True
            )
            return
        
        # Verifica estoque
        if product['stock_count'] <= 0:
            await query.answer("❌ Produto sem estoque!", show_alert=True)
            return
        
        # Mostra confirmação
        confirm_text = f"""🛒 **CONFIRMAÇÃO DE COMPRA**

**Produto:** {product['name']}
**Preço:** R$ {product['price']:.2f}
**Seu saldo:** R$ {user['balance']:.2f}
**Saldo após compra:** R$ {user['balance'] - product['price']:.2f}

Confirma a compra?"""
        
        await query.edit_message_text(
            confirm_text,
            reply_markup=StoreKeyboards.purchase_confirmation(product_id),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def process_purchase(self, query, context, product_id: int):
        """Processa a compra efetivamente"""
        user_id = query.from_user.id
        user = self.db.get_user(user_id)
        
        # Busca produto novamente (verificação de segurança)
        products = self.db.get_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product or product['stock_count'] <= 0:
            await query.edit_message_text(
                "❌ Produto indisponível.",
                reply_markup=StoreKeyboards.back_main()
            )
            return
        
        if user['balance'] < product['price']:
            await query.edit_message_text(
                "❌ Saldo insuficiente.",
                reply_markup=StoreKeyboards.back_main()
            )
            return
        
        # Busca login disponível
        login = self.db.get_available_login(product_id)
        if not login:
            await query.edit_message_text(
                "❌ Nenhum login disponível.",
                reply_markup=StoreKeyboards.back_main()
            )
            return
        
        # Processa compra
        try:
            # Deduz saldo
            self.db.update_user_balance(user_id, product['price'], "subtract")
            
            # Marca login como vendido
            self.db.mark_login_as_sold(login['id'], user_id)
            
            # Registra compra
            self.db.create_purchase(user_id, product_id, login['id'], product['price'])
            
            # Registra transação
            self.db.create_transaction(user_id, "purchase", product['price'], product_id)
            
            # Processa pontos de afiliado se configurado
            await self.process_affiliate_points(user_id, product['price'])
            
            # Envia notificação de venda para o canal
            user_info = self.db.get_user(user_id)
            purchase_info = {'id': purchase_id, 'amount': product['price']}
            await self.notification_system.send_sale_notification(user_info, product, purchase_info)
            
            # Verifica se precisa enviar alerta de estoque baixo
            new_stock = product['stock_count'] - 1
            if new_stock <= 5:
                await self.notification_system.send_stock_alert(product['name'], new_stock)
            
            # Instrução de uso baseada no produto
            instructions = self.get_product_instructions(product['name'])
            
            # Monta mensagem de sucesso
            success_text = f"""✅ **COMPRA REALIZADA COM SUCESSO!**

**Produto:** {product['name']}
**Preço:** R$ {product['price']:.2f}

📧 **E-mail:** `{login['email']}`
🔐 **Senha:** `{login['password']}`

📖 **INSTRUÇÕES DE USO:**
{instructions}

{login['additional_info'] if login['additional_info'] else ''}

**Validade:** {product['duration']} dias
**Novo saldo:** R$ {user['balance'] - product['price']:.2f}

Obrigado pela compra! 🎉"""
            
            await query.edit_message_text(
                success_text,
                reply_markup=StoreKeyboards.back_main(),
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Log da compra
            self.db.add_log(
                user_id=user_id,
                action="purchase",
                details=f"Comprou {product['name']} por R$ {product['price']:.2f}"
            )
            
        except Exception as e:
            logging.error(f"Erro ao processar compra: {e}")
            await query.edit_message_text(
                "❌ Erro ao processar compra. Contate o suporte.",
                reply_markup=StoreKeyboards.back_main()
            )
    
    async def show_profile(self, query, context):
        """Mostra perfil do usuário"""
        user_id = query.from_user.id
        user = self.db.get_user(user_id)
        
        # Busca estatísticas do usuário
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Total de recargas
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE user_id = ? AND transaction_type = 'recharge' AND status = 'completed'
        ''', (user_id,))
        total_recharges = cursor.fetchone()[0]
        
        # Total de gift cards resgatados
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM gift_cards 
            WHERE used_by = ? AND is_used = 1
        ''', (user_id,))
        total_gifts = cursor.fetchone()[0]
        
        conn.close()
        
        profile_text = f"""🙋‍♂️ **Meu perfil**

🔎 **Veja aqui os detalhes da sua conta:**

**👤 Informações:**
🆔 **ID da Carteira:** {user_id}
💰 **Saldo Atual:** R$ {user['balance']:.2f}

**📊 Suas movimentações:**
—🛒 **Compras Realizadas:** {user['total_purchases']}
—💠 **Pix Inseridos:** R$ {total_recharges:.2f}
—🎁 **Gifts Resgatados:** R$ {total_gifts:.2f}"""
        
        await query.edit_message_text(
            profile_text,
            reply_markup=StoreKeyboards.profile_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_recharge_menu(self, query, context):
        """Mostra menu de recarga"""
        user = self.db.get_user(query.from_user.id)
        min_deposit = float(self.db.get_setting("min_deposit") or settings.MIN_DEPOSIT)
        
        recharge_text = f"""💼 **ID da Carteira:** {query.from_user.id}
💵 **Saldo Disponível:** R$ {user['balance']:.2f}

💡**Selecione uma opção para recarregar:**

🔻 **Recarga mínima:** R$ {min_deposit:.2f}"""
        
        await query.edit_message_text(
            recharge_text,
            reply_markup=StoreKeyboards.recharge_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def request_recharge_amount(self, query, context):
        """Solicita valor de recarga"""
        min_deposit = float(self.db.get_setting("min_deposit") or settings.MIN_DEPOSIT)
        
        self.user_states[query.from_user.id] = WAITING_RECHARGE_AMOUNT
        
        await query.edit_message_text(
            f"""ℹ️ **Informe o valor que deseja recarregar:**

🔻 **Recarga mínima:** R$ {min_deposit:.2f}

⚠️ Por favor, envie o valor que deseja recarregar agora.""",
            reply_markup=StoreKeyboards.back_main(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manipula entradas de texto"""
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        user_state = self.user_states.get(user_id)
        
        if user_state == WAITING_RECHARGE_AMOUNT:
            await self.process_recharge_amount(update, context, text)
        elif user_state == WAITING_SEARCH_TERM:
            await self.process_search(update, context, text)
        elif user_state == WAITING_GIFT_CODE:
            await self.process_gift_code(update, context, text)
    
    async def process_recharge_amount(self, update: Update, context, amount_text: str):
        """Processa valor de recarga"""
        user_id = update.effective_user.id
        
        try:
            amount = float(amount_text.replace(',', '.'))
            
            min_deposit = float(self.db.get_setting("min_deposit") or settings.MIN_DEPOSIT)
            max_deposit = float(self.db.get_setting("max_deposit") or settings.MAX_DEPOSIT)
            
            if amount < min_deposit:
                await update.message.reply_text(
                    f"❌ Valor mínimo: R$ {min_deposit:.2f}",
                    reply_markup=StoreKeyboards.back_main()
                )
                return
            
            if amount > max_deposit:
                await update.message.reply_text(
                    f"❌ Valor máximo: R$ {max_deposit:.2f}",
                    reply_markup=StoreKeyboards.back_main()
                )
                return
            
            # Cria pagamento
            await self.create_payment(update, context, amount)
            
            del self.user_states[user_id]
            
        except ValueError:
            await update.message.reply_text(
                "❌ Valor inválido. Use apenas números.",
                reply_markup=StoreKeyboards.back_main()
            )
    
    async def create_payment(self, update: Update, context, amount: float):
        """Cria pagamento PIX"""
        user_id = update.effective_user.id
        
        await update.message.reply_text("Gerando pagamento...")
        
        # Verifica se PIX automático está ativo
        pix_mode = self.db.get_setting("pix_mode") or "auto"
        
        if pix_mode == "auto" and self.payment_system:
            # PIX automático
            payment_result = self.payment_system.create_pix_payment(amount, user_id)
            
            if payment_result["success"]:
                # Salva transação
                transaction_id = self.db.create_transaction(
                    user_id=user_id,
                    transaction_type="recharge",
                    amount=amount,
                    payment_id=payment_result["payment_id"],
                    pix_code=payment_result["pix_code"]
                )
                
                # Salva pagamento pendente
                self.pending_payments[user_id] = {
                    "transaction_id": transaction_id,
                    "mp_payment_id": payment_result["mp_payment_id"],
                    "amount": amount
                }
                
                payment_text = settings.MESSAGES['payment_generated'].format(
                    expiration=payment_result["expires_in"],
                    amount=amount,
                    payment_id=payment_result["payment_id"],
                    pix_code=payment_result["pix_code"]
                )
                
                await update.message.reply_text(
                    payment_text,
                    reply_markup=StoreKeyboards.payment_waiting(),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    f"❌ Erro ao gerar pagamento: {payment_result['error']}",
                    reply_markup=StoreKeyboards.back_main()
                )
        
        else:
            # PIX manual
            manual_result = self.manual_payment.create_manual_payment(amount, user_id)
            
            await update.message.reply_text(
                f"💰 **Pagamento Manual**\n\n"
                f"Valor: R$ {amount:.2f}\n"
                f"ID: {manual_result['payment_id']}\n\n"
                f"Entre em contato com o suporte para confirmar o pagamento.",
                reply_markup=StoreKeyboards.back_main(),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_ranking(self, query, context, ranking_type: str):
        """Mostra ranking"""
        ranking_data = self.db.get_ranking_data(ranking_type, 10)
        
        titles = {
            "services": "🏆 Ranking dos serviços mais vendidos (deste mês)",
            "recharges": "🏆 Ranking dos usuários que mais recarregaram (deste mês)",
            "purchases": "🏆 Ranking dos usuários que mais compraram (deste mês)",
            "giftcards": "🏆 Ranking dos usuários que mais resgataram gift card (prazo total)",
            "balance": "🏆 Ranking dos usuários com maior saldo"
        }
        
        medals = ["🥇", "🥈", "🥉"]
        
        ranking_text = f"{titles[ranking_type]}\n\n"
        
        if not ranking_data:
            ranking_text += "Nenhum dado disponível."
        else:
            for i, item in enumerate(ranking_data):
                position = i + 1
                medal = medals[i] if i < 3 else ""
                
                if ranking_type == "services":
                    ranking_text += f"{position}°) {item['name']} {medal} Com {item['sales_count']} pedidos\n"
                elif ranking_type in ["recharges", "giftcards"]:
                    value_key = "total_recharges" if ranking_type == "recharges" else "total_giftcards"
                    ranking_text += f"{position}°) {item['first_name']} {medal} Com R$ {item[value_key]:.2f} {'em recargas' if ranking_type == 'recharges' else 'resgatados'}\n"
                elif ranking_type == "purchases":
                    ranking_text += f"{position}°) {item['first_name']} {medal} Com {item['purchase_count']} compras\n"
                elif ranking_type == "balance":
                    ranking_text += f"{position}°) {item['first_name']} {medal} Com R$ {item['balance']:.2f} de saldo\n"
        
        await query.edit_message_text(
            ranking_text,
            reply_markup=StoreKeyboards.ranking_back(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def check_payment_status(self, query, context, user_id: int):
        """Verifica status do pagamento"""
        if user_id not in self.pending_payments:
            await query.edit_message_text(
                "❌ Nenhum pagamento pendente encontrado.",
                reply_markup=StoreKeyboards.back_main()
            )
            return
        
        payment_info = self.pending_payments[user_id]
        
        if self.payment_system:
            # Verifica status no Mercado Pago
            status = self.payment_system.check_payment_status(payment_info["mp_payment_id"])
            
            if status["success"] and status["status"] == "approved":
                # Pagamento aprovado
                await self.process_approved_payment(user_id, payment_info["amount"])
                
                del self.pending_payments[user_id]
                
                await query.edit_message_text(
                    f"✅ **Pagamento aprovado!**\n\nR$ {payment_info['amount']:.2f} foram adicionados ao seu saldo.",
                    reply_markup=StoreKeyboards.back_main(),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.answer("⏰ Pagamento ainda não foi aprovado.", show_alert=True)
        else:
            await query.answer("💰 Aguarde aprovação manual do pagamento.", show_alert=True)
    
    async def process_approved_payment(self, user_id: int, amount: float):
        """Processa pagamento aprovado"""
        # Adiciona saldo
        self.db.update_user_balance(user_id, amount, "add")
        
        # Marca transação como completa
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE transactions SET status = "completed", completed_date = CURRENT_TIMESTAMP WHERE user_id = ? AND amount = ? AND status = "pending" ORDER BY created_date DESC LIMIT 1',
            (user_id, amount)
        )
        conn.commit()
        conn.close()
        
        # Envia notificação de recarga para o canal
        user_info = self.db.get_user(user_id)
        await self.notification_system.send_recharge_notification(
            user_info, 
            amount, 
            "PIX Automático" if self.payment_system else "PIX Manual"
        )
        
        # Processa pontos de afiliado
        await self.process_affiliate_points(user_id, amount)
        
    async def process_affiliate_points(self, user_id: int, amount: float):
        """Processa pontos de afiliado para quem indicou"""
        affiliate_enabled = self.db.get_setting("affiliate_system_enabled")
        if affiliate_enabled != "true":
            return
        
        user = self.db.get_user(user_id)
        if not user['referred_by']:
            return
        
        # Busca quem indicou
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT user_id FROM users WHERE affiliate_code = ?',
            (user['referred_by'],)
        )
        referrer = cursor.fetchone()
        
        if referrer:
            points_per_recharge = int(self.db.get_setting("points_per_recharge") or settings.POINTS_PER_RECHARGE)
            
            # Adiciona pontos
            cursor.execute(
                'UPDATE users SET affiliate_points = affiliate_points + ? WHERE user_id = ?',
                (points_per_recharge, referrer[0])
            )
            conn.commit()
        
        conn.close()
    
    # Comandos do menu lateral
    async def pix_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /pix"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "Você enviou em um formato incorreto. Envie /pix e o valor que deseja...\n"
                "Exemplo:\n/pix 10\n/pix 6.26"
            )
            return
        
        try:
            amount = float(args[0].replace(',', '.'))
            await self.create_payment(update, context, amount)
        except (ValueError, IndexError):
            await update.message.reply_text(
                "❌ Valor inválido. Use: /pix 10.50"
            )
    
    async def id_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /id"""
        await update.message.reply_text(f"🆔 **Seu id é:** {update.effective_user.id}")
    
    async def afiliados_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /afiliados"""
        user_id = update.effective_user.id
        affiliate_stats = self.db.get_affiliate_stats(user_id)
        
        status = "Ativo" if settings.AFFILIATE_SYSTEM_ENABLED else "Inativo"
        points_per_recharge = self.db.get_setting("points_per_recharge") or settings.POINTS_PER_RECHARGE
        
        affiliate_text = f"""ℹ️ **Status:** {status}
📊 **Comissão por Indicação:** {points_per_recharge} pontos
👥 **Total de Afiliados:** {affiliate_stats.get('affiliates_count', 0)}
🔗 **Link para Indicar:** {affiliate_stats.get('affiliate_link', 'N/A')}

**Como Funciona?**
Copie seu link de indicação e envie para outras pessoas.
Cada vez que alguém indicado por você fizer uma recarga no bot, você receberá uma porcentagem desse valor!
Por exemplo, com uma comissão de 50%, se 5 pessoas indicadas recarregarem R$10,00 cada, você receberá R$25,00.
Indique mais e aumente seus ganhos!"""
        
        await update.message.reply_text(
            affiliate_text,
            reply_markup=StoreKeyboards.affiliate_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    def get_product_instructions(self, product_name: str) -> str:
        """Retorna instruções de uso automáticas baseadas no produto"""
        product_lower = product_name.lower()
        
        if 'netflix' in product_lower:
            return """1. Acesse netflix.com
2. Clique em "Entrar"
3. Digite o e-mail e senha fornecidos
4. Selecione o perfil desejado
5. Aproveite o conteúdo premium!

⚠️ **IMPORTANTE:**
• NÃO altere dados da conta
• NÃO adicione cartão próprio
• NÃO mude senha ou e-mail
• Use apenas para assistir"""
        
        elif 'spotify' in product_lower:
            return """1. Acesse spotify.com
2. Clique em "Entrar" 
3. Digite o e-mail e senha fornecidos
4. Aproveite a música premium sem anúncios!

⚠️ **IMPORTANTE:**
• NÃO altere dados da conta
• NÃO adicione forma de pagamento
• Download offline disponível"""
        
        elif 'disney' in product_lower:
            return """1. Acesse disneyplus.com
2. Clique em "Entrar"
3. Digite o e-mail e senha fornecidos
4. Crie seu perfil personalizado
5. Aproveite Disney, Marvel, Star Wars!

⚠️ **IMPORTANTE:**
• NÃO altere dados da conta
• Até 4 perfis simultâneos"""
        
        elif 'amazon' in product_lower or 'prime' in product_lower:
            return """1. Acesse primevideo.com
2. Clique em "Entrar"
3. Digite o e-mail e senha fornecidos
4. Aproveite filmes e séries originais!

⚠️ **IMPORTANTE:**
• NÃO altere dados da conta
• NÃO use para compras na Amazon
• Apenas para Prime Video"""
        
        elif 'globoplay' in product_lower:
            return """1. Acesse globoplay.globo.com
2. Clique em "Entrar"
3. Digite o e-mail e senha fornecidos
4. Assista novelas, séries e esportes!

⚠️ **IMPORTANTE:**
• NÃO altere dados da conta
• Conteúdo ao vivo disponível"""
        
        elif 'youtube' in product_lower:
            return """1. Acesse youtube.com
2. Clique no perfil (canto superior direito)
3. Digite o e-mail e senha fornecidos
4. Aproveite sem anúncios e com download!

⚠️ **IMPORTANTE:**
• NÃO altere dados da conta
• YouTube Music incluso"""
        
        elif 'crunchyroll' in product_lower:
            return """1. Acesse crunchyroll.com
2. Clique em "Log In"
3. Digite o e-mail e senha fornecidos
4. Assista animes em HD sem anúncios!

⚠️ **IMPORTANTE:**
• NÃO altere dados da conta
• Legendas e dublagens disponíveis"""
        
        elif 'chatgpt' in product_lower:
            return """1. Acesse chat.openai.com
2. Clique em "Log In"
3. Digite o e-mail e senha fornecidos
4. Use ChatGPT Plus ilimitado!

⚠️ **IMPORTANTE:**
• NÃO altere dados da conta
• GPT-4 disponível"""
        
        elif 'free fire' in product_lower:
            return """1. Abra Free Fire
2. Faça login com Facebook/Google
3. Use as informações fornecidas
4. Aproveite skins e diamantes!

⚠️ **IMPORTANTE:**
• NÃO altere dados da conta
• NÃO vincule outros métodos"""
        
        else:
            return """1. Acesse o site oficial do serviço
2. Faça login com os dados fornecidos
3. Aproveite o conteúdo premium!

⚠️ **IMPORTANTE:**
• NÃO altere dados da conta
• NÃO adicione formas de pagamento
• Use apenas para consumo do conteúdo
• Em caso de dúvidas, entre em contato"""