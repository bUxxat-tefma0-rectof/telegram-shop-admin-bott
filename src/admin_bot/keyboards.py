from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

class AdminKeyboards:
    
    @staticmethod
    def main_menu():
        """Menu principal do admin"""
        keyboard = [
            [
                InlineKeyboardButton("🎟️ LOGINS | CONTA PREMIUM", callback_data="admin_logins"),
            ],
            [
                InlineKeyboardButton("👤 PERFIL", callback_data="admin_profile"),
                InlineKeyboardButton("💰 ADICIONAR SALDO", callback_data="admin_add_balance")
            ],
            [
                InlineKeyboardButton("👨‍💻 SUPORTE", callback_data="admin_support"),
            ],
            [
                InlineKeyboardButton("🔎 PESQUISAR SERVIÇOS", callback_data="admin_search")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_dashboard():
        """Dashboard administrativo"""
        keyboard = [
            [
                InlineKeyboardButton("🔧 CONFIGURAÇÕES", callback_data="admin_config"),
                InlineKeyboardButton("🔖 AÇÕES", callback_data="admin_actions")
            ],
            [
                InlineKeyboardButton("🔄 TRANSAÇÕES", callback_data="admin_transactions"),
                InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_config_menu():
        """Menu de configurações"""
        keyboard = [
            [InlineKeyboardButton("⚙️ CONFIGURAÇÕES GERAIS ⚙️", callback_data="config_general")],
            [InlineKeyboardButton("🕵️‍♀️ CONFIGURAR ADMINS", callback_data="config_admins")],
            [InlineKeyboardButton("👥 CONFIGURAR AFILIADOS", callback_data="config_affiliates")],
            [InlineKeyboardButton("👤 CONFIGURAR USUARIOS", callback_data="config_users")],
            [InlineKeyboardButton("💠 CONFIGURAR PIX", callback_data="config_pix")],
            [InlineKeyboardButton("🖥️ CONFIGURAR LOGINS", callback_data="config_logins")],
            [InlineKeyboardButton("🔎 CONFIGURAR PESQUISA DE LOGIN", callback_data="config_search")],
            [InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_dashboard")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def general_config():
        """Configurações gerais"""
        keyboard = [
            [InlineKeyboardButton("♻️ RENOVAR PLANO ♻️", callback_data="renew_plan")],
            [InlineKeyboardButton("🤖 REINICIAR BOT 🤖", callback_data="restart_bot")],
            [InlineKeyboardButton("🔴 MANUTENÇÃO", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("🎧 MUDAR SUPORTE", callback_data="change_support")],
            [InlineKeyboardButton("✂️ MUDAR SEPARADOR", callback_data="change_separator")],
            [InlineKeyboardButton("📭 MUDAR DESTINO LOG", callback_data="change_log_dest")],
            [InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_config")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_management():
        """Gestão de administradores"""
        keyboard = [
            [InlineKeyboardButton("➕ ADICIONAR ADM", callback_data="add_admin")],
            [InlineKeyboardButton("🚮 REMOVER ADM", callback_data="remove_admin")],
            [InlineKeyboardButton("🗞️ LISTA DE ADM", callback_data="list_admins")],
            [InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_config")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def affiliate_config():
        """Configuração de afiliados"""
        keyboard = [
            [InlineKeyboardButton("🟢 SISTEMA DE INDICAÇÃO", callback_data="toggle_affiliate_system")],
            [InlineKeyboardButton("🗞️ PONTOS POR RECARGA", callback_data="set_points_per_recharge")],
            [InlineKeyboardButton("🔻 PONTOS MINIMO PARA CONVERTER", callback_data="set_min_points")],
            [InlineKeyboardButton("✖️ MULTIPLICADOR PARA CONVERTER", callback_data="set_multiplier")],
            [InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_config")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def user_config():
        """Configuração de usuários"""
        keyboard = [
            [InlineKeyboardButton("📭 TRANSMITIR A TODOS", callback_data="broadcast_all")],
            [InlineKeyboardButton("🔎 PESQUISAR USUARIO", callback_data="search_user")],
            [InlineKeyboardButton("🎁 BONUS DE REGISTRO", callback_data="set_registration_bonus")],
            [InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_config")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pix_config():
        """Configuração PIX"""
        keyboard = [
            [InlineKeyboardButton("🔴 PIX MANUAL", callback_data="set_pix_manual")],
            [InlineKeyboardButton("🟢 PIX AUTOMATICO", callback_data="set_pix_auto")],
            [InlineKeyboardButton("🔑 MUDAR TOKEN", callback_data="change_mp_token")],
            [InlineKeyboardButton("🔻 MUDAR DEPOSITO MIN", callback_data="change_min_deposit")],
            [InlineKeyboardButton("❗️ MUDAR DEPOSITO MAX", callback_data="change_max_deposit")],
            [InlineKeyboardButton("⏰ MUDAR TEMPO DE EXPIRAÇÃO", callback_data="change_expiration_time")],
            [InlineKeyboardButton("🔶 MUDAR BONUS", callback_data="change_deposit_bonus")],
            [InlineKeyboardButton("🔷 MUDAR MIN PARA BONUS", callback_data="change_min_for_bonus")],
            [InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_config")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def login_config():
        """Configuração de logins"""
        keyboard = [
            [InlineKeyboardButton("📮 ADICIONAR LOGIN", callback_data="add_login")],
            [InlineKeyboardButton("🥾 REMOVER LOGIN", callback_data="remove_login")],
            [InlineKeyboardButton("❌ REMOVER POR PLATAFORMA", callback_data="remove_by_platform")],
            [InlineKeyboardButton("📦 ESTOQUE DETALHADO", callback_data="detailed_stock")],
            [InlineKeyboardButton("🗑️ ZERAR ESTOQUE", callback_data="clear_stock")],
            [InlineKeyboardButton("💸 MUDAR VALOR DO SERVIÇO", callback_data="change_service_price")],
            [InlineKeyboardButton("🪪 MUDAR VALOR DE TODOS", callback_data="change_all_prices")],
            [InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_config")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def search_config():
        """Configuração de pesquisa"""
        keyboard = [
            [InlineKeyboardButton("🟢 SISTEMA PESQUISA", callback_data="toggle_search_system")],
            [InlineKeyboardButton("➕ ADICIONAR IMAGEM", callback_data="add_search_image")],
            [InlineKeyboardButton("🚮 REMOVER IMAGEM", callback_data="remove_search_image")],
            [InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_config")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirmation_keyboard(action_data: str):
        """Teclado de confirmação"""
        keyboard = [
            [
                InlineKeyboardButton("✅ CONFIRMAR", callback_data=f"confirm_{action_data}"),
                InlineKeyboardButton("❌ CANCELAR", callback_data="cancel_action")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_keyboard(callback_data: str):
        """Teclado apenas com voltar"""
        keyboard = [
            [InlineKeyboardButton("↩️ VOLTAR", callback_data=callback_data)]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_menu_lateral():
        """Menu lateral para administradores"""
        keyboard = [
            [KeyboardButton("⚔️ Menu Inicial")],
            [KeyboardButton("🗡️ Menu Administrativo")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def product_purchase(product_id: int):
        """Botões para compra de produto"""
        keyboard = [
            [InlineKeyboardButton("🛒 COMPRAR", callback_data=f"buy_product_{product_id}")],
            [InlineKeyboardButton("↩️ VOLTAR", callback_data="admin_logins")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def maintenance_toggle(is_maintenance: bool):
        """Botão de manutenção"""
        status = "ON" if is_maintenance else "OFF"
        color = "🔴" if is_maintenance else "🟢"
        keyboard = [
            [InlineKeyboardButton(f"{color} MANUTENÇÃO ({status})", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("↩️ VOLTAR", callback_data="config_general")]
        ]
        return InlineKeyboardMarkup(keyboard)