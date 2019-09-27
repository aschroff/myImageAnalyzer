# tests/test_blog.py

import unittest

from base import BaseTestCase
from flask_login import current_user
from mvm.models import Target

class ItemsTests(BaseTestCase):

    # Ensure a logged in user can add a new post
    def test_user_can_create_item(self):
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin"),
                follow_redirects=True
            )
            your_file = open("./tests/Test data/Ed.jpg", "rb") 
            response = self.client.post(
                '/item/new',
                data=dict(item_file=your_file, itemname="description in itemname", 
                          analysis_keywords = True,
                          analysis_persons = True,
                          analysis_celebs = True,
                          analysis_targets = True,
                          analysis_text = True,
                          analysis_labels = True,
                          analysis_threshold = 90, ),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Your new item has been created', response.data)
            self.assertIn(b'admin', response.data)
            self.assertIn(b'Ed Sheeran', response.data)
            self.assertIn(b'description in itemname', response.data)
            self.assertIn(b'Testtext noch la', response.data)
            self.assertIn(b'Face', response.data)
            self.assertIn(b'Male', response.data)
            
      # Ensure user can register
    def test_user_item_full(self):
        with self.client:
            response = self.client.post('/register', data=dict(
                username='maxmustermann2', email='max2@mustermann.com',
                password='mm@mvm', confirm_password='mm@mvm'
            ), follow_redirects=True)            
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="max2@mustermann.com", password="mm@mvm"),
                follow_redirects=True
            )
            self.assertTrue(current_user.username == "maxmustermann2")
            self.assertTrue(current_user.is_active)

            user_id = current_user.id    
        with self.client: 
            response = self.client.post(
                    '/target/new?user_id='+str(user_id),
                    data=dict(name="Annatarget"),
                    follow_redirects=True
            )
            
            

            
        with self.client:   
            targetid = Target.query.filter_by(name="Annatarget").first().id  
            your_file = open("./tests/Test data/Anna10.jpg", "rb")
            response = self.client.post(
                '/targetimage/'+str(targetid)+'/new',
                data=dict(name="Annatargetimage10", age=10, file=your_file),
                follow_redirects=True
            )            
        
        with self.client:
            your_file = open("./tests/Test data/Ed.jpg", "rb")
            response = self.client.post(
                    '/item/new',
                    data=dict(item_file=your_file, itemname="item full cycle", 
                              analysis_keywords = True,
                              analysis_persons = True,
                              analysis_celebs = True,
                              analysis_targets = True,
                              analysis_text = True,
                              analysis_labels = True,
                              analysis_threshold = 90,
                    ),
                    follow_redirects=True
            )
            self.assertIn(b'maxmustermann2', response.data)
            self.assertIn(b'Your new item has been created', response.data)
            self.assertIn(b'Ed Sheeran', response.data)
            self.assertIn(b'Annatarget', response.data)
            self.assertIn(b'item full cycle', response.data)
            self.assertIn(b'Testtext noch la', response.data)
            self.assertIn(b'Annatargetimage10', response.data)
            self.assertIn(b'Face', response.data)
            self.assertIn(b'Male', response.data)
        
if __name__ == '__main__':
    unittest.main()
