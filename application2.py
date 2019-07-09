# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 20:46:04 2019

@author: Andi
"""

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World"