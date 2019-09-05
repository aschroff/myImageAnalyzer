from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from flask_babel import gettext
from mvm.analytics.forms import CreateTargetForm, CreateTargetImageForm, SearchItemForm, FilterItemForm
from mvm.models import User, Item, ItemKeyword, Keyword, Person, Attribute, PersonAttribute, Celebrity, Target, Targetimage
from mvm.items.utils import save_item, save_thumbnail, get_image_from_file
from sqlalchemy import func 
from mvm import db
from sqlalchemy.sql import union


analytics = Blueprint('analytics', __name__)


@analytics.route("/keywords")
def keywords():
    page = request.args.get('page', 1, type=int)
    keywordstest = db.session.query(func.count(ItemKeyword.item_id).label('countitems'), Keyword.id, Keyword.keywordtextname).group_by(ItemKeyword.keyword_id).join(Keyword)
    k = keywordstest.paginate(page=page, per_page=10)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()
    return render_template('keywords.html', keywords=k, itemsall=itemsall, searchform=searchform)  


@analytics.route("/keyword/<string:keywordtextname>")
def keyword_items(keywordtextname):
    page = request.args.get('page', 1, type=int)
    keyword = Keyword.query.filter_by(keywordtextname=keywordtextname).first_or_404()    
    item_keywords = ItemKeyword.query.filter_by(reference=keyword).order_by(ItemKeyword.date_analysis.desc()).paginate(page=page, per_page=4)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    return render_template('keyword_items.html', item_keywords=item_keywords, keyword=keyword, itemsall=itemsall)

@analytics.route("/attributes")
def attributes():
    page = request.args.get('page', 1, type=int)
    attributestest = db.session.query(func.count(PersonAttribute.person_id).label('countpersons'), Attribute.id, Attribute.attributetextname).group_by(PersonAttribute.attribute_id).join(Attribute)
    a = attributestest.paginate(page=page, per_page=10)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('attributes.html', attributes=a, itemsall=itemsall, searchform=searchform) 
    
@analytics.route("/attribute/<string:attributetextname>")
def attribute_items(attributetextname):
    page = request.args.get('page', 1, type=int)
    attribute = Attribute.query.filter_by(attributetextname=attributetextname).first_or_404()    
    attributeitems = Item.query.join(Person).join(PersonAttribute).filter_by(attribute_id = attribute.id).distinct().paginate(page=page, per_page=4)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('attribute_items.html', attributeitems=attributeitems, attribute=attribute, itemsall=itemsall, searchform=searchform)

@analytics.route("/celebrities")
def celebrities():
    page = request.args.get('page', 1, type=int)
    celebritiesstest = db.session.query(func.count(Person.id).label('countpersons'), Celebrity.id, Celebrity.name, Celebrity.aws_id).group_by(Person.celebrity_id).join(Celebrity)
    a = celebritiesstest.paginate(page=page, per_page=10)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('celebrities.html', celebrities=a, itemsall=itemsall, searchform=searchform) 
    
@analytics.route("/celebrity/<string:aws_id>")
def celebrity_items(aws_id):
    page = request.args.get('page', 1, type=int)
    celebrity = Celebrity.query.filter_by(aws_id=aws_id).first_or_404()    
    celebrityitems = Item.query.join(Person).filter_by(celebrity_id = celebrity.id).distinct().paginate(page=page, per_page=4)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('celebrity_items.html', celebrityitems=celebrityitems, celebrity=celebrity, itemsall=itemsall, searchform=searchform)

@analytics.route("/target/new", methods=['GET', 'POST'])
@login_required
def new_target():
    form = CreateTargetForm()
    if form.validate_on_submit():  
        if form.name.data:         
           target = Target(name = form.name.data, searcher = current_user)
           db.session.add(target)
           db.session.commit()
           flash(gettext('Your new target has been created'), 'success') 
           return redirect(url_for('users.account'))  
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()  
    searchform = SearchItemForm()
    return render_template('create_target.html', title='New Target', form=form, legend=gettext('New Target'), itemsall=itemsall, searchform=searchform)

@analytics.route("/target/<int:target_id>/update", methods=['GET', 'POST'])
@login_required
def update_target(target_id):
    target = Target.query.get_or_404(target_id)
    if target.searcher != current_user:
        abort(403)
    form=CreateTargetForm()
    if form.validate_on_submit():         
        target.name = form.name.data                  
        db.session.commit()
        flash(gettext('Your target has been updated'), 'success')
        return redirect(url_for('users.account'))   
    elif request.method == 'GET':
        form.name.data = target.name 
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('create_target.html', title="Update Target",
                           form=form, legend=gettext('Update Target'), target=target, itemsall=itemsall, searchform=searchform) 
    
@analytics.route("/targetimage/<int:target_id>/new", methods=['GET', 'POST'])
@login_required
def new_targetimage(target_id):
    target = Target.query.get_or_404(target_id)
    form = CreateTargetImageForm()
    if form.validate_on_submit():  
        if form.file.data:     
           file = save_item(form.file.data) 
           thumbnail = save_thumbnail(form.file.data)
           targetimage = Targetimage(name = form.name.data, imagefortarget = target, file = file, thumbnail = thumbnail, age = form.age.data)
           db.session.add(targetimage)
           db.session.commit()
           flash(gettext('Your new image has been created'), 'success') 
           return redirect(url_for('analytics.update_target', target_id = target.id))  
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()  
    searchform = SearchItemForm()    
    return render_template('create_targetimage.html', title='New Image', form=form, legend=gettext('New image for target'), itemsall=itemsall, searchform=searchform)    


@analytics.route("/targetimage/<int:targetimage_id>/update", methods=['GET', 'POST'])
@login_required
def update_targetimage(targetimage_id):
    print(targetimage_id)
    targetimage = Targetimage.query.get_or_404(targetimage_id)
    form = CreateTargetImageForm()
    if form.validate_on_submit():  
        if form.file.data:     
           targetimage.file = save_item(form.file.data) 
           targetimage.thumbnail = save_thumbnail(form.file.data)
        targetimage.name = form.name.data
        targetimage.age = form.age.data
        db.session.commit()
        flash(gettext('Your new image has been updated'), 'success') 
        return redirect(url_for('analytics.update_targetimage', targetimage_id = targetimage.id))  
    elif request.method == 'GET':
        form.name.data = targetimage.name
        form.age.data = targetimage.age
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()  
    searchform = SearchItemForm()    
    return render_template('create_targetimage.html', title='Update Image', form=form, legend=gettext('Update image for target'), itemsall=itemsall, searchform=searchform)    

@analytics.route("/targetimage/<int:targetimage_id>")
def targetimage(targetimage_id):
    targetimage = Targetimage.query.get_or_404(targetimage_id)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('targetimage.html', title=targetimage.name, targetimage=targetimage, itemsall=itemsall, searchform=searchform)

@analytics.route("/targetimage/<int:targetimage_id>/delete", methods=['POST'])
@login_required
def deletetargetimage(targetimage_id):
    targetimage = Targetimage.query.get_or_404(targetimage_id)
    if targetimage.imagefortarget.searcher != current_user:
        abort(403)
    target_id = targetimage.imagefortarget.id   
    db.session.delete(targetimage)
    
    db.session.commit()
    flash(gettext('Your Image has been deleted'), 'success')
    return redirect(url_for('analytics.update_target', target_id = target_id))  

@analytics.route("/target/<int:target_id>")
def target(target_id):
    target = Target.query.get_or_404(target_id)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('target.html', title=target.name, target=target, itemsall=itemsall, searchform=searchform)

@analytics.route("/target/<int:target_id>/delete", methods=['POST'])
@login_required
def deletetarget(target_id):
    target = Target.query.get_or_404(target_id)    
    if target.searcher != current_user:
        abort(403)  
    db.session.delete(target)
    
    db.session.commit()
    flash(gettext('Your target has been deleted'), 'success')
    return redirect(url_for('users.account', user_id = current_user.id))  

@analytics.route("/search/", methods=['POST'])
def search():
    print(request.args)
    form = SearchItemForm()    
    if len(form.searchtext.data) > 0:
        search_query=form.searchtext.data
    else:
        search_query = str('*')
    return redirect(url_for('analytics.results', search_query=search_query, search_keywords=True, search_attributes = False,
                            search_celebs = False, search_text = False, search_age = '', search_targets = '',searchtexthidden=form.searchtext.data))

@analytics.route("/filter/<search_query>", methods=['POST'])
def filter(search_query):    
    formfilter = FilterItemForm()
    choices = Target.query.filter_by(searcher = current_user)
    formfilter.search_targets.query = choices   
    if formfilter.search_targets.data:
        search_targets = formfilter.search_targets.data.id
    else:                  
        search_targets = ''
    return redirect(url_for('analytics.results', search_query=search_query, search_keywords=formfilter.search_keywords.data, search_attributes = formfilter.search_attributes.data,
                            search_celebs = formfilter.search_celebs.data, search_text = formfilter.search_text.data, search_age = formfilter.search_age.data,
                            search_targets=search_targets, searchtexthidden = formfilter.searchtexthidden.data))
    

@analytics.route("/results/<search_query>")
def results(search_query):
    page = request.args.get('page', 1, type=int)
    if search_query != str('*'):
         itemscollect = Item.query.filter(Item.itemname.contains(search_query)).distinct()         
    else:
        itemscollect = Item.query.order_by(Item.date_posted.desc())
         
    if request.args.get('search_keywords') == 'True':
        itemscollect1 = Item.query.join(ItemKeyword).join(Keyword).filter(Keyword.keywordtextname.contains(search_query)).distinct()
        itemscollect2 = itemscollect1.union(itemscollect)
        itemscollect = itemscollect2

    if request.args.get('search_celebs') == 'True':
        itemscollect1 = Item.query.join(Person).join(Celebrity).filter(Celebrity.name.contains(search_query)).distinct()
        itemscollect2 = itemscollect1.union(itemscollect)
        itemscollect = itemscollect2

    if request.args.get('search_text') == 'True':
        itemscollect1 = Item.query.filter(Item.text.contains(search_query)).distinct()
        itemscollect2 = itemscollect1.union(itemscollect)
        itemscollect = itemscollect2
    if request.args.get('search_targets'):
        itemscollect = itemscollect.join(Person).join(Targetimage).join(Target).filter_by(id=request.args.get('search_targets'))

    items = itemscollect.distinct().paginate(page=page, per_page=4)    
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()  
    formsearch = SearchItemForm()
    formfilter = FilterItemForm()
    formsearch.searchtext.data = request.args.get('searchtexthidden')
    if request.args.get('search_keywords') == 'True':
        formfilter.search_keywords.data = request.args.get('search_keywords')
    if request.args.get('search_attributes') == 'True':
        formfilter.search_attributes.data = request.args.get('search_attributes')
    if request.args.get('search_celebs') == 'True':
        formfilter.search_celebs.data = request.args.get('search_celebs')
    if request.args.get('search_text') == 'True':        
        formfilter.search_text.data = request.args.get('search_text')
    formfilter.search_age.data = request.args.get('search_age')
    formfilter.searchtexthidden.data = request.args.get('searchtexthidden')
    
    if current_user.is_authenticated:
        choices = Target.query.filter_by(searcher = current_user)
        formfilter.search_targets.query = choices 
        if request.args.get('search_targets'):
            select = Target.query.get(request.args.get('search_targets'))
            formfilter.search_targets.process_data(select)
            #        formfilter.searchtexthidden.data = request.args.get('searchtexthidden')
        print('Ja')
    print(formfilter.search_targets)    
    return render_template('searchresults.html', title='Search', legend=gettext('Item search'), searchform = formsearch, filterform = formfilter, itemresults = items, itemsall=itemsall, search_query = search_query)

#    
#    choices = Target.query.filter_by(searcher = current_user)
#    form.search_targets.query = choices
#    page = request.args.get('page', 1, type=int)
#    print(request.args)
#    print(request.form)
#    if form.validate_on_submit():  
#        print('fall1')
#        searchtext = form.searchtext.data
#    else:
#        print('fall2')
#        searchtext = str('')    
##        if form.searchtext.data:   
#    print('3') 
#    print(page) 
#    items = Item.query.join(ItemKeyword).join(Keyword).filter(Keyword.keywordtextname.contains(searchtext)).distinct().paginate(page=page, per_page=4) 
#    itemsall = Item.query.order_by(Item.date_posted.desc()).all()  
#     return render_template('search.html', form=form, title='Search', legend=gettext('Item search'), itemresults = items, itemsall=itemsall)      
