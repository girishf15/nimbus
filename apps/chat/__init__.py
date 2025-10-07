from flask import Blueprint

# Serve blueprint static files under /static/chat
chat_bp = Blueprint('chat', __name__, template_folder='templates', static_folder='static', static_url_path='/static/chat')

from . import routes
