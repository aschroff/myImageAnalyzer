from flask import Blueprint
from flask import render_template, request
from mvm import db
from mvm.models import Item

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    items = Item.query.order_by(Item.date_posted.desc()).paginate(page=page, per_page=4)
    return render_template('home.html', items=items)


@main.route("/about")
def about():
    db.drop_all()
    db.create_all()
    
    return render_template('about.html', title='About')
