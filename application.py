# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 20:46:04 2019

@author: Andi
"""

from mvm import create_app

application = create_app()


if __name__ == '__main__':
    application.run(debug=True)