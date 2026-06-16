import sqlite3
import json
from datetime import datetime
import config

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(config.DB_FILE)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        """إنشء جداول قاعدة البيانات"""
        
        # جدول المستخدمين
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                purchase_count INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0
            )
        ''')
        
        # جدول الأسعار
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                product_id TEXT PRIMARY KEY,
                product_name TEXT,
                price REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول طرق الدفع
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_methods (
                method_id TEXT PRIMARY KEY,
                method_name TEXT,
                method_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الرسائل المخصصة
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                message_content TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المعاملات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product TEXT,
                amount REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        self.conn.commit()
        self._init_default_data()

    def _init_default_data(self):
        """تهيئة البيانات الافتراضية"""
        for product_id, price in config.DEFAULT_PRICES.items():
            self.cursor.execute('''
                INSERT OR IGNORE INTO prices (product_id, product_name, price)
                VALUES (?, ?, ?)
            ''', (product_id, product_id.title(), price))
        
        for method_id, (method_name, value) in [
            ("syriatel", ("Syriatel Cash", config.DEFAULT_PAYMENT["syriatel"])),
            ("cham", ("Cham Cash", config.DEFAULT_PAYMENT["cham"])),
            ("usdt", ("USDT BEP20", config.DEFAULT_PAYMENT["usdt"]))
        ]:
            self.cursor.execute('''
                INSERT OR IGNORE INTO payment_methods (method_id, method_name, method_value)
                VALUES (?, ?, ?)
            ''', (method_id, method_name, value))
        
        self.conn.commit()

    # ===== عمليات المستخدمين =====
    def add_user(self, user_id, username, first_name):
        """إضافة مستخدم جديد"""
        self.cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        self.conn.commit()

    def get_user_count(self):
        """الحصول على عدد المستخدمين"""
        self.cursor.execute('SELECT COUNT(*) FROM users')
        return self.cursor.fetchone()[0]

    def get_users_stats(self):
        """إحصائيات المستخدمين"""
        self.cursor.execute('''
            SELECT COUNT(*), SUM(total_spent) FROM users
        ''')
        count, total = self.cursor.fetchone()
        return {"total_users": count or 0, "total_revenue": total or 0}

    # ===== عمليات الأسعار =====
    def update_price(self, product_id, new_price):
        """تحديث سعر منتج"""
        self.cursor.execute('''
            UPDATE prices SET price = ?, updated_at = CURRENT_TIMESTAMP
            WHERE product_id = ?
        ''', (new_price, product_id))
        self.conn.commit()

    def get_prices(self):
        """الحصول على جميع الأسعار"""
        self.cursor.execute('SELECT product_id, price FROM prices')
        return {row[0]: row[1] for row in self.cursor.fetchall()}

    def get_price(self, product_id):
        """الحصول على سعر منتج"""
        self.cursor.execute('SELECT price FROM prices WHERE product_id = ?', (product_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # ===== عمليات طرق الدفع =====
    def update_payment_method(self, method_id, method_value):
        """تحديث طريقة دفع"""
        self.cursor.execute('''
            UPDATE payment_methods SET method_value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE method_id = ?
        ''', (method_value, method_id))
        self.conn.commit()

    def get_payment_methods(self):
        """الحصول على جميع طرق الدفع"""
        self.cursor.execute('SELECT method_id, method_name, method_value FROM payment_methods')
        return {row[0]: {"name": row[1], "value": row[2]} for row in self.cursor.fetchall()}

    # ===== عمليات الرسائل =====
    def update_message(self, message_id, content):
        """تحديث رسالة"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO messages (message_id, message_content, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (message_id, content))
        self.conn.commit()

    def get_message(self, message_id):
        """الحصول على رسالة"""
        self.cursor.execute('SELECT message_content FROM messages WHERE message_id = ?', (message_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        """إغلاق الاتصال"""
        self.conn.close()

# إنشاء مثيل من قاعدة البيانات
db = Database()
