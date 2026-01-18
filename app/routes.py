from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_wtf import FlaskForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

class RegisterForm(FlaskForm):
    """注册表单"""
    email = StringField('邮箱', validators=[
        DataRequired('邮箱不能为空'),
        Email('请输入有效的邮箱地址')
    ])
    username = StringField('用户名', validators=[
        DataRequired('用户名不能为空'),
        Length(min=3, max=20, message='用户名长度需要在3-20之间')
    ])
    password = PasswordField('密码', validators=[
        DataRequired('密码不能为空'),
        Length(min=6, message='密码长度至少6个字符')
    ])
    password_confirm = PasswordField('确认密码', validators=[
        DataRequired('确认密码不能为空'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('注册')
    
    def validate_email(self, field):
        """验证邮箱是否已存在"""
        from app.models import User
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')
    
    def validate_username(self, field):
        """验证用户名是否已存在"""
        from app.models import User
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用')

class LoginForm(FlaskForm):
    """登录表单"""
    email = StringField('邮箱', validators=[
        DataRequired('邮箱不能为空'),
        Email('请输入有效的邮箱地址')
    ])
    password = PasswordField('密码', validators=[
        DataRequired('密码不能为空')
    ])
    submit = SubmitField('登录')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        from app import db
        from app.models import User
        
        # 创建新用户
        user = User(
            email=form.email.data,
            username=form.username.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        from app.models import User
        
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('邮箱或密码错误', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        flash(f'欢迎回来，{user.username}！', 'success')
        
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('已登出', 'success')
    return redirect(url_for('auth.login'))
