from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

class StoreKeyboards:
    
    @staticmethod
    def main_menu():
        """Menu principal da loja"""
        keyboard = [
            [InlineKeyboardButton("💎 Logins | Contas Premium", callback_data="store_products")],
            [
                InlineKeyboardButton("🪪 PERFIL", callback_data="store_profile"),
                InlineKeyboardButton("💰 RECARGA", callback_data="store_recharge")
            ],
            [
                InlineKeyboardButton("🎖️ Ranking", callback_data="store_ranking"),
                InlineKeyboardButton("👩‍💻 Suporte", callback_data="store_support")
            ],
            [
                InlineKeyboardButton("ℹ️ Informações", callback_data="store_info"),
                InlineKeyboardButton("🔎 Pesquisar Serviços", callback_data="store_search")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def product_list(products):
        """Lista de produtos disponíveis"""
        keyboard = []
        
        for product in products:
            keyboard.append([
                InlineKeyboardButton(
                    f"{product['name']} - R$ {product['price']:.2f}",
                    callback_data=f"product_{product['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("↩️ VOLTAR", callback_data="back_main")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def product_details(product_id: int, has_stock: bool = True):
        """Detalhes do produto com botão de compra"""
        keyboard = []
        
        if has_stock:
            keyboard.append([InlineKeyboardButton("🛒 Comprar", callback_data=f"buy_{product_id}")])
        else:
            keyboard.append([InlineKeyboardButton("❌ Sem Estoque", callback_data="no_stock")])
        
        keyboard.append([InlineKeyboardButton("↩️ Voltar", callback_data="store_products")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def profile_menu():
        """Menu do perfil"""
        keyboard = [
            [InlineKeyboardButton("🛍️ Historico De Compras", callback_data="purchase_history")],
            [InlineKeyboardButton("↩️ Voltar", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def recharge_menu():
        """Menu de recarga"""
        keyboard = [
            [InlineKeyboardButton("PUSHIN PAY", callback_data="recharge_pix")],
            [InlineKeyboardButton("↩️ Voltar", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def payment_waiting():
        """Botão aguardando pagamento"""
        keyboard = [
            [InlineKeyboardButton("⏰ Aguardando Pagamento", callback_data="check_payment")],
            [InlineKeyboardButton("↩️ Voltar", callback_data="store_recharge")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def ranking_menu():
        """Menu de ranking"""
        keyboard = [
            [
                InlineKeyboardButton("🏆 Serviços", callback_data="ranking_services"),
                InlineKeyboardButton("💰 Recargas", callback_data="ranking_recharges")
            ],
            [
                InlineKeyboardButton("🛒 Compras", callback_data="ranking_purchases"),
                InlineKeyboardButton("🎁 Gift Card", callback_data="ranking_giftcards")
            ],
            [
                InlineKeyboardButton("💎 Saldo", callback_data="ranking_balance"),
                InlineKeyboardButton("↩️ Voltar", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def ranking_back():
        """Botão voltar para ranking"""
        keyboard = [
            [InlineKeyboardButton("↩️ Voltar", callback_data="store_ranking")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_main():
        """Botão voltar ao menu principal"""
        keyboard = [
            [InlineKeyboardButton("↩️ Voltar", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def side_menu():
        """Menu lateral da loja"""
        keyboard = [
            [KeyboardButton("/start")],
            [KeyboardButton("/pix")],
            [KeyboardButton("/historico")],
            [KeyboardButton("/afiliados")],
            [KeyboardButton("/id")],
            [KeyboardButton("/ranking")],
            [KeyboardButton("/alertas")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def purchase_confirmation(product_id: int):
        """Confirmação de compra"""
        keyboard = [
            [
                InlineKeyboardButton("✅ CONFIRMAR COMPRA", callback_data=f"confirm_buy_{product_id}"),
                InlineKeyboardButton("❌ CANCELAR", callback_data="store_products")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def affiliate_menu():
        """Menu de afiliados"""
        keyboard = [
            [InlineKeyboardButton("💰 Converter Pontos", callback_data="convert_points")],
            [InlineKeyboardButton("↩️ Voltar", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def alerts_toggle(product_id: int, is_active: bool):
        """Toggle de alerta para produto"""
        status = "🔔 Ativar" if not is_active else "🔕 Desativar"
        action = "activate" if not is_active else "deactivate"
        
        keyboard = [
            [InlineKeyboardButton(f"{status} Alerta", callback_data=f"alert_{action}_{product_id}")],
            [InlineKeyboardButton("↩️ Voltar", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def search_results(products):
        """Resultados da pesquisa"""
        keyboard = []
        
        for product in products:
            keyboard.append([
                InlineKeyboardButton(
                    f"{product['name']} - R$ {product['price']:.2f}",
                    callback_data=f"product_{product['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔍 Nova Pesquisa", callback_data="store_search")])
        keyboard.append([InlineKeyboardButton("↩️ Voltar", callback_data="back_main")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def gift_card_menu():
        """Menu de gift cards"""
        keyboard = [
            [InlineKeyboardButton("🎁 Resgatar Gift Card", callback_data="redeem_gift")],
            [InlineKeyboardButton("📜 Histórico de Gifts", callback_data="gift_history")],
            [InlineKeyboardButton("↩️ Voltar", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)