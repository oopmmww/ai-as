"""
dashboard_route.py
Route สำหรับเข้าถึง dashboard HTML

ใช้ใน main.py:
    from dashboard_route import register_dashboard_route
    register_dashboard_route(app)
"""

from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def show_dashboard():
    """แสดง Dashboard"""
    return render_template('dashboard.html')


@dashboard_bp.route('/')
def index_redirect():
    """Redirect / ไปที่ dashboard"""
    return render_template('dashboard.html')


def register_dashboard_route(app):
    """ลงทะเบียน dashboard routes ใน Flask app"""
    app.register_blueprint(dashboard_bp)
