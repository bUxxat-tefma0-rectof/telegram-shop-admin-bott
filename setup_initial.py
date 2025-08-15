#!/usr/bin/env python3
"""
Script de Setup Inicial - Configura tudo automaticamente
"""

import os
import sys
from dotenv import load_dotenv

# Carrega configurações
load_dotenv()

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_database():
    """Configura banco de dados inicial"""
    try:
        from database.models import Database
        from config.settings import settings
        
        print("💾 Configurando banco de dados...")
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(settings.DATABASE_PATH), exist_ok=True)
        
        # Inicializa banco
        db = Database(settings.DATABASE_PATH)
        
        # Configura configurações padrão
        default_settings = {
            "support_link": settings.SUPPORT_LINK,
            "separator": settings.SEPARATOR,
            "log_destination": str(settings.LOG_DESTINATION),
            "affiliate_system_enabled": "true",
            "min_points_to_convert": str(settings.MIN_POINTS_TO_CONVERT),
            "points_multiplier": str(settings.POINTS_MULTIPLIER),
            "points_per_recharge": str(settings.POINTS_PER_RECHARGE),
            "registration_bonus": str(settings.REGISTRATION_BONUS),
            "maintenance_mode": "false",
            "min_deposit": str(settings.MIN_DEPOSIT),
            "max_deposit": str(settings.MAX_DEPOSIT),
            "pix_expiration_time": str(settings.PIX_EXPIRATION_TIME),
            "deposit_bonus": str(settings.DEPOSIT_BONUS),
            "min_deposit_for_bonus": str(settings.MIN_DEPOSIT_FOR_BONUS),
            "pix_mode": "manual"
        }
        
        for key, value in default_settings.items():
            db.set_setting(key, value)
        
        # Configura admin
        admin_id = settings.ADMIN_USER_ID
        if admin_id:
            db.set_setting(f"admin_{admin_id}", "true")
            db.set_setting("admin_list", str(admin_id))
        
        # Cria usuário admin se não existir
        if admin_id:
            if not db.get_user(admin_id):
                db.create_user(admin_id, "admin", "Administrador")
        
        print("✅ Banco configurado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar banco: {e}")
        return False

def setup_sample_products():
    """Adiciona produtos de exemplo"""
    try:
        from database.models import Database
        from config.settings import settings
        
        print("🛍️ Adicionando produtos de exemplo...")
        
        db = Database(settings.DATABASE_PATH)
        
        # Produtos de exemplo
        sample_products = [
            {
                "name": "NETFLIX PREMIUM",
                "price": 15.99,
                "description": "Netflix Premium com acesso total - 30 dias de garantia",
                "duration": 30
            },
            {
                "name": "SPOTIFY PREMIUM", 
                "price": 8.99,
                "description": "Spotify Premium sem anúncios - 30 dias de garantia",
                "duration": 30
            },
            {
                "name": "DISNEY+ PREMIUM",
                "price": 12.99, 
                "description": "Disney+ com todo conteúdo premium - 30 dias de garantia",
                "duration": 30
            }
        ]
        
        for product_data in sample_products:
            # Verifica se já existe
            products = db.get_products()
            exists = any(p['name'] == product_data['name'] for p in products)
            
            if not exists:
                product_id = db.create_product(
                    product_data['name'],
                    product_data['price'], 
                    product_data['description'],
                    product_data['duration']
                )
                
                # Adiciona logins de exemplo
                sample_logins = [
                    f"user1_{product_data['name'].lower().replace(' ', '')}@example.com",
                    f"user2_{product_data['name'].lower().replace(' ', '')}@example.com",
                    f"user3_{product_data['name'].lower().replace(' ', '')}@example.com"
                ]
                
                for i, email in enumerate(sample_logins):
                    db.add_login_to_stock(
                        product_id,
                        email,
                        f"senha{i+1}23",
                        f"Login de exemplo para {product_data['name']}"
                    )
                
                print(f"✅ Produto adicionado: {product_data['name']}")
        
        print("✅ Produtos de exemplo configurados!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar produtos: {e}")
        return False

def main():
    """Setup principal"""
    print("🚀 SETUP INICIAL DO SISTEMA")
    print("=" * 40)
    
    # Setup banco
    db_ok = setup_database()
    
    # Setup produtos exemplo
    products_ok = setup_sample_products()
    
    print("\n" + "=" * 40)
    print("📊 RESULTADO DO SETUP:")
    print(f"💾 Banco de dados: {'✅' if db_ok else '❌'}")
    print(f"🛍️ Produtos exemplo: {'✅' if products_ok else '❌'}")
    
    if db_ok and products_ok:
        print("\n🎉 SETUP COMPLETO!")
        print("\n📱 Seus bots agora têm:")
        print("   • Configurações padrão")
        print("   • Admin configurado")
        print("   • Produtos de exemplo")
        print("   • Sistema de afiliados ativo")
        print("\n✅ Você pode testar agora!")
    else:
        print("\n❌ SETUP INCOMPLETO - Verifique os erros")

if __name__ == "__main__":
    main()