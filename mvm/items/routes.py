from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from flask_babel import gettext
from mvm import db, rekognition
from mvm.items.forms import CreateItemForm
from mvm.models import User, Item, ItemKeyword, Keyword
from mvm.items.utils import save_item, save_thumbnail, get_image_from_file


items = Blueprint('items', __name__)



@items.route("/item/new", methods=['GET', 'POST'])
@login_required
def new_item():
    form = CreateItemForm()
    if form.validate_on_submit():  
        if form.item_file.data:
           itemfile = save_item(form.item_file.data) 
           thumbnailfile = save_thumbnail(form.item_file.data)            
           item = Item(item_file = itemfile, itemname = form.itemname.data, thumbnail = thumbnailfile,
                       owner = current_user,  analysis_keywords=form.analysis_keywords.data, analysis_keywords_theshold = form.analysis_keywords_theshold.data)
           db.session.add(item)
           db.session.commit()
           if form.analysis_keywords.data:
               imgbytes = get_image_from_file(itemfile)
               rekres = rekognition.detect_labels(Image={'Bytes': imgbytes}, MinConfidence=item.analysis_keywords_theshold)
               for label in rekres['Labels']:
                       itemkeywordstring = str(label['Name'])
                       keyword = Keyword.query.filter_by(keywordtextname = itemkeywordstring).first()
                       if keyword is None:
                           keyword = Keyword(keywordtextname = itemkeywordstring)
                           db.session.add(keyword)
                       print(itemkeywordstring)
                       itemkeyword = ItemKeyword(reference = keyword, itemin = item)
                       db.session.add(itemkeyword)
               db.session.commit()
           flash(gettext('Your new item has been created'), 'success') 
           return redirect(url_for('main.home'))  
    itemsall = Item.query.order_by(Item.date_posted.desc())   
    form.analysis_keywords.data = True
    form.analysis_keywords_theshold.data = 90
    return render_template('create_item.html', title='New Item', form=form, legend=gettext('New Item'), itemsall=itemsall)

@items.route("/item/<int:item_id>")
def item(item_id):
    item = Item.query.get_or_404(item_id)
    itemkeywords = ItemKeyword.query.filter_by(itemin=item) 
    itemsall = Item.query.order_by(Item.date_posted.desc())
    return render_template('item.html', title=item.itemname, item=item, itemkeywords=itemkeywords, itemsall=itemsall)   

@items.route("/item/<int:item_id>/update", methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)
    form=CreateItemForm()
    if form.validate_on_submit():
        if form.item_file.data:
           item.item_file = save_item(form.item_file.data) 
           item.thumbnail = save_thumbnail(form.item_file.data)         
        item.itemname = form.itemname.data           
        item.analysis_keywords = form.analysis_keywords.data
        item.analysis_persons = form.analysis_persons.data
        item.analysis_celebs = form.analysis_celebs.data 
        item.analysis_text = form.analysis_text.data
        item.analysis_labels = form.analysis_labels.data
        item.analysis_keywords_theshold = form.analysis_keywords_theshold.data
        db.session.query(ItemKeyword).filter(ItemKeyword.item_id == item_id).delete()
        db.session.commit()
        if form.analysis_keywords.data:
               imgbytes = get_image_from_file(item.item_file)
               rekres = rekognition.detect_labels(Image={'Bytes': imgbytes}, MinConfidence=item.analysis_keywords_theshold)
               for label in rekres['Labels']:
                       itemkeywordstring = str(label['Name'])
                       keyword = Keyword.query.filter_by(keywordtextname = itemkeywordstring).first()
                       if keyword is None:
                           keyword = Keyword(keywordtextname = itemkeywordstring)
                           db.session.add(keyword)
                       itemkeyword = ItemKeyword(reference = keyword, itemin = item)
                       db.session.add(itemkeyword)
               db.session.commit()               
        flash(gettext('Your item has been updated'), 'success')
        return redirect(url_for('items.item', item_id=item.id))   
    elif request.method == 'GET':
        form.itemname.data = item.itemname
        form.item_file.data = item.item_file
        form.analysis_keywords.data = item.analysis_keywords
        form.analysis_persons.data = item.analysis_persons        
        form.analysis_celebs.data = item.analysis_celebs
        form.analysis_text.data = item.analysis_text
        form.analysis_labels.data = item.analysis_labels
        form.analysis_keywords_theshold.data = item.analysis_keywords_theshold
    itemsall = Item.query.order_by(Item.date_posted.desc())
    itemkeywords = ItemKeyword.query.filter_by(itemin=item)
    return render_template('create_item.html', title="Update Item",
                           form=form, legend=gettext('Update Item'), item=item, itemsall=itemsall, itemkeywords=itemkeywords)  
    
@items.route("/item/<int:item_id>/delete", methods=['POST'])
@login_required
def delete(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)
    print(ItemKeyword.query.filter_by(itemin=item).all())
    db.session.delete(item)
    
    db.session.commit()
    flash(gettext('Your item has been deleted'), 'success')
    return redirect(url_for('main.home'))


@items.route("/user/<string:username>")
def user_items(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    items = Item.query.filter_by(owner=user).order_by(Item.date_posted.desc()).paginate(page=page, per_page=4)
    itemsall = Item.query.order_by(Item.date_posted.desc())
    return render_template('user_items.html', items=items, user=user, itemsall=itemsall)


    
