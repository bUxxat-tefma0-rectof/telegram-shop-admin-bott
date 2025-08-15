import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com todas as tabelas necessárias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                balance REAL DEFAULT 0.0,
                total_purchases INTEGER DEFAULT 0,
                total_recharges REAL DEFAULT 0.0,
                affiliate_points INTEGER DEFAULT 0,
                affiliate_code TEXT UNIQUE,
                referred_by TEXT,
                registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT 0,
                is_banned BOOLEAN DEFAULT 0
            )
        ''')
        
        # Tabela de produtos/logins
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                duration INTEGER DEFAULT 30,
                stock_count INTEGER DEFAULT 0,
                total_sales INTEGER DEFAULT 0,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabela de estoque de logins
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_stock (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                additional_info TEXT,
                is_sold BOOLEAN DEFAULT 0,
                sold_date DATETIME,
                sold_to INTEGER,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (sold_to) REFERENCES users (user_id)
            )
        ''')
        
        # Tabela de transações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL, -- 'purchase', 'recharge', 'bonus', 'affiliate'
                amount REAL NOT NULL,
                product_id INTEGER,
                payment_id TEXT,
                pix_code TEXT,
                status TEXT DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'expired'
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_date DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Tabela de compras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                login_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (login_id) REFERENCES login_stock (id)
            )
        ''')
        
        # Tabela de gift cards
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gift_cards (
                id INTEGER PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                amount REAL NOT NULL,
                created_by INTEGER,
                used_by INTEGER,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_date DATETIME,
                is_used BOOLEAN DEFAULT 0,
                FOREIGN KEY (created_by) REFERENCES users (user_id),
                FOREIGN KEY (used_by) REFERENCES users (user_id)
            )
        ''')
        
        # Tabela de configurações do bot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_settings (
                id INTEGER PRIMARY KEY,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL,
                updated_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Tabela de imagens para pesquisa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_images (
                id INTEGER PRIMARY KEY,
                file_id TEXT NOT NULL,
                description TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)
    
    # ===== MÉTODOS DE USUÁRIO =====
    
    def create_user(self, user_id: int, username: str = None, first_name: str = None) -> bool:
        """Cria um novo usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Gera código de afiliado único
            affiliate_code = self.generate_affiliate_code(user_id)
            
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, affiliate_code)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, affiliate_code))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Busca um usuário pelo ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM users WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def update_user_balance(self, user_id: int, amount: float, operation: str = 'add') -> bool:
        """Atualiza o saldo do usuário"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if operation == 'add':
            cursor.execute('''
                UPDATE users SET balance = balance + ?, last_activity = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (amount, user_id))
        elif operation == 'subtract':
            cursor.execute('''
                UPDATE users SET balance = balance - ?, last_activity = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (amount, user_id))
        elif operation == 'set':
            cursor.execute('''
                UPDATE users SET balance = ?, last_activity = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (amount, user_id))
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        return affected_rows > 0
    
    def generate_affiliate_code(self, user_id: int) -> str:
        """Gera um código de afiliado único"""
        base_string = f"{user_id}_{datetime.now().timestamp()}"
        hash_object = hashlib.md5(base_string.encode())
        return hash_object.hexdigest()[:8].upper()
    
    def get_affiliate_stats(self, user_id: int) -> Dict:
        """Retorna estatísticas de afiliado"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Busca código de afiliado
        cursor.execute('SELECT affiliate_code, affiliate_points FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            conn.close()
            return {}
        
        affiliate_code, points = user_data
        
        # Conta afiliados
        cursor.execute('SELECT COUNT(*) FROM users WHERE referred_by = ?', (affiliate_code,))
        affiliates_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'affiliate_code': affiliate_code,
            'points': points,
            'affiliates_count': affiliates_count,
            'affiliate_link': f'https://t.me/seu_bot_aqui?start={affiliate_code}'
        }
    
    # ===== MÉTODOS DE PRODUTOS =====
    
    def create_product(self, name: str, price: float, description: str = "", duration: int = 30) -> int:
        """Cria um novo produto"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO products (name, price, description, duration)
            VALUES (?, ?, ?, ?)
        ''', (name, price, description, duration))
        
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return product_id
    
    def add_login_to_stock(self, product_id: int, email: str, password: str, additional_info: str = "") -> bool:
        """Adiciona um login ao estoque"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO login_stock (product_id, email, password, additional_info)
                VALUES (?, ?, ?, ?)
            ''', (product_id, email, password, additional_info))
            
            # Atualiza contador de estoque
            cursor.execute('''
                UPDATE products SET stock_count = stock_count + 1
                WHERE id = ?
            ''', (product_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False
    
    def get_available_login(self, product_id: int) -> Optional[Dict]:
        """Retorna um login disponível do produto"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM login_stock 
            WHERE product_id = ? AND is_sold = 0 
            ORDER BY created_date ASC 
            LIMIT 1
        ''', (product_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def mark_login_as_sold(self, login_id: int, user_id: int) -> bool:
        """Marca um login como vendido"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE login_stock 
            SET is_sold = 1, sold_date = CURRENT_TIMESTAMP, sold_to = ?
            WHERE id = ?
        ''', (user_id, login_id))
        
        # Atualiza contador de estoque
        cursor.execute('''
            SELECT product_id FROM login_stock WHERE id = ?
        ''', (login_id,))
        
        product_id = cursor.fetchone()[0]
        
        cursor.execute('''
            UPDATE products SET stock_count = stock_count - 1, total_sales = total_sales + 1
            WHERE id = ?
        ''', (product_id,))
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        return affected_rows > 0
    
    def get_products(self, active_only: bool = True) -> List[Dict]:
        """Retorna lista de produtos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM products'
        if active_only:
            query += ' WHERE is_active = 1'
        query += ' ORDER BY name'
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        products = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return products
    
    def search_products(self, search_term: str) -> List[Dict]:
        """Busca produtos por nome"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM products 
            WHERE name LIKE ? AND is_active = 1 AND stock_count > 0
            ORDER BY name
        ''', (f'%{search_term}%',))
        
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        products = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return products
    
    # ===== MÉTODOS DE TRANSAÇÕES =====
    
    def create_transaction(self, user_id: int, transaction_type: str, amount: float, 
                          product_id: int = None, payment_id: str = None, pix_code: str = None) -> int:
        """Cria uma nova transação"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (user_id, transaction_type, amount, product_id, payment_id, pix_code)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, transaction_type, amount, product_id, payment_id, pix_code))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return transaction_id
    
    def complete_transaction(self, transaction_id: int) -> bool:
        """Marca uma transação como completa"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE transactions 
            SET status = 'completed', completed_date = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (transaction_id,))
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        return affected_rows > 0
    
    def create_purchase(self, user_id: int, product_id: int, login_id: int, amount: float) -> int:
        """Registra uma compra"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO purchases (user_id, product_id, login_id, amount)
            VALUES (?, ?, ?, ?)
        ''', (user_id, product_id, login_id, amount))
        
        purchase_id = cursor.lastrowid
        
        # Atualiza total de compras do usuário
        cursor.execute('''
            UPDATE users SET total_purchases = total_purchases + 1
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        return purchase_id
    
    # ===== MÉTODOS DE ESTATÍSTICAS =====
    
    def get_revenue_stats(self) -> Dict:
        """Retorna estatísticas de receita"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Receita total
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE transaction_type = 'recharge' AND status = 'completed'
        ''')
        total_revenue = cursor.fetchone()[0]
        
        # Receita mensal
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE transaction_type = 'recharge' AND status = 'completed'
            AND DATE(created_date) >= DATE('now', 'start of month')
        ''')
        monthly_revenue = cursor.fetchone()[0]
        
        # Receita diária
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE transaction_type = 'recharge' AND status = 'completed'
            AND DATE(created_date) = DATE('now')
        ''')
        daily_revenue = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_revenue': total_revenue,
            'monthly_revenue': monthly_revenue,
            'daily_revenue': daily_revenue
        }
    
    def get_sales_stats(self) -> Dict:
        """Retorna estatísticas de vendas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Vendas totais
        cursor.execute('SELECT COUNT(*) FROM purchases')
        total_sales = cursor.fetchone()[0]
        
        # Vendas de hoje
        cursor.execute('''
            SELECT COUNT(*) FROM purchases 
            WHERE DATE(purchase_date) = DATE('now')
        ''')
        daily_sales = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_sales': total_sales,
            'daily_sales': daily_sales
        }
    
    def get_user_stats(self) -> Dict:
        """Retorna estatísticas de usuários"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {'total_users': total_users}
    
    def get_ranking_data(self, ranking_type: str, limit: int = 10) -> List[Dict]:
        """Retorna dados de ranking"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if ranking_type == 'services':
            cursor.execute('''
                SELECT p.name, COUNT(pu.id) as sales_count
                FROM products p
                LEFT JOIN purchases pu ON p.id = pu.product_id
                WHERE DATE(pu.purchase_date) >= DATE('now', 'start of month')
                GROUP BY p.id, p.name
                ORDER BY sales_count DESC
                LIMIT ?
            ''', (limit,))
        
        elif ranking_type == 'recharges':
            cursor.execute('''
                SELECT u.first_name, COALESCE(SUM(t.amount), 0) as total_recharges
                FROM users u
                LEFT JOIN transactions t ON u.user_id = t.user_id
                WHERE t.transaction_type = 'recharge' AND t.status = 'completed'
                AND DATE(t.created_date) >= DATE('now', 'start of month')
                GROUP BY u.user_id, u.first_name
                ORDER BY total_recharges DESC
                LIMIT ?
            ''', (limit,))
        
        elif ranking_type == 'purchases':
            cursor.execute('''
                SELECT u.first_name, COUNT(p.id) as purchase_count
                FROM users u
                LEFT JOIN purchases p ON u.user_id = p.user_id
                WHERE DATE(p.purchase_date) >= DATE('now', 'start of month')
                GROUP BY u.user_id, u.first_name
                ORDER BY purchase_count DESC
                LIMIT ?
            ''', (limit,))
        
        elif ranking_type == 'giftcards':
            cursor.execute('''
                SELECT u.first_name, COALESCE(SUM(g.amount), 0) as total_giftcards
                FROM users u
                LEFT JOIN gift_cards g ON u.user_id = g.used_by
                WHERE g.is_used = 1
                GROUP BY u.user_id, u.first_name
                ORDER BY total_giftcards DESC
                LIMIT ?
            ''', (limit,))
        
        elif ranking_type == 'balance':
            cursor.execute('''
                SELECT first_name, balance
                FROM users
                ORDER BY balance DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    # ===== MÉTODOS DE CONFIGURAÇÕES =====
    
    def get_setting(self, key: str) -> Optional[str]:
        """Busca uma configuração"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT setting_value FROM bot_settings WHERE setting_key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def set_setting(self, key: str, value: str) -> bool:
        """Define uma configuração"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO bot_settings (setting_key, setting_value, updated_date)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        return affected_rows > 0
    
    # ===== MÉTODOS DE LOGS =====
    
    def add_log(self, user_id: int, action: str, details: str = "") -> bool:
        """Adiciona um log"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (user_id, action, details)
            VALUES (?, ?, ?)
        ''', (user_id, action, details))
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        return affected_rows > 0