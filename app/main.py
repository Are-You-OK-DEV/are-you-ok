from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from calendar import monthcalendar, month_name
import calendar
from app.logger import get_logger

logger = get_logger()

main_bp = Blueprint('main', __name__)

# 延迟导入以避免循环导入
def _get_models():
    from app import db
    from app.models import Diary, DailyStats, User
    return db, Diary, DailyStats, User

@main_bp.route('/')
def index():
    """首页"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """仪表板 - 显示今日日记和日历"""
    db, Diary, DailyStats, User = _get_models()
    today = date.today()
    
    # 获取今天的日记
    today_diary = Diary.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    # 获取总日记数
    total_diaries = Diary.query.filter_by(user_id=current_user.id).count()
    
    # 获取本月数据
    current_year = today.year
    current_month = today.month
    
    # 获取本月所有日记数据
    month_start = date(current_year, current_month, 1)
    if current_month == 12:
        month_end = date(current_year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(current_year, current_month + 1, 1) - timedelta(days=1)
    
    month_diaries = Diary.query.filter(
        Diary.user_id == current_user.id,
        Diary.date >= month_start,
        Diary.date <= month_end
    ).all()
    
    # 构建日历数据
    cal = monthcalendar(current_year, current_month)
    diary_map = {diary.date: diary for diary in month_diaries}
    
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                day_date = date(current_year, current_month, day)
                diary = diary_map.get(day_date)
                week_data.append({
                    'day': day,
                    'date': day_date,
                    'diary': diary,
                    'is_today': day_date == today,
                    'mood': diary.mood if diary else None,
                    'mood_emoji': diary.get_mood_emoji() if diary else ''
                })
        calendar_data.append(week_data)
    
    return render_template('index.html',
                          today_diary=today_diary,
                          today=today,
                          calendar_data=calendar_data,
                          month_name=month_name[current_month],
                          year=current_year,
                          month=current_month,
                          total_diaries=total_diaries)

@main_bp.route('/diary/new', methods=['GET', 'POST'])
@login_required
def new_diary():
    """创建或编辑今天的日记"""
    db, Diary, DailyStats, User = _get_models()
    today = date.today()
    
    # 检查是否已有今天的日记
    diary = Diary.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        mood = request.form.get('mood', 3, type=int)
        
        if not title or not content:
            logger.warning(f"用户 {current_user.username} 尝试保存空日记")
            flash('标题和内容不能为空', 'danger')
            return redirect(url_for('main.new_diary'))
        
        # 确保心情分数在1-5之间
        mood = max(1, min(5, mood))
        
        if diary:
            # 更新现有日记
            diary.title = title
            diary.content = content
            diary.mood = mood
            diary.mood_label = _get_mood_label(mood)
            logger.info(f"用户 {current_user.username} 更新日记 (ID: {diary.id}), 心情: {mood}")
            flash('日记已更新', 'success')
        else:
            # 创建新日记
            diary = Diary(
                user_id=current_user.id,
                title=title,
                content=content,
                mood=mood,
                mood_label=_get_mood_label(mood),
                date=today
            )
            db.session.add(diary)
            logger.info(f"用户 {current_user.username} 创建新日记, 标题: {title}, 心情: {mood}")
            flash('日记已保存', 'success')
        
        # 更新或创建每日统计
        stats = DailyStats.query.filter_by(
            user_id=current_user.id,
            date=today
        ).first()
        
        if stats:
            stats.mood_score = mood
            stats.has_diary = True
        else:
            stats = DailyStats(
                user_id=current_user.id,
                date=today,
                mood_score=mood,
                has_diary=True
            )
            db.session.add(stats)
        
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    
    return render_template('diary.html', diary=diary, today=today)

@main_bp.route('/diary/<int:diary_id>')
@login_required
def view_diary(diary_id):
    """查看日记详情"""
    db, Diary, DailyStats, User = _get_models()
    diary = Diary.query.get_or_404(diary_id)
    
    # 检查权限
    if diary.user_id != current_user.id:
        flash('您没有权限查看这篇日记', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('diary_detail.html', diary=diary)

@main_bp.route('/calendar')
@login_required
def calendar_view():
    """日历视图"""
    db, Diary, DailyStats, User = _get_models()
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)
    
    # 验证年月有效性
    if month < 1 or month > 12:
        month = date.today().month
    if year < 2000 or year > 2100:
        year = date.today().year
    
    # 获取该月的所有日记
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)
    
    month_diaries = Diary.query.filter(
        Diary.user_id == current_user.id,
        Diary.date >= month_start,
        Diary.date <= month_end
    ).all()
    
    # 构建日历数据
    cal = monthcalendar(year, month)
    diary_map = {diary.date: diary for diary in month_diaries}
    today = date.today()
    
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                day_date = date(year, month, day)
                diary = diary_map.get(day_date)
                week_data.append({
                    'day': day,
                    'date': day_date,
                    'diary': diary,
                    'is_today': day_date == today,
                    'mood': diary.mood if diary else None,
                    'mood_emoji': diary.get_mood_emoji() if diary else '',
                    'title_preview': diary.title[:20] if diary else ''
                })
        calendar_data.append(week_data)
    
    # 计算前后月份
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # 统计数据
    total_days_with_diary = len(month_diaries)
    mood_stats = _calculate_mood_stats(month_diaries)
    
    return render_template('calendar.html',
                          calendar_data=calendar_data,
                          month_name=month_name[month],
                          year=year,
                          month=month,
                          prev_month=prev_month,
                          prev_year=prev_year,
                          next_month=next_month,
                          next_year=next_year,
                          total_days=total_days_with_diary,
                          mood_stats=mood_stats)

@main_bp.route('/stats')
@login_required
def stats():
    """统计页面"""
    db, Diary, DailyStats, User = _get_models()
    # 获取近30天的数据
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    
    diaries = Diary.query.filter(
        Diary.user_id == current_user.id,
        Diary.date >= thirty_days_ago,
        Diary.date <= today
    ).all()
    
    # 计算统计数据
    mood_stats = _calculate_mood_stats(diaries)
    
    # 近30天日记数
    diary_count = len(diaries)
    
    # 平均心情分数
    if diaries:
        avg_mood = sum(d.mood for d in diaries) / len(diaries)
    else:
        avg_mood = 0
    
    # 按日期统计
    date_stats = []
    for i in range(30):
        check_date = today - timedelta(days=29 - i)
        diary = next((d for d in diaries if d.date == check_date), None)
        date_stats.append({
            'date': check_date,
            'has_diary': diary is not None,
            'mood': diary.mood if diary else 0
        })
    
    return render_template('stats.html',
                          mood_stats=mood_stats,
                          diary_count=diary_count,
                          avg_mood=round(avg_mood, 1),
                          date_stats=date_stats)

@main_bp.route('/profile')
@login_required
def profile():
    """用户个人资料页面"""
    db, Diary, DailyStats, User = _get_models()
    # 获取用户统计数据
    total_diaries = Diary.query.filter_by(user_id=current_user.id).count()
    
    # 获取第一篇日记日期
    first_diary = Diary.query.filter_by(user_id=current_user.id).order_by(Diary.date).first()
    first_diary_date = first_diary.date if first_diary else None
    
    # 计算连续记录天数
    today = date.today()
    streak = 0
    check_date = today
    
    while True:
        diary = Diary.query.filter_by(
            user_id=current_user.id,
            date=check_date
        ).first()
        
        if diary:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
        
        if streak > 365:  # 防止无限循环
            break
    
    return render_template('profile.html',
                          total_diaries=total_diaries,
                          first_diary_date=first_diary_date,
                          streak=streak,
                          user=current_user,
                          now=datetime.utcnow())

@main_bp.route('/api/mood-data')
@login_required
def api_mood_data():
    """API: 获取心情数据用于图表"""
    db, Diary, DailyStats, User = _get_models()
    days = request.args.get('days', 30, type=int)
    today = date.today()
    start_date = today - timedelta(days=days-1)
    
    diaries = Diary.query.filter(
        Diary.user_id == current_user.id,
        Diary.date >= start_date,
        Diary.date <= today
    ).all()
    
    data = []
    for i in range(days):
        check_date = start_date + timedelta(days=i)
        diary = next((d for d in diaries if d.date == check_date), None)
        data.append({
            'date': check_date.isoformat(),
            'mood': diary.mood if diary else None,
            'has_diary': diary is not None
        })
    
    return jsonify(data)

def _get_mood_label(mood):
    """获取心情标签"""
    labels = {
        1: '很糟糕',
        2: '不太好',
        3: '一般',
        4: '不错',
        5: '很棒'
    }
    return labels.get(mood, '一般')

def _calculate_mood_stats(diaries):
    """计算心情统计"""
    stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for diary in diaries:
        stats[diary.mood] += 1
    return stats
