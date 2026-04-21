# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from urllib.parse import urlparse
import re

auth_bp = Blueprint('auth', __name__)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('', 'http', 'https') and ref_url.netloc == test_url.netloc

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if next_page and not is_safe_url(next_page):
                return redirect(url_for('dashboard.index'))
            return redirect(next_page or url_for('dashboard.index'))
        flash('Nome de utilizador ou palavra-passe inválidos.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validação simples de email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not username or not email or not password:
            flash('Todos os campos são obrigatórios.', 'warning')
        elif not re.match(email_regex, email):
            flash('Endereço de email inválido.', 'warning')
        elif User.query.filter_by(username=username).first():
            flash('Nome de utilizador já em uso.', 'warning')
        elif User.query.filter_by(email=email).first():
            flash('Email já registado.', 'warning')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Conta criada com sucesso. Por favor inicie sessão.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sessão terminada.', 'info')
    return redirect(url_for('auth.login'))
