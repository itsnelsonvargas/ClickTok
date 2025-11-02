"""
Database Management for ClickTok
Handles product storage, video tracking, and analytics
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """Manages all database operations for ClickTok"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def connect(self):
        """Establish database connection"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def init_database(self):
        """Create tables if they don't exist"""
        conn = self.connect()
        cursor = conn.cursor()

        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                commission_rate REAL,
                commission_amount REAL,
                category TEXT,
                rating REAL,
                image_url TEXT,
                affiliate_link TEXT NOT NULL,
                product_url TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                notes TEXT
            )
        """)

        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                video_path TEXT NOT NULL,
                caption TEXT,
                hashtags TEXT,
                tiktok_url TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_posted TIMESTAMP,
                status TEXT DEFAULT 'created',
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        """)

        # Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                views INTEGER,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                clicks INTEGER,
                conversions INTEGER,
                revenue REAL,
                FOREIGN KEY (video_id) REFERENCES videos(id)
            )
        """)

        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.info("Database initialized successfully")

    def add_product(self, product_data: Dict) -> int:
        """Add a new product to the database"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO products (
                    product_id, name, description, price, commission_rate,
                    commission_amount, category, rating, image_url,
                    affiliate_link, product_url, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data.get('product_id'),
                product_data.get('name'),
                product_data.get('description'),
                product_data.get('price'),
                product_data.get('commission_rate'),
                product_data.get('commission_amount'),
                product_data.get('category'),
                product_data.get('rating'),
                product_data.get('image_url'),
                product_data.get('affiliate_link'),
                product_data.get('product_url'),
                product_data.get('status', 'pending')
            ))
            conn.commit()
            logger.info(f"Added product: {product_data.get('name')}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Product already exists: {product_data.get('product_id')}")
            return -1

    def get_products(self, status: Optional[str] = None) -> List[Dict]:
        """Retrieve products, optionally filtered by status"""
        conn = self.connect()
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT * FROM products WHERE status = ? ORDER BY date_added DESC", (status,))
        else:
            cursor.execute("SELECT * FROM products ORDER BY date_added DESC")

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def update_product_status(self, product_id: str, status: str):
        """Update product status"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET status = ? WHERE product_id = ?", (status, product_id))
        conn.commit()
    
    def delete_product(self, product_id: str) -> bool:
        """Delete a product from the database"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            conn.commit()
            logger.info(f"Deleted product: {product_id}")
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            return False

    def add_video(self, video_data: Dict) -> int:
        """Add a generated video to the database"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO videos (
                product_id, video_path, caption, hashtags, status
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            video_data.get('product_id'),
            video_data.get('video_path'),
            video_data.get('caption'),
            video_data.get('hashtags'),
            video_data.get('status', 'created')
        ))
        conn.commit()
        logger.info(f"Added video for product: {video_data.get('product_id')}")
        return cursor.lastrowid

    def update_video_post(self, video_id: int, tiktok_url: str):
        """Update video after posting to TikTok"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE videos
            SET tiktok_url = ?, date_posted = ?, status = 'posted'
            WHERE id = ?
        """, (tiktok_url, datetime.now(), video_id))
        conn.commit()

    def get_videos(self, status: Optional[str] = None) -> List[Dict]:
        """Retrieve videos"""
        conn = self.connect()
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT * FROM videos WHERE status = ? ORDER BY date_created DESC", (status,))
        else:
            cursor.execute("SELECT * FROM videos ORDER BY date_created DESC")

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_daily_post_count(self) -> int:
        """Get number of posts today"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count FROM videos
            WHERE date(date_posted) = date('now') AND status = 'posted'
        """)
        result = cursor.fetchone()
        return result['count'] if result else 0

    def add_analytics(self, analytics_data: Dict):
        """Add analytics data"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analytics (
                video_id, views, likes, comments, shares, clicks, conversions, revenue
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analytics_data.get('video_id'),
            analytics_data.get('views', 0),
            analytics_data.get('likes', 0),
            analytics_data.get('comments', 0),
            analytics_data.get('shares', 0),
            analytics_data.get('clicks', 0),
            analytics_data.get('conversions', 0),
            analytics_data.get('revenue', 0.0)
        ))
        conn.commit()

    def get_stats(self) -> Dict:
        """Get overall statistics"""
        conn = self.connect()
        cursor = conn.cursor()

        stats = {}

        # Total products
        cursor.execute("SELECT COUNT(*) as count FROM products")
        stats['total_products'] = cursor.fetchone()['count']

        # Total videos
        cursor.execute("SELECT COUNT(*) as count FROM videos")
        stats['total_videos'] = cursor.fetchone()['count']

        # Posted videos
        cursor.execute("SELECT COUNT(*) as count FROM videos WHERE status = 'posted'")
        stats['posted_videos'] = cursor.fetchone()['count']

        # Total views, likes, etc.
        cursor.execute("""
            SELECT SUM(views) as views, SUM(likes) as likes,
                   SUM(comments) as comments, SUM(shares) as shares
            FROM videos WHERE status = 'posted'
        """)
        engagement = cursor.fetchone()
        stats['total_views'] = engagement['views'] or 0
        stats['total_likes'] = engagement['likes'] or 0
        stats['total_comments'] = engagement['comments'] or 0
        stats['total_shares'] = engagement['shares'] or 0

        return stats

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
