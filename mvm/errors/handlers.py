from flask import Blueprint, render_template
from mvm.models import Item

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    return render_template('errors/404.html', itemsall=itemsall), 404


@errors.app_errorhandler(403)
def error_403(error):
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    return render_template('errors/403.html', itemsall=itemsall), 403


@errors.app_errorhandler(500)
def error_500(error):
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    return render_template('errors/500.html', itemsall=itemsall), 500
