from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from flask_babel import gettext
from mvm import db, rekognition
from mvm.items.forms import CreateItemForm
from mvm.models import User, Item, ItemKeyword, Keyword
from mvm.items.utils import save_item, save_thumbnail, get_image_from_file


analytics = Blueprint('analytics', __name__)


@analytics.route("/keywords")
def keywords():
    page = request.args.get('page', 1, type=int)
#    keywordstest = db.session.query(ItemKeyword).join(ItemKeyword, Keyword.itemkeywords)    
#    keywordstest1 = keywordstest.order_by(Keyword.keywordtextname.asc()).paginate(page=page, per_page=10)
#    keywordstest = db.session.query(ItemKeyword).join(ItemKeyword, Keyword.itemkeywords)
#    keywordstest1 = keywordstest.order_by(Keyword.keywordtextname.asc()).paginate(page=page, per_page=10)
#    print('keywordstest')
#    print(keywordstest1.items)
    keywords = Keyword.query.order_by(Keyword.keywordtextname.asc()).paginate(page=page, per_page=10)
    itemsall = Item.query.order_by(Item.date_posted.desc())
    return render_template('keywords.html', keywords=keywords, itemsall=itemsall)  


@analytics.route("/keyword/<string:keywordtextname>")
def keyword_items(keywordtextname):
    page = request.args.get('page', 1, type=int)
    keyword = Keyword.query.filter_by(keywordtextname=keywordtextname).first_or_404()    
    item_keywords = ItemKeyword.query.filter_by(reference=keyword).order_by(ItemKeyword.date_analysis.desc()).paginate(page=page, per_page=4)
    itemsall = Item.query.order_by(Item.date_posted.desc())
    return render_template('keyword_items.html', item_keywords=item_keywords, keyword=keyword, itemsall=itemsall)


    
