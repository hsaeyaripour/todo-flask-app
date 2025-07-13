# app/tests/test_app.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_homepage_redirects_to_login():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
