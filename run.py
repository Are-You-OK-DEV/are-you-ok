import os
from app import create_app, db
from app.logger import get_logger

logger = get_logger()
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': __import__('app.db', fromlist=['User']).User,
        'Diary': __import__('app.db', fromlist=['Diary']).Diary,
        'DailyStats': __import__('app.db', fromlist=['DailyStats']).DailyStats,
    }

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("应用启动，监听地址: http://0.0.0.0:5000")
    logger.info("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
