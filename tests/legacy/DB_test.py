from datetime import datetime
import unittest

from app import app, db
from app.model import Coach, Customer, Course, Connect, Manager, Post, Health
from werkzeug.security import generate_password_hash

with app.app_context():
    class DBTestCase(unittest.TestCase):
        def setUp(self):
            self.client = app.test_client()
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
            app.app_context().push()
            db.create_all()

        def test_addUser(self):
            # check the table and delete the existing data
            hel = Health.query.first()
            if hel:
                db.session.delete(hel)
                db.session.commit()
            po = Post.query.first()
            if po:
                db.session.delete(po)
                db.session.commit()
            con = Connect.query.first()
            if con:
                db.session.delete(con)
                db.session.commit()
            cor = Course.query.first()
            if cor:
                db.session.delete(cor)
                db.session.commit()
            cus = Customer.query.first()
            if cus:
                db.session.delete(cus)
                db.session.commit()
            coa = Coach.query.first()
            if coa:
                db.session.delete(coa)
                db.session.commit()
            man = Manager.query.first()
            if man:
                db.session.delete(man)
                db.session.commit()
            memember = Customer()
            memember.username = 'DBtest'
            memember.password = generate_password_hash("testCus66")  # encrypted password is stored
            memember.profile = '../static/customerProfile/default_none.jpg'
            memember.Email = 'member@example.com'
            memember.sex = 0
            memember.status = 0
            memember.posts = 0
            memember.log = 0
            coach = Coach()
            coach.username = 'DBtest'
            coach.password = generate_password_hash("testCoa66")  # encrypted password is stored
            coach.cprofile = '../static/coachProfile/test.jpg'
            coach.Email = 'coach@example.com'
            coach.speciality = 'all'
            coach.sex = 1
            manager = Manager()
            manager.username = 'DBtest'
            manager.password = generate_password_hash("testMan66")  # encrypted password
            manager.Email = 'manager@example.com'
            manager.log = 0
            db.session.add_all([memember, manager])
            db.session.add(coach)
            db.session.commit()
            newMember = Customer.query.filter_by(username='DBtest').first()
            newCoach = Coach.query.filter_by(username='DBtest').first()
            newManager = Manager.query.filter_by(username='DBtest').first()
            # test the foreign key relations:
            health = Health()
            health.uid = newMember.id
            health.birthday = datetime.strptime('2022-12-09', '%Y-%m-%d')
            health.weight = 0
            health.height = 0
            health.aim_weight = 0
            health.prefer = 'fitting'
            post = Post()
            post.uid = newMember.id
            post.photo = '../static/post/test20221216_193109.jpg'
            post.description = 'test test test'
            post.tag = 'first'
            course = Course()
            course.cid = newCoach.id
            course.name = 'test'
            course.description = 'test test test!'
            course.courseProfile = '../static/Course/cover/Coach20221217_204532.jpg'
            course.start = datetime.strptime('2022-12-17 20:44:12', '%Y-%m-%d %H:%M:%S')
            course.end = datetime.strptime('2022-12-17 22:00:12', '%Y-%m-%d %H:%M:%S')
            course.video = '../static/Course/video/_Compressed_Coach20221217_204532.mp4'
            db.session.add(health)
            db.session.commit()
            db.session.add(post)
            db.session.commit()
            db.session.add(course)
            db.session.commit()
            newCourse = Course.query.filter_by(cid=newCoach.cid).first()
            newHealth = Health.query.filter_by(uid=newMember.id).first()
            newPost = Post.query.filter_by(uid=newMember.id).first()
            # test the many-to-many relationship
            connect = Connect(newMember.id, newCoach.cid, newCourse.id)
            db.session.add_all([connect])
            db.session.commit()
            newConnect = Connect.query.filter_by(id=newMember.id).first()
            # assertions
            self.assertIsNotNone(newMember)
            self.assertIsNotNone(newCoach)
            self.assertIsNotNone(newManager)
            self.assertIsNotNone(newHealth)
            self.assertIsNotNone(newPost)
            self.assertIsNotNone(newConnect)

        def test_deleteManager(self):
            manager = Manager.query.first()
            db.session.delete(manager)
            db.session.commit()

        def test_deleteMember_and_coach(self):
            # connect can be deleted without key constrains
            connect = Connect.query.first()
            db.session.delete(connect)
            db.session.commit()
            # Then, delete the health of the same member
            health = Health.query.first()
            record = health.uid
            db.session.delete(health)
            db.session.commit()
            # Then, delete the post of the same member
            post = Post.query.filter_by(uid=record).first()
            db.session.delete(post)
            db.session.commit()
            # finally, delete the user
            member = Customer.query.filter_by(id=record).first()
            db.session.delete(member)
            db.session.commit()
            # check the deletion to see if it is successful or not
            health_after = Health.query.first()
            post_after = Post.query.first()
            member_after = Customer.query.first()
            self.assertIsNone(health_after)
            self.assertIsNone(post_after)
            self.assertIsNone(member_after)
            course = Course.query.first()  # course can be deleted without key constrains
            record = course.cid
            db.session.delete(course)
            db.session.commit()
            # finally, delete the coach
            coach = Coach.query.filter_by(cid=record).first()
            db.session.delete(coach)
            db.session.commit()
            # check the deletion to see if it is successful or not
            coach_after = Coach.query.first()
            course_after = Course.query.first()
            self.assertIsNone(coach_after)
            self.assertIsNone(course_after)

        def tearDown(self):
            pass
            # db.session.remove()
            # db.drop_all()


if __name__ == '__main__':
    unittest.main()
