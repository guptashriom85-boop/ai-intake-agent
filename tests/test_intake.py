import os
os.environ["DATABASE_URL"]="sqlite:///./test_intake.db"
os.environ["ADMIN_EMAIL"]="admin@test.com"
os.environ["ADMIN_PASSWORD"]="secret"
os.environ["JWT_SECRET"]="test-secret-key-32-characters-long"
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    with TestClient(app) as c: assert c.get('/health').json()['status']=='ok'

def test_clinic_emergency():
    with TestClient(app) as c:
        r=c.post('/api/intake',json={"mode":"clinic","name":"Test User","contact":"a@b.com","message":"I have chest pain and can't breathe"})
        assert r.status_code==200; d=r.json(); assert d['risk']=='critical'; assert d['urgency']=='emergency'; assert d['handoff_requested']==1

def test_legal_intake():
    with TestClient(app) as c:
        r=c.post('/api/intake',json={"mode":"legal","name":"Test User","contact":"999","message":"I received a lawsuit"})
        assert r.status_code==200; assert r.json()['risk']=='high'

def test_appointment():
    with TestClient(app) as c:
        r=c.post('/api/appointments',json={"mode":"clinic","name":"Test","contact":"999","preferred_slot":"Tomorrow 10 AM","notes":"follow-up"})
        assert r.status_code==200; assert r.json()['status']=='requested'

def test_admin_stats_requires_auth():
    with TestClient(app) as c: assert c.get('/api/admin/stats').status_code==401

def test_admin_login_and_stats():
    with TestClient(app) as c:
        token=c.post('/auth/login',json={"email":"admin@test.com","password":"secret"}).json()['access_token']
        assert c.get('/api/admin/stats',headers={'Authorization':f'Bearer {token}'}).status_code==200
