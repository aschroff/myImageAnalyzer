from flask import Blueprint
from flask import render_template, request
from mvm import db
from mvm.models import Item, Keyword, ItemKeyword, Person
from mvm.analytics.forms import SearchItemForm

main = Blueprint('main', __name__)

def create_texts(item):
    foundkeywords = False
    foundtargets = False
    foundcelebrities = False
    foundtext = False
    foundlabel = False
    line1 = ""
    line4 = ""
    characterLine = 23
    keywords = Keyword.query.join(ItemKeyword).filter_by(itemin=item)
    for keyword in keywords:
        if len(line1) == 0:
            foundkeywords = True        
            line1=keyword.keywordtextname
        else:
            line1=line1 + ", " + keyword.keywordtextname  
        if keyword.label:
            if len(line4) == 0:
                foundlabel = True        
                line4=keyword.keywordtextname
            else:
                line4=line4 + ", " + keyword.keywordtextname              
    line2 = ""
    for person in Person.query.filter_by(itemin=item):
        if person.relatedcelebrity:
            text=person.relatedcelebrity.name
            foundcelebrities=True
        elif  person.foundtargetimage:   
            text=person.foundtargetimage.imagefortarget.name
            foundtargets=True
        else:
            continue
        if len(line2) == 0:
            line2=text
        else:
            line2=line2 + ", " + text 
    line3=""
    text =  item.text       
    if len(text)>0:
        line3 = str(item.text)
        foundtext = True
    
    if len(line1)>characterLine:
        line1=line1[0:characterLine-3] + "..."
    if len(line2)>characterLine:
        line2=line2[0:characterLine-3] + "..."
    if len(line3)>characterLine:
        line3=line3[0:characterLine-3] + "..."   
    if len(line4)>characterLine*3:
        line4=line4[0:characterLine*3-3] + "..." 
    entry = {}
    entry["line1"]=line1
    entry["line2"]=line2
    entry["line3"]=line3
    entry["line4"]=line4
    entry["foundkeywords"] = foundkeywords
    entry["foundtargets"] = foundtargets
    entry["foundcelebrities"] = foundcelebrities
    entry["foundtext"] = foundtext
    entry["foundlabel"] = foundlabel
    return line1, line2, line3,  line4, foundkeywords, foundtargets, foundcelebrities, foundtext, foundlabel, entry

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    items = Item.query.order_by(Item.date_posted.desc()).paginate(page=page, per_page=12)
    texts={}  
    for item in items.items:
        line1, line2, line3, line4, foundkeywords, foundtargets, foundcelebrities, foundtext, foundlabel, entry = create_texts(item)
        texts[item.id]=entry 
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()
    return render_template('home.html', items=items, itemsall=itemsall, searchform=searchform, texts=texts)


@main.route("/about")
def about():
    db.drop_all()
    db.create_all()
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()
    return render_template('about.html', title='About', itemsall=itemsall, searchform=searchform)
