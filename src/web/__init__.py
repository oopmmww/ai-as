"""Web and API modules"""

from .routes import app
from .dashboard_route import register_dashboard_route

__all__ = [
    'app',
    'register_dashboard_route',
]
