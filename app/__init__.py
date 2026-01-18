from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from app.logger import setup_logger, get_logger

db = SQLAlchemy()
login_manager = LoginManager()

# 初始化日志
setup_logger()
logger = get_logger()

def create_app():
    app = Flask(__name__)
    logger.info("开始创建Flask应用...")
    
    # 配置
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = 'your-secret-key-change-this'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'diary.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    logger.info("Flask扩展已初始化")
    
    with app.app_context():
        # 导入模型定义（在应用上下文中，在初始化后）
        from app.models import User, Diary, DailyStats
        
        # 创建数据库表
        db.create_all()
        logger.info("数据库表已创建或已存在")
        
        # 设置 user_loader
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
    
    # 注册蓝图
    from app.routes import auth_bp
    from app.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    logger.info("蓝图已注册")
    
    # 记录应用启动成功
    logger.info("Flask应用创建完成，服务启动就绪")
    
    return app

