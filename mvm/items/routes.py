from datetime import datetime
import random 
from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from flask_babel import gettext
from mvm import db, rekognition
from mvm.items.forms import CreateItemForm
from mvm.models import User, Item, ItemKeyword, Keyword, Attribute, Person, PersonAttribute, Celebrity
from mvm.items.utils import save_item, save_thumbnail, get_image_from_file
from mvm.analytics.forms import SearchItemForm

steps = 10
items = Blueprint('items', __name__)

def unsafe_content_detection(item):
       if item.analysis_labels:
           imgbytes = get_image_from_file(item.item_file)
           rekres = rekognition.detect_moderation_labels(Image={'Bytes': imgbytes}, MinConfidence=item.analysis_threshold)
           print(rekres)
           for label in rekres['ModerationLabels']:
                   print(len(label['ParentName']))
                   print(label['ParentName'])
                   if len(label['ParentName']) > 0:
                       labeltext = label['ParentName'] + " - " + label['Name']     
                       keyword = Keyword.query.filter_by(keywordtextname = labeltext).first()
                       if keyword is None:
                           keyword = Keyword(keywordtextname = labeltext, label=True)
                           db.session.add(keyword)
                       itemkeyword = ItemKeyword(reference = keyword, itemin = item)
                       db.session.add(itemkeyword)
           db.session.commit()

def object_and_scene_detection(item):
       if item.analysis_keywords:
           imgbytes = get_image_from_file(item.item_file)
           rekres = rekognition.detect_labels(Image={'Bytes': imgbytes}, MinConfidence=item.analysis_threshold)
           for label in rekres['Labels']:
                   itemkeywordstring = str(label['Name'])
                   keyword = Keyword.query.filter_by(keywordtextname = itemkeywordstring).first()
                   if keyword is None:
                       keyword = Keyword(keywordtextname = itemkeywordstring)
                       db.session.add(keyword)
                   itemkeyword = ItemKeyword(reference = keyword, itemin = item)
                   db.session.add(itemkeyword)
           db.session.commit()
           

def facial_analysis(item):    
           if item.analysis_persons:
               imgbytes = get_image_from_file(item.item_file)
               rekres = rekognition.detect_faces(Image={'Bytes': imgbytes},  Attributes=['ALL'])
               for personresult in rekres['FaceDetails']:
                       rangeage = personresult['AgeRange']
                       low = rangeage['Low']
                       high = rangeage['High']
                       boundingbox = personresult['BoundingBox']
                       width = boundingbox['Width']
                       height = boundingbox['Height']
                       left = boundingbox['Left']
                       top = boundingbox['Top']
                       person = Person(itemin = item, BoundingBoxWidth = width, BoundingBoxHeight = height, 
                                       BoundingBoxLeft = left, BoundingBoxTop = top, AgeLow = low, AgeHigh = high)
                       db.session.add(person)
                       for attributename in personresult.keys():
                           if attributename == 'Emotions':
                               for emotion in personresult[attributename]:
                                   if emotion['Confidence'] >= item.analysis_threshold:
                                        emotionname = emotion['Type']                                      
                                        attribute = Attribute.query.filter_by(attributetextname = emotionname).first()
                                        if attribute is None:
                                            attribute = Attribute(attributetextname = emotionname)
                                            db.session.add(attribute)
                                        personattribute =  PersonAttribute(referenceperson = person, referenceattribute = attribute)  
                                        db.session.add(personattribute)                                       
                           elif attributename == 'Landmarks':                                   
                               print()
                           elif attributename == 'Pose':    
                               print()                               
                           elif attributename == 'Quality':     
                               print()                               
                           elif attributename == 'Confidence':
                               print()  
                           elif attributename == 'Gender':
                               attributenamegender = personresult[attributename]['Value']
                               attribute = Attribute.query.filter_by(attributetextname = attributenamegender).first()      
                               if attribute is None:
                                   attribute = Attribute(attributetextname = attributenamegender)
                                   db.session.add(attribute)                                           
                               personattribute =  PersonAttribute(referenceperson = person, referenceattribute = attribute)  
                               db.session.add(personattribute)                                                            
                           elif 'Value' in personresult[attributename]:
                                   if personresult[attributename]['Value']: 
                                       attribute = Attribute.query.filter_by(attributetextname = attributename).first()
                                       if attribute is None:
                                           attribute = Attribute(attributetextname = attributename)
                                           db.session.add(attribute)                                           
                                       personattribute =  PersonAttribute(referenceperson = person, referenceattribute = attribute)  
                                       db.session.add(personattribute)
                       db.session.commit()  

def detectposition(positionx, positiony, comparewidth, compareheight, compareleft, comparetop):
    x1 = positionx
    y1 = positiony
    x2 = positionx + 1/steps
    y2 = positiony + 1/steps
    x1c = compareleft
    y1c = comparetop
    x2c = compareleft + comparewidth
    y2c = comparetop + compareheight
    return (((x1 <= x1c) and (x2 >= x1c)) or ((x1 <= x2c) and (x2 >= x1c))) and \
           (((y1 <= y1c) and (y2 >= y1c)) or ((y1 <= y2c) and (y2 >= y1c)))

def determineoverlap(compare, personidentified):
    overlap = 0
    for x in range(0,steps, 1):
        for y in range(0, steps, 1):
            if detectposition(x/steps ,y/steps ,compare['Width'], compare['Height'], compare['Left'], compare['Top']) \
                and detectposition(x/steps,y/steps,personidentified.BoundingBoxWidth, personidentified.BoundingBoxHeight, personidentified.BoundingBoxLeft, personidentified.BoundingBoxTop):
                overlap = overlap + 1
    return overlap           

def celebrity_recognition(item):    
           if item.analysis_persons and item.analysis_celebs:
               imgbytes = get_image_from_file(item.item_file)
               rekres = rekognition.recognize_celebrities(Image={'Bytes': imgbytes})
               print('celebrity_recognition')
               for celebrityresult in rekres['CelebrityFaces']:
                       print('celebrityresult:' + str(celebrityresult))
                       if celebrityresult['MatchConfidence'] >= item.analysis_threshold: 
                           boundingbox = celebrityresult['Face']['BoundingBox']
                           maxoverlap = 0
                           for person in item.persons:
                               print('person:' + str(person.id))
                               overlap = determineoverlap(compare = boundingbox, personidentified = person)
                               print('overlap person:' + str(overlap))
                               if overlap > maxoverlap:
                                   maxoverlap = overlap
                                   personfit = person
                                   print('New max:' + str(maxoverlap))
                           if maxoverlap > 0:
                                print('found' + str(celebrityresult) + str(personfit.id))
                                celebrity = Celebrity.query.filter_by(aws_id = celebrityresult['Id']).first()
                                if celebrity is None:
                                    if len(celebrityresult['Urls']) > 0:
                                        celebrity = Celebrity(aws_id = celebrityresult['Id'], name = celebrityresult['Name'], url = celebrityresult['Urls'][0])
                                    else:
                                        celebrity = Celebrity(aws_id = celebrityresult['Id'], name = celebrityresult['Name'], url = "http://www.google.de")
                                    db.session.add(celebrity)
                                    db.session.commit()
                                personfit.celebrity_id =  celebrity.id 
                                db.session.commit()   
                           else:
                                print('not found' + str(celebrityresult))                   

def face_comparison(item):    
           if item.analysis_persons and item.analysis_targets :
               imgbytes = get_image_from_file(item.item_file) 
               print(item.itemname)
               for target in current_user.targets:
                   print(target.name)
                   max_sim = 0
                   for targetimage in target.targetimages:
                       print (targetimage.name)
                       imgbytescompare = get_image_from_file(targetimage.file)
                       rekres = rekognition.compare_faces(SimilarityThreshold=item.analysis_threshold, SourceImage={'Bytes': imgbytescompare}, TargetImage={'Bytes': imgbytes})
                       print(rekres) 
                       if len(rekres['FaceMatches']) > 0:
                           sim = rekres['FaceMatches'][0]['Similarity']
                           print(sim)
                           if sim >= item.analysis_threshold: 
                               if sim > max_sim: 
                                   boundingbox = rekres['FaceMatches'][0]['Face']['BoundingBox']
                                   maxoverlap = 0
                                   for person in item.persons:
                                       overlap = determineoverlap(compare = boundingbox, personidentified = person)
                                       print('overlap person:' + str(overlap))
                                       if overlap > maxoverlap:
                                           maxoverlap = overlap
                                           max_sim = sim
                                           personfit = person
                                           print('New max:' + str(maxoverlap))
                                   if maxoverlap > 0:
                                        personfit.foundtargetimage = targetimage
                                        db.session.commit()   
                                   else:
                                        print('not found') 
                       else:
                           print('not found 1')

def text_detection(item):    
           if item.analysis_text:
               imgbytes = get_image_from_file(item.item_file) 
               rekres = rekognition.detect_text(Image={'Bytes': imgbytes})
               print(rekres)
               item.text = ''
               for worddetected in rekres['TextDetections']:
                   if worddetected['Confidence'] >= item.analysis_threshold: 
                       textpiece = worddetected['DetectedText']
                       print(textpiece)
                       newtext = str(item.text) + str(' ') + str(textpiece)
                       if len(newtext) <= 1000:
                           item.text = newtext
           print(item.text)        
           db.session.commit() 
                   

@items.route("/item/new", methods=['GET', 'POST'])
@login_required
def new_item():
    form = CreateItemForm()
    if form.validate_on_submit():  
        if form.item_file.data:
           itemfile = save_item(form.item_file.data) 
           thumbnailfile = save_thumbnail(form.item_file.data)            
           item = Item(item_file = itemfile, itemname = form.itemname.data, thumbnail = thumbnailfile,
                       owner = current_user,  analysis_keywords=form.analysis_keywords.data, 
                       analysis_persons = form.analysis_persons.data, analysis_celebs = form.analysis_celebs.data,
                       analysis_targets = form.analysis_targets.data, analysis_text = form.analysis_text.data, analysis_labels = form.analysis_labels.data,
                       analysis_threshold = form.analysis_threshold.data)
           db.session.add(item)
           db.session.commit()
           # Object and scene detection - Keywords
           object_and_scene_detection(item = item)             
           # Facial analysis - Persons
           facial_analysis(item = item) 
           # Celebrity recognition        
           celebrity_recognition(item = item)  
           # Face comparision
           face_comparison(item=item)
           # Test in item
           text_detection(item=item)
           # Image moderation
           unsafe_content_detection(item = item)  
           flash(gettext('Your new item has been created'), 'success') 
           return redirect(url_for('main.home'))  
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()  
    form.analysis_keywords.data = True
    form.analysis_threshold.data = 90
    searchform = SearchItemForm()
    return render_template('create_item.html', title='New Item', form=form, legend=gettext('New Item'), itemsall=itemsall, searchform=searchform)

@items.route("/item/<int:item_id>")
def item(item_id):
    item = Item.query.get_or_404(item_id)
    itemkeywords = ItemKeyword.query.filter_by(itemin=item)
    persons = Person.query.filter_by(itemin=item)
    attributes = {}
    for person in persons:
        personattributes = PersonAttribute.query.filter_by(referenceperson=person).all()
        attributes[person.id] = personattributes   
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('item.html', title=item.itemname, item=item, itemkeywords=itemkeywords, itemsall=itemsall,
                           persons = persons, personattributes = attributes, searchform=searchform)   

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
        item.analysis_targets = form.analysis_targets.data
        item.analysis_text = form.analysis_text.data
        item.analysis_labels = form.analysis_labels.data
        item.analysis_threshold = form.analysis_threshold.data
        db.session.query(ItemKeyword).filter(ItemKeyword.item_id == item_id).delete()
        db.session.query(Person).filter(Person.item_id == item_id).delete()
        db.session.commit()
        # Object and scene detection - Keywords
        object_and_scene_detection(item = item)             
        # Facial analysis - Persons
        facial_analysis(item = item) 
        # Celebrity recognition        
        celebrity_recognition(item = item)  
        # Face comparision
        face_comparison(item=item)
        # Test in item
        text_detection(item=item)
        # Image moderation
        unsafe_content_detection(item = item) 
        flash(gettext('Your item has been updated'), 'success')
        return redirect(url_for('items.item', item_id=item.id))   
    elif request.method == 'GET':
        form.itemname.data = item.itemname
        form.item_file.data = item.item_file
        form.analysis_keywords.data = item.analysis_keywords
        form.analysis_persons.data = item.analysis_persons        
        form.analysis_celebs.data = item.analysis_celebs
        form.analysis_targets.data = item.analysis_targets               
        form.analysis_text.data = item.analysis_text
        form.analysis_labels.data = item.analysis_labels
        form.analysis_threshold.data = item.analysis_threshold
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    itemkeywords = ItemKeyword.query.filter_by(itemin=item).all()
    searchform = SearchItemForm()
    return render_template('create_item.html', title="Update Item",
                           form=form, legend=gettext('Update Item'), item=item, itemsall=itemsall, itemkeywords=itemkeywords, searchform=searchform)  
    
@items.route("/item/<int:item_id>/delete", methods=['POST'])
@login_required
def delete(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)
    db.session.delete(item)
    
    db.session.commit()
    flash(gettext('Your item has been deleted'), 'success')
    return redirect(url_for('main.home'))


@items.route("/user/<string:username>")
def user_items(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    items = Item.query.filter_by(owner=user).order_by(Item.date_posted.desc()).paginate(page=page, per_page=4)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('user_items.html', items=items, user=user, itemsall=itemsall, searchform=searchform)


    
