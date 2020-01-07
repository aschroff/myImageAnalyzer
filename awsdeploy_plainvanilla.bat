python scriptcheckrequirementstxtforAWS.py > Output
SET /p winentries=<Output
Del Output
if "%winentries%" == "pypiwin32/pywin32" goto WININREQ
git add *.config
git add *.py
git add *.html
git add requirements.txt
git commit -m %1
git push
eb deploy
goto ENDE
   :WININREQ
echo "pypiwin32/pywin32 in requirements.txt -> Remove"
   :ENDE   