import unittest
from datetime import datetime

from app import app, db, model
from flask import session
from flask_login import login_user
from werkzeug.security import generate_password_hash

with app.app_context():
    class URLTestCase(unittest.TestCase):
        def setUp(self):
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
            self.client = app.test_client()
            app.app_context().push()

            manager = model.Manager.query.first()
            if not manager:
                manager = model.Manager()
                manager.username = 'Admin'
                manager.password = generate_password_hash('AdminTest66')
                manager.Email = 'admin@example.com'
                manager.log = 0
                db.session.add(manager)

            coach = model.Coach.query.filter_by(username='Coach').first()
            if not coach:
                coach = model.Coach()
                coach.username = 'Coach'
                coach.password = generate_password_hash('CoachTest66')
                coach.cprofile = '../static/coachProfile/default_none.jpg'
                coach.Email = 'coach@example.com'
                coach.speciality = 'all'
                coach.sex = 0
                db.session.add(coach)

            customer = model.Customer.query.filter_by(username='DemoUser').first()
            if not customer:
                customer = model.Customer()
                customer.username = 'DemoUser'
                customer.password = generate_password_hash('DemoUser66')
                customer.profile = '../static/customerProfile/default_none.jpg'
                customer.Email = 'customer@example.com'
                customer.status = 1
                customer.log = 0
                customer.sex = 0
                customer.posts = 0
                db.session.add(customer)
                db.session.flush()

                health = model.Health()
                health.uid = customer.id
                health.birthday = datetime.strptime('2020-01-01', '%Y-%m-%d')
                health.height = 170
                health.weight = 60
                health.aim_weight = 58
                health.prefer = 'fitness'
                db.session.add(health)

            db.session.commit()

        def tearDown(self):
            pass

        def test_app_start_route(self):
            with app.test_request_context():
                response = self.client.get('/', follow_redirects=True)
                self.assertEqual(200, response.status_code)

        def test_app_no_login_route(self):
            response = self.client.get('/newlogin')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/Managerlogin')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/Managers')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/CustomerLogin')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/manager')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/register')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/newAccount')
            self.assertEqual(response.status_code, 200)

        def test_app_unauthenticated_visit_route(self):
            with app.test_request_context():
                session['role'] = ''
                response = self.client.get('/newlogin')  # users will be redirected back to login page
                self.assertEqual(response.status_code, 200)

        def test_app_authenticated_visit_route(self):
            with app.test_request_context():  # since we are testing HTTP requests, a test request context is needed
                session['role'] = 'Manager'
                manager = model.Manager.query.first()
                login_user(manager, remember=True)
                response = self.client.get('/Showdata', follow_redirects=True)  # managers can view management data
                self.assertEqual(response.status_code, 200)
                session['role'] = 'customer'
                customer = model.Customer.query.filter_by(username="DemoUser").first()
                login_user(customer, remember=True)
                response = self.client.get('/ShowMyCourse',
                                           follow_redirects=True)  # members cna view their chosen courses
                self.assertEqual(response.status_code, 200)
                session['role'] = 'Coach'
                coach = model.Coach.query.filter_by(username="Coach").first()
                login_user(coach, remember=True)
                response = self.client.get('/ShowCoachcourse',
                                           follow_redirects=True)  # coaches can view their released courses
                self.assertEqual(response.status_code, 200)

        def test_app_profile_route(self):
            with app.test_request_context():  # since we are testing HTTP requests, a test request context is needed
                session['role'] = 'Manager'
                manager = model.Manager.query.first()
                login_user(manager, remember=False)
                response = self.client.get('/Manageraccount')  # login to view or update profile
                self.assertEqual(response.status_code, 302)
                session['role'] = 'customer'
                customer = model.Customer.query.filter_by(username="DemoUser").first()
                login_user(customer, remember=True)
                response = self.client.get('/Showaccount')  # login to view or update profile
                self.assertEqual(response.status_code, 302)
                session['role'] = 'Coach'
                coach = model.Coach.query.filter_by(username="Coach").first()
                login_user(coach, remember=True)
                response = self.client.get('/ShowCoachaccount')  # login to view or update profile
                self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    unittest.main()
