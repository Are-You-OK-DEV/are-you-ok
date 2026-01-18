import os
from app import create_app, db

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
    app.run(debug=True, host='0.0.0.0', port=5000)
