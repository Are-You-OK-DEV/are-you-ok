from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from flask_wtf import FlaskForm
from app import mail
from flask_mail import Message

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

class VerifyEmailForm(FlaskForm):
    """邮箱验证表单"""
    verify_code = IntegerField('验证码', validators=[
        DataRequired('验证码不能为空'),
        NumberRange(min=0, max=999999, message='验证码格式不正确')
    ])
    submit = SubmitField('验证')

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

def send_verify_email(user, verify_code):
    """发送验证邮件"""
    try:
        msg = Message(
            subject='邮箱验证码 - Are You OK',
            recipients=[user.email],
            html=f'''
            <h2>欢迎注册 Are You OK</h2>
            <p>您的邮箱验证码是：</p>
            <h1 style="color: #007bff; font-size: 2em;">{verify_code}</h1>
            <p>验证码有效期为 15 分钟，请勿分享给他人。</p>
            <p>如果您未进行此操作，请忽略此邮件。</p>
            ''',
            body=f'您的邮箱验证码是：{verify_code}，有效期为 15 分钟。'
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f'邮件发送失败：{e}')
        return False

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
            username=form.username.data,
            is_verified=False
        )
        user.set_password(form.password.data)
        
        # 生成验证码
        verify_code = user.generate_verify_code()
        
        db.session.add(user)
        db.session.commit()
        
        # 发送验证邮件
        if send_verify_email(user, verify_code):
            flash('注册成功！验证码已发送到您的邮箱，请检查邮件进行验证', 'success')
            return redirect(url_for('auth.verify_email', email=user.email))
        else:
            db.session.delete(user)
            db.session.commit()
            flash('邮件发送失败，请重试', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/verify-email/<email>', methods=['GET', 'POST'])
def verify_email(email):
    """邮箱验证"""
    from app.models import User
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('auth.register'))
    
    if user.is_verified:
        flash('邮箱已验证，请直接登录', 'info')
        return redirect(url_for('auth.login'))
    
    form = VerifyEmailForm()
    
    if form.validate_on_submit():
        verify_code = str(form.verify_code.data).zfill(6)
        
        if user.is_verify_code_valid(verify_code):
            user.is_verified = True
            user.verify_code = None
            user.verify_code_expires = None
            from app import db
            db.session.commit()
            
            flash('邮箱验证成功！请登录', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('验证码无效或已过期，请重新输入', 'danger')
    
    return render_template('verify_email.html', form=form, email=email)

@auth_bp.route('/resend-verify-code/<email>')
def resend_verify_code(email):
    """重新发送验证码"""
    from app.models import User
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('auth.register'))
    
    if user.is_verified:
        flash('邮箱已验证', 'info')
        return redirect(url_for('auth.login'))
    
    # 生成新验证码
    verify_code = user.generate_verify_code()
    from app import db
    db.session.commit()
    
    # 发送验证邮件
    if send_verify_email(user, verify_code):
        flash('新的验证码已发送到您的邮箱', 'success')
    else:
        flash('邮件发送失败，请重试', 'danger')
    
    return redirect(url_for('auth.verify_email', email=email))

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
        
        if not user.is_verified:
            flash('邮箱未验证，请先完成邮箱验证', 'warning')
            return redirect(url_for('auth.verify_email', email=user.email))
        
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
