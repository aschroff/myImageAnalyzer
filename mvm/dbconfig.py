# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 21:16:17 2019

@author: Andi
"""
import os

if 'RDS_HOSTNAME' in os.environ:
  DATABASE = {
    'NAME': os.environ['RDS_DB_NAME'],
    'USER': os.environ['RDS_USERNAME'],
    'PASSWORD': os.environ['RDS_PASSWORD'],
    'HOST': os.environ['RDS_HOSTNAME'],
    'PORT': os.environ['RDS_PORT'],
  }
  databaseURI = 'mysql://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(NAME)s' % DATABASE
else:
  databaseURI = 'mysql://root:Welcome1@localhost/mvm'

#databaseURI = 'mysql://dbadmin:Welcome1@aa185kmyt8wve44.cu76mq9u5srd.eu-central-1.rds.amazonaws.com/mvm'

