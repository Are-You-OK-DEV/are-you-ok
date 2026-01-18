from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_login import UserMixin
from app import db
import secrets


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 邮箱验证相关
    is_verified = db.Column(db.Boolean, default=False)
    verify_code = db.Column(db.String(6))
    verify_code_expires = db.Column(db.DateTime)
    
    # 关系
    diaries = db.relationship('Diary', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password_hash, password)
    
    def generate_verify_code(self):
        """生成邮箱验证码"""
        self.verify_code = ''.join([str(i) for i in secrets.SystemRandom().sample(range(10), 6)])
        self.verify_code_expires = datetime.utcnow() + timedelta(minutes=15)
        return self.verify_code
    
    def is_verify_code_valid(self, code):
        """验证验证码是否有效"""
        return (self.verify_code == code and 
                self.verify_code_expires and 
                datetime.utcnow() < self.verify_code_expires)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Diary(db.Model):
    """日记模型"""
    __tablename__ = 'diaries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mood = db.Column(db.Integer, nullable=False)  # 1-5 分数
    mood_label = db.Column(db.String(20))  # 心情标签
    date = db.Column(db.Date, nullable=False, index=True)  # 日记日期
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 为同一用户同一日期建立唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='unique_user_date'),
    )
    
    def get_mood_emoji(self):
        """获取心情emoji"""
        moods = {
            1: '😢 很糟糕',
            2: '😕 不太好',
            3: '😐 一般',
            4: '😊 不错',
            5: '😄 很棒'
        }
        return moods.get(self.mood, '')
    
    def __repr__(self):
        return f'<Diary {self.title}>'


class DailyStats(db.Model):
    """每日统计模型（用于日历显示优化）"""
    __tablename__ = 'daily_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)  # 日期
    mood_score = db.Column(db.Integer)  # 当天心情分数
    has_diary = db.Column(db.Boolean, default=False)  # 是否有日记
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 为同一用户同一日期建立唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='unique_stats_user_date'),
    )
    
    def __repr__(self):
        return f'<DailyStats {self.date}>'
