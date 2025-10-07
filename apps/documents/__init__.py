from flask import Blueprint

documents_bp = Blueprint('documents', __name__, template_folder='templates', static_folder='static', static_url_path='/static/documents')

from . import routes
