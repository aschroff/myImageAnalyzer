# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 09:30:50 2019

@author: Andi
"""

createtempversion = False
with open('requirements.txt') as orginalversion:
    if 'pypiwin32' in orginalversion.read():
        createtempversion = True
    if 'pywin32' in orginalversion.read():   
        createtempversion = True

if createtempversion:
    print("pypiwin32/pywin32")
else:
    print("Clean")

with open('requirements.txt') as orginalversion:
    if createtempversion:
       with open("requirementsAWS.txt", "w+") as tempversion:
           orginallines = orginalversion.readlines()
           for line in orginallines:
               if ("pypiwin32" in line) or ("pywin32" in line):
                   pass
               else:
                   tempversion.write(line)
               
   
        
