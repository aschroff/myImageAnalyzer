from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from flask_babel import gettext
from mvm import db, rekognition
from mvm.items.forms import CreateItemForm
from mvm.models import User, Item, ItemKeyword, Keyword
from mvm.items.utils import save_item, save_thumbnail, get_image_from_file
from sqlalchemy import func 


analytics = Blueprint('analytics', __name__)


@analytics.route("/keywords")
def keywords():
    page = request.args.get('page', 1, type=int)
    keywordstest = db.session.query(func.count(ItemKeyword.item_id).label('countitems'), Keyword.id, Keyword.keywordtextname).group_by(ItemKeyword.keyword_id).join(Keyword)
    k = keywordstest.paginate(page=page, per_page=10)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    return render_template('keywords.html', keywords=k, itemsall=itemsall)  


@analytics.route("/keyword/<string:keywordtextname>")
def keyword_items(keywordtextname):
    page = request.args.get('page', 1, type=int)
    keyword = Keyword.query.filter_by(keywordtextname=keywordtextname).first_or_404()    
    item_keywords = ItemKeyword.query.filter_by(reference=keyword).order_by(ItemKeyword.date_analysis.desc()).paginate(page=page, per_page=4)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    return render_template('keyword_items.html', item_keywords=item_keywords, keyword=keyword, itemsall=itemsall)


    
