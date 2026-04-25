# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint
config_bp = Blueprint('config', __name__)
from app.config import routes
