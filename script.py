# -*- coding: utf-8 -*-
"""
Created on Sat Aug 24 19:10:43 2019

@author: Andi
"""

from mvm import create_app

application = create_app()

from mvm import db

with application.app_context():
    db.drop_all()
    db.create_all()