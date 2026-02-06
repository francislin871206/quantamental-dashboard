"""
Virtual Trading Engine
Simulates paper trading with portfolio tracking, order management, and P&L calculation.
Data is persisted to SQLite database.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import pandas as pd
import yfinance as yf


@dataclass
class Order:
    """Represents a trading order"""
    id: Optional[int]
    ticker: str
    order_type: str  # 'buy' or 'sell'
    quantity: int
    price: float
    timestamp: datetime
    status: str  # 'filled', 'pending', 'cancelled'
    strategy: str


@dataclass
class Position:
    """Represents a portfolio position"""
    ticker: str
    quantity: int
    avg_cost: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_pct: float


class VirtualTradingEngine:
    """Paper trading simulation engine with persistent storage"""
    
    def __init__(self, db_path: str = "virtual_trading.db", initial_cash: float = 100000):
        self.db_path = db_path
        self.initial_cash = initial_cash
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                cash_balance REAL DEFAULT 100000,
                initial_cash REAL DEFAULT 100000
            )
        """)
        
        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                order_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                strategy TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                avg_cost REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, ticker)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, password: str) -> Optional[int]:
        """Create a new user account"""
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, created_at, cash_balance, initial_cash)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, datetime.now().isoformat(), self.initial_cash, self.initial_cash))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        """Authenticate user and return user_id if successful"""
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM users WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_user_balance(self, user_id: int) -> float:
        """Get user's cash balance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT cash_balance FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0
    
    def get_current_price(self, ticker: str) -> float:
        """Fetch current price from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
        except Exception:
            pass
        return 0.0
    
    def place_order(self, user_id: int, ticker: str, order_type: str, 
                    quantity: int, strategy: str = "Manual") -> Dict[str, Any]:
        """Place a buy or sell order"""
        current_price = self.get_current_price(ticker)
        if current_price == 0:
            return {"success": False, "error": f"Could not fetch price for {ticker}"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current balance
        cursor.execute("SELECT cash_balance FROM users WHERE id = ?", (user_id,))
        cash_balance = cursor.fetchone()[0]
        
        total_cost = current_price * quantity
        
        if order_type == 'buy':
            if total_cost > cash_balance:
                conn.close()
                return {"success": False, "error": "Insufficient funds"}
            
            # Update cash balance
            cursor.execute("""
                UPDATE users SET cash_balance = cash_balance - ? WHERE id = ?
            """, (total_cost, user_id))
            
            # Update or insert position
            cursor.execute("""
                SELECT quantity, avg_cost FROM positions WHERE user_id = ? AND ticker = ?
            """, (user_id, ticker))
            existing = cursor.fetchone()
            
            if existing:
                old_qty, old_avg = existing
                new_qty = old_qty + quantity
                new_avg = ((old_qty * old_avg) + (quantity * current_price)) / new_qty
                cursor.execute("""
                    UPDATE positions SET quantity = ?, avg_cost = ? WHERE user_id = ? AND ticker = ?
                """, (new_qty, new_avg, user_id, ticker))
            else:
                cursor.execute("""
                    INSERT INTO positions (user_id, ticker, quantity, avg_cost) VALUES (?, ?, ?, ?)
                """, (user_id, ticker, quantity, current_price))
        
        elif order_type == 'sell':
            # Check if user has enough shares
            cursor.execute("""
                SELECT quantity FROM positions WHERE user_id = ? AND ticker = ?
            """, (user_id, ticker))
            existing = cursor.fetchone()
            
            if not existing or existing[0] < quantity:
                conn.close()
                return {"success": False, "error": "Insufficient shares"}
            
            # Update cash balance
            cursor.execute("""
                UPDATE users SET cash_balance = cash_balance + ? WHERE id = ?
            """, (total_cost, user_id))
            
            # Update position
            new_qty = existing[0] - quantity
            if new_qty == 0:
                cursor.execute("""
                    DELETE FROM positions WHERE user_id = ? AND ticker = ?
                """, (user_id, ticker))
            else:
                cursor.execute("""
                    UPDATE positions SET quantity = ? WHERE user_id = ? AND ticker = ?
                """, (new_qty, user_id, ticker))
        
        # Record the order
        cursor.execute("""
            INSERT INTO orders (user_id, ticker, order_type, quantity, price, timestamp, status, strategy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, ticker, order_type, quantity, current_price, 
              datetime.now().isoformat(), 'filled', strategy))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "order_type": order_type,
            "ticker": ticker,
            "quantity": quantity,
            "price": current_price,
            "total": total_cost
        }
    
    def get_positions(self, user_id: int) -> List[Position]:
        """Get all positions for a user with current prices"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ticker, quantity, avg_cost FROM positions WHERE user_id = ?
        """, (user_id,))
        
        positions = []
        for row in cursor.fetchall():
            ticker, quantity, avg_cost = row
            current_price = self.get_current_price(ticker)
            unrealized_pnl = (current_price - avg_cost) * quantity
            unrealized_pnl_pct = ((current_price / avg_cost) - 1) * 100 if avg_cost > 0 else 0
            
            positions.append(Position(
                ticker=ticker,
                quantity=quantity,
                avg_cost=avg_cost,
                current_price=current_price,
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_pct=unrealized_pnl_pct
            ))
        
        conn.close()
        return positions
    
    def get_orders(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get order history for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, ticker, order_type, quantity, price, timestamp, status, strategy
            FROM orders WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?
        """, (user_id, limit))
        
        orders = []
        for row in cursor.fetchall():
            orders.append({
                'id': row[0],
                'ticker': row[1],
                'order_type': row[2],
                'quantity': row[3],
                'price': row[4],
                'timestamp': row[5],
                'status': row[6],
                'strategy': row[7]
            })
        
        conn.close()
        return orders
    
    def get_portfolio_value(self, user_id: int) -> Dict[str, float]:
        """Calculate total portfolio value"""
        cash = self.get_user_balance(user_id)
        positions = self.get_positions(user_id)
        
        total_position_value = sum(p.current_price * p.quantity for p in positions)
        total_value = cash + total_position_value
        
        # Get initial cash for P&L calculation
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT initial_cash FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        initial_cash = result[0] if result else self.initial_cash
        conn.close()
        
        total_pnl = total_value - initial_cash
        total_pnl_pct = ((total_value / initial_cash) - 1) * 100 if initial_cash > 0 else 0
        
        return {
            'cash': cash,
            'positions_value': total_position_value,
            'total_value': total_value,
            'initial_cash': initial_cash,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct
        }
    
    def reset_account(self, user_id: int):
        """Reset user's account to initial state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Reset cash
        cursor.execute("""
            UPDATE users SET cash_balance = initial_cash WHERE id = ?
        """, (user_id,))
        
        # Delete all positions
        cursor.execute("DELETE FROM positions WHERE user_id = ?", (user_id,))
        
        # Delete all orders
        cursor.execute("DELETE FROM orders WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
