import datetime
import json
import os
import time
from app import app, db, bcrypt, mail
from app.forms import ManagerLogin, ForgetPassword, UpdateAccountFrom, ResetPassword, \
    ManagerAccountFrom, Membership, UpdateCoachFrom, PostFrom, NewCourse
from app.model import Coach, Customer, Course, Health, Manager, Post, Connect
from flask import render_template, flash, request, session, url_for, redirect
from flask_login import logout_user, login_user, current_user, login_required
from flask_mail import Message

try:
    from PIL import Image
except Exception:
    Image = None

try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
except Exception:
    VideoFileClip = None


@app.route('/')
def welcome():
    form = ForgetPassword()
    app.logger.info("Index page (App started successfully).")
    return render_template("login.html", form=form)

@app.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('CustomerLogin'))
    else:
        return render_template("register.html")

@app.route('/addMember')
def addMember():
    if current_user.is_authenticated and session.get('role') == 'Manager':
        return render_template("register.html")
    else:
        flash('Manager Login authentication is required for this operation!')
        return redirect(url_for('CustomerLogin'))


@app.route('/addCoach')
def addCoach():  # managers can create new account
    if current_user.is_authenticated and session.get('role') == 'Manager':
        return render_template("NewCoach.html")
    else:
        flash('Login authentication is required for this operation!')
        return redirect(url_for('CustomerLogin'))


@app.route('/addManager')
def addManager():  # managers can create new account
    if current_user.is_authenticated and session.get('role') == 'Manager':
        return render_template("NewManager.html")
    else:
        flash('Login authentication is required for this operation!')
        return redirect(url_for('CustomerLogin'))


@app.route('/deleteCoach', methods=['POST', 'GET'])
def deleteCoach():  # managers can delete coach
    if current_user.is_authenticated and session.get('role') == 'Manager':
        target = request.args.get('id')
        target_user = Coach.query.filter_by(cid=target).first()
        target_course = Course.query.filter_by(cid=target).all()
        try:
            for course in target_course:  # delete all the courses of the coach
                db.session.delete(course)
            db.session.delete(target_user)
            db.session.commit()
            app.logger.info(target_user.username + " has been deleted. Action by: " + current_user.username)
            flash("Coach: " + target_user.username + " has been deleted!")
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s', e)
            app.logger.warning("Coach: " + target_user.username + "delete failed. Action by: " + current_user.username)
            raise e
    else:
        flash('Login authentication is required for this operation!')
    return redirect(url_for('CustomerLogin'))


@app.route('/deleteManager', methods=['POST', 'GET'])
def deleteManager():  # Super manager can delete managers
    if current_user.is_authenticated and session.get('role') == 'Manager':
        target = request.args.get('id')
        target_user = Manager.query.filter_by(aid=target).first()
        try:
            db.session.delete(target_user)
            db.session.commit()
            app.logger.info(target_user.username + " has been deleted. Action by: " + current_user.username)
            flash("Manager: " + target_user.username + " has been deleted.")
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s', e)
            app.logger.warning(
                "Manager: " + target_user.username + "delete failed. Action by: " + current_user.username)
            raise e
    else:
        flash('Login authentication is required for this operation!')
    return redirect(url_for('CustomerLogin'))


@app.route('/deleteMember', methods=['POST', 'GET'])
def deleteMember():  # managers can delete members
    if current_user.is_authenticated and session.get('role') == 'Manager':
        target = request.args.get('id')
        target_user = Customer.query.filter_by(id=target).first()
        target_health = Health.query.filter_by(uid=target).first()
        target_posts = Post.query.filter_by(uid=target).all()
        try:
            db.session.delete(target_health)
            db.session.commit()
            for post in target_posts:  # delete all the posts of the user
                db.session.delete(post)
                db.session.commit()
            db.session.delete(target_user)
            db.session.commit()
            app.logger.info(target_user.username + "has been deleted. Action by: " + current_user.username)
            flash("Customer: " + target_user.username + " has been deleted.")
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s', e)
            app.logger.warning("Customer: " + target_user.username + "delete failed. Action by: "
                               + current_user.username)
            raise e
    else:
        flash('Login authentication is required for this operation!')
    return redirect(url_for('CustomerLogin'))


@app.route("/logout")
def logout():
    role = request.args.get('role')
    user = request.args.get('user')
    if role == 'Admin':
        log = Manager.query.first()
    elif role == 'manager':
        log = Manager.query.filter_by(username=user).first()
    elif role == 'customer':
        log = Customer.query.filter_by(username=user).first()
    elif role == 'coach':
        log = Coach.query.filter_by(username=user).first()
    try:
        log.log = 0  # set the login status to be offline
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error('%s', e)
        raise e
    logout_user()  # log the user out form the session
    session.pop('role')
    return redirect(url_for('newlogin'))


@app.route('/manager')
def manager():  # manager login
    form = ManagerLogin()
    form1 = ForgetPassword()
    app.logger.debug("Opening manager login page")
    return render_template("Managerlogin.html", form=form, form1=form1)


@app.route('/Managerlogin', methods=['GET', 'POST'])
def Managerlogin():  # log in a super admin
    form = ManagerLogin()
    form1 = ForgetPassword()
    if form.validate_on_submit():
        Admin = Manager.query.first()  # the first one is the super manager
        if Admin.username == form.username.data and bcrypt.check_password_hash(Admin.password, form.password.data):
            try:
                Admin.log = 1  # set the login status to be online
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.error('%s', e)
                raise e
            if form.remember.data:
                login_user(Admin, remember=True)
                session['role'] = 'Manager'
            app.logger.info(Admin.username + " logged in successfully.")
            return render_template("Managermenu.html", user=Admin.username, man='Admin', role=Admin)
        elif Admin.username == form.username.data and not bcrypt.check_password_hash(Admin.password,
                                                                                     form.password.data):
            app.logger.warning(Admin.username + "log in failed due to Password error.")
            flash("Password is invalid! Validate e-mail to retrieve.")
        elif Admin.username != form.username.data:
            app.logger.warning(Admin.username + "log in failed.")
            flash("Username is wrong!")
        return render_template("Managerlogin.html", form=form, form1=form1)
    if request.method == 'GET':
        return render_template("error.html", errormessage="Direct URL visit is not allowed!")
    else:
        return render_template("error.html")


@app.route('/Managers', methods=['POST', 'GET'])
def Managers():  # log in a normal manager
    if request.method == 'POST':
        testname = request.form.get("name")
        testpassword = request.form.get("psw")
        # check in database
        checkuser = Manager.query.all()
        checkuser.pop(0)  # all managers since the first one is super manager
        for check in checkuser:
            if (check.username == testname and
                    bcrypt.check_password_hash(check.password, testpassword)):
                name = check.username  # username should be passed to the home page
                try:
                    check.log = 1  # set the login status to be online
                    app.logger.info("Manager: " + check.username + " has logged in.")
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    app.logger.error('%s', e)
                    raise e
                if request.form.get('remember'):
                    login_user(check, remember=True)
                    session['role'] = 'Manager'
                app.logger.info(check.username + " (manager) has logged in.")
                return render_template("NormalManager.html", user=name, man='manager', role=check)
            # if login fails, show error message
            elif (check.username == testname and not bcrypt.check_password_hash(
                    check.password, testpassword)):
                flash("Password is wrong! Please re-enter!", "error")
                app.logger.warning(testname + " logged in failed! (Password error)")
                return redirect(url_for('newlogin'))
            # else, no such user
        flash("No such user:" + testname + " ! Please register first!", "error")
        app.logger.warning(testname + " logged in failed! (No such manager)")
        return redirect(url_for('newlogin'))
    if request.method == 'GET':
        return render_template("error.html", errormessage="Direct URL visit is not allowed!")
    else:
        return render_template("error.html")


@app.route('/CustomerLogin', methods=['GET', 'POST'])
def CustomerLogin():
    if request.method == 'POST':
        testname = request.form.get("name")
        testpassword = request.form.get("psw")
        man = request.form.get("type")
        if man == "customer":
            checkuser = Customer.query.all()  # all customers
            for check in checkuser:
                if (check.username == testname and
                        bcrypt.check_password_hash(check.password, testpassword)):
                    name = check.username  # username should be passed to the home page
                    now = check.id
                    health_person = Health.query.filter_by(uid=now).first()  # get the health data of this customer
                    try:
                        check.log = 1  # set the login status to be online
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error('%s', e)
                        raise e
                    # calculate the age of a user
                    today = datetime.date.today()
                    birth = health_person.birthday
                    if today > birth:
                        age = today.year - birth.year
                    else:
                        age = today.year - birth.year - 1
                    # login the user
                    if request.form.get('remember'):
                        login_user(check, remember=True)
                        session['role'] = 'customer'
                    app.logger.info(check.username + " (customer) has logged in.")
                    return render_template("Customerlogin.html", user=name, man=man, role=check, health=health_person,
                                           age=age)
                elif (check.username == testname and not bcrypt.check_password_hash(
                        check.password, testpassword)):  # wrong password error
                    flash("Password is wrong! Please re-enter!", "error")
                    app.logger.warning(testname + " logged in denied! (Password error)")
                    return redirect(url_for('newlogin'))
        else:  # coach log in
            checkuser = Coach.query.all()  # all coaches
            for check in checkuser:
                if (check.username == testname and
                        bcrypt.check_password_hash(check.password, testpassword)):
                    name = check.username  # username should be passed to the home page
                    try:
                        check.log = 1  # set the login status to be online
                        db.session.commit()
                        app.logger.info(name + " logged in successfully!")
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error('%s', e)
                        raise e
                    # login the user
                    if request.form.get('remember'):
                        login_user(check, remember=True)
                        session['role'] = 'Coach'
                    app.logger.info(check.username + " (coach) has logged in.")
                    return render_template("Coachlogin.html", user=name, man=man, role=check)
                elif (check.username == testname and not bcrypt.check_password_hash(
                        check.password, testpassword)):  # wrong password error
                    flash("Password is wrong! Please re-enter!", "error")
                    app.logger.warning(testname + " logged in denied! (Password error)")
                    return redirect(url_for('newlogin'))
        # no such customer or coach, return to login page and show error messages
        flash("No such user: " + testname + " !", "error")
        app.logger.warning(testname + " logged in failed! (No such user)")
        return redirect(url_for('newlogin'))
    # for redirect routes
    if request.method == 'GET':
        if current_user.is_authenticated:  # a logged-in user should be redirected back to the home page
            name = current_user.username
            man = session.get('role')
            if man == 'customer':
                health_person = Health.query.filter_by(
                    uid=current_user.id).first()  # get the health data of this customer
                today = datetime.date.today()
                birth = health_person.birthday
                if today > birth:
                    age = today.year - birth.year
                else:
                    age = today.year - birth.year - 1
                message = 'you have already logged in!'
                flash(message, 'success')
                return render_template("Customerlogin.html", user=name, man=man, role=current_user,
                                       health=health_person,
                                       age=age)
            elif man == 'Manager':  # redirect managers back
                message = 'you have already logged in!'
                flash(message, 'success')
                if current_user.id == 1:
                    keep = 'Admin'
                    return render_template("Managermenu.html", user=current_user.username, man=keep, role=current_user)
                else:
                    keep = "manager"
                    return render_template("NormalManager.html", user=current_user.username, man=keep,
                                           role=current_user)
            elif man == 'Coach':  # redirect managers back
                message = 'you have already logged in!'
                flash(message, 'success')
                return render_template("Coachlogin.html", user=current_user.username, man='coach', role=current_user)
            else:
                return render_template("error.html", errormessage="Accessed denied! Please login.")
        else:
            return render_template("error.html", errormessage="Accessed denied! Please login.")
    else:
        return render_template("error.html")


@app.route('/newlogin')
def newlogin():  # goback to login page
    if current_user.is_authenticated:  # a logged-in in user should stay in the system
        return redirect(url_for('CustomerLogin'))
    else:
        form = ForgetPassword()
        app.logger.info("redirect to login page(customer and coach)")
        return render_template("login.html", form=form)


def send_reset_email(user):
    token = user.get_reset_token()  # get the token of customer log in
    msg = Message('Password Reset Request',
                  sender=app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com'),
                  recipients=[user.Email])
    msg.body = f'''To reset your password, visit the following link within 30 Minutes:
    
{url_for('Reset_password', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route('/Request_password_reset', methods=['POST', 'GET'])
def Request_password_reset():
    if current_user.is_authenticated:  # a logged-in in user should stay in the system
        return redirect(url_for('CustomerLogin'))
    form = ForgetPassword()
    if form.validate_on_submit():
        role = form.CustomerType.data
        if role == "Customer":
            user = Customer.query.filter_by(username=form.username.data).first()  # find the customer
        if role == "Coach":
            user = Coach.query.filter_by(username=form.username.data).first()  # find the coach
        if role == "Manager":
            user = Manager.query.filter_by(username=form.username.data).first()  # find the manager
        if user:
            if user.Email == form.email.data:  # if user's email address is valid
                send_reset_email(user)
                flash('An email has been sent to retrieve your password.')
            else:
                flash('Email is Wrong. Request denied.')
        else:
            flash('Username is Invalid. Register first.')
        return redirect(url_for('newlogin'))


@app.route('/Reset_password/<token>', methods=['POST', 'GET'])
def Reset_password(token):
    if current_user.is_authenticated:  # a logged-in in user should stay in the system
        return redirect(url_for('CustomerLogin'))
    user = Customer.verify_reset_token(token)  # search for all members
    coach = Coach.verify_reset_token(token)  # search for all coaches
    Mana = Manager.verify_reset_token(token)  # search for all managers
    checklist = [user, coach, Mana]
    count = 0
    for role in checklist:
        if role is not None:
            target = role
        else:
            count = count + 1
    # if all checks failed, error message is send
    if count == 3:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('newlogin'))
    form = ResetPassword()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        target.password = hashed_password
        try:
            db.session.commit()
            app.logger.info(target.username + "has updated password.")
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s', e)
            raise e
        flash('Your password has been updated!', 'success')
        return redirect(url_for('newlogin'))
    # else, go back to the same page
    return render_template("reset_password.html", form=form)


@app.route('/newCoach', methods=['POST', 'GET'])
def newCoach():  # sign up route for customers
    if request.method == 'POST':
        # validate user's message
        newname = request.form.get("name")
        mail = request.form.get("mailenter")
        gender = request.values.getlist('gender')
        # encrypt the password
        hashed_psw = bcrypt.generate_password_hash(request.form.get("psw")).decode('utf-8')
        # validate inputs in data base
        checkuser = Coach.query.all()  # all Coaches
        for alluser in checkuser:
            if alluser.username == newname:
                flash("That user name has been taken! please choose another one!", 'error')
                return render_template("NewCoach.html")
        # save customer data into DB
        user = Coach()
        user.username = newname
        user.password = hashed_psw
        user.Email = mail
        user.sex = gender
        if gender[0] == '0':  # unknown sex
            user.cprofile = "../static/coachProfile/default_none.jpg"
        if gender[0] == '1':  # male
            user.cprofile = "../static/coachProfile/default_male.jpg"
        if gender[0] == '2':  # female
            user.cprofile = "../static/coachProfile/default_female.jpg"
        user.speciality = "all"  # default value
        try:
            db.session.add(user)
            db.session.commit()
            flash("Coach: " + user.username + " has been added!")
            app.logger.info("Coach: " + user.username + " has been added. Action by: " + current_user.username)
        except Exception as e:
            db.session.rollback()
            app.logger.error("Coach: " + user.username + "addition failed. Action by: " + current_user.username)
            app.logger.error('%s', e)
            raise e
        return redirect(url_for('CustomerLogin'))
    if request.method == 'GET':
        if current_user.is_authenticated and session.get('role') == 'Manager':  # Managers should use panels to access
            flash("Do not use Direct URL visits. Use function panels instead.")
        else:
            flash("Illegal visit. (Higher authentications required.)", 'info')
        return redirect(url_for('CustomerLogin'))
    else:
        return render_template("error.html")


@app.route('/newManager', methods=['POST', 'GET'])
def newManager():  # sign up route for manager
    if request.method == 'POST':
        # validate user's message
        newname = request.form.get("name")
        mail = request.form.get("mailenter")
        gender = request.values.getlist('gender')
        # encrypt the password
        hashed_psw = bcrypt.generate_password_hash(request.form.get("psw")).decode('utf-8')
        # validate inputs in data base
        checkuser = Manager.query.all()  # all Coaches
        for alluser in checkuser:
            if alluser.username == newname:
                flash("That user name has been taken! pelase choose another one!", 'error')
                return render_template("NewCoach.html")
        # save customer data into DB
        user = Manager()
        user.username = newname
        user.password = hashed_psw
        user.Email = mail
        user.log = 0  # set to be offline
        try:
            db.session.add(user)
            db.session.commit()
            flash("Manager: " + user.username + " has been added!")
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s', e)
            raise e
        return redirect(url_for('CustomerLogin'))
    if request.method == 'GET':
        if current_user.is_authenticated:  # a logged-in in user should stay in the system
            if current_user.id == 1 and session.get('role') == 'Manager':  # Managers should use panels to access
                flash("Do not use Direct URL visits. Use function panels instead.")
            else:
                flash("Illegal visit. (Higher authentications required.)", 'info')
            return redirect(url_for('CustomerLogin'))
    else:
        return render_template("error.html")


@app.route('/newAccount', methods=['POST', 'GET'])
def newAccount():  # sign up route for customers
    if request.method == 'POST':
        # validate user's message
        newname = request.form.get("name")
        mail = request.form.get("mailenter")
        psw = request.form.get('psw')
        gender = request.values.getlist('gender')
        # encrypt the password
        hashed_psw = bcrypt.generate_password_hash(
            request.form.get("psw")).decode('utf-8')

        # validate inputs in data base
        checkuser = Customer.query.all()  # all users
        for all in checkuser:
            if (all.username == newname):
                flash("That user name has been taken! please choose another one!", 'error')
                return render_template("register.html")
        # save customer data into DB
        user = Customer()
        user.username = newname
        user.password = hashed_psw
        user.Email = mail
        user.status = 0  # 0 represents trail user
        user.log = 0  # 0 for offline since it's just registration now
        user.sex = gender
        if gender[0] == '0':  # unknown sex
            user.profile = "../static/customerProfile/default_none.jpg"
        if gender[0] == '1':  # male
            user.profile = "../static/customerProfile/default_male.jpg"
        if gender[0] == '2':  # female
            user.profile = "../static/customerProfile/default_female.jpg"
        user.posts = 0  # no posts send yet
        try:
            db.session.add(user)
            db.session.commit()
            app.logger.info("User registration success.")
        except Exception as e:
            db.session.rollback()
            app.logger.warning("User registration failed.")
            app.logger.error('%s', e)
            raise e
        currentuser = Customer.query.all()
        # create a health data for shown
        data = Health()
        data.uid = currentuser[len(currentuser) - 1].id
        data.prefer = "None"
        data.height = 0
        data.weight = 0
        data.birthday = datetime.date.today()  # create time
        data.aim_weight = 0

        try:
            db.session.add(data)
            db.session.commit()
            # show success message
            flash(f"{newname}" + " have registered successfully!", 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s', e)
            raise e
        form = ForgetPassword()
        return render_template("login.html", username=newname, password=psw, form=form)
    if request.method == 'GET':
        if current_user.is_authenticated:  # a logged-in in user should stay in the system
            flash("DO NOT use url to access! Choose from menu panel instead.", 'info')
            return redirect(url_for('CustomerLogin'))
        else:
            return render_template("error.html", errormessage="Direct URL visit is not allowed!")
    else:
        return render_template("error.html")


@app.route('/Showaccount', methods=['POST', 'GET'])
@login_required
def showAccount():
    form = UpdateAccountFrom()
    health_person = Health.query.filter_by(uid=current_user.id).first()
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.Email
        form.gender.data = current_user.sex
        form.birthday.data = health_person.birthday
        form.weight.data = health_person.weight
        form.height.data = health_person.height
        form.aim.data = health_person.aim_weight
        form.prefer.data = health_person.prefer
    user = str(current_user.__class__)  # set the class of user one screen
    if "Customer" in user:
        user = 'Customer'
    elif "Coach" in user:
        user = "Coach"
    elif "Manager" in user:
        user = "Manager"
    return render_template("ajax/account.html", role=user, user=current_user, form=form, health=health_person)


def save_picture(form_picture):
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = current_user.username + f_ext  # userprofile is named after its unique username
    picture_path = os.path.join(app.root_path, 'static/customerProfile', picture_fn)
    # delete if user profile already exists
    if os.path.exists(picture_path):
        os.remove(picture_path)
    # resize the picture before saving it
    output_size = (200, 200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/updateAccount', methods=['POST', 'GET'])
def updateAccount():
    if request.method == 'GET':
        flash("Url visit is not allowed!")
        return redirect(url_for('CustomerLogin'))
    form = UpdateAccountFrom()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile = "../static/customerProfile/" + picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.sex = form.gender.data
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s', e)
            raise e
        health = Health.query.filter_by(uid=current_user.id).first()
        health.height = form.height.data
        health.weight = form.weight.data
        health.birthday = form.birthday.data
        health.aim_weight = form.aim.data
        health.prefer = form.prefer.data
        try:
            db.session.add(health)
            db.session.commit()
            app.logger.info(current_user.username + " account updated successfully")
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s', e)
            raise e
        flash("Your Account has been updated!", 'warning')
        return redirect(url_for('CustomerLogin'))
    else:
        app.logger.error(current_user.username + "update account failed: " + form.errors)
        return render_template("error.html", errormessage=form.errors)


@app.route('/ShowCoachaccount', methods=['POST', 'GET'])
@login_required
def ShowCoachaccount():
    form = UpdateCoachFrom()
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.Email
        form.gender.data = current_user.sex
        form.speciality.data = current_user.speciality
    user = str(current_user.__class__)  # set the class of user one screen
    if "Customer" in user:
        user = 'Customer'
    elif "Coach" in user:
        user = "Coach"
    elif "Manager" in user:
        user = "Manager"
    return render_template("ajax/Coachaccount.html", role=user, user=current_user, form=form)


def save_picture_coach(form_picture):
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = current_user.username + f_ext  # coach profile is named after its unique username
    picture_path = os.path.join(app.root_path, 'static/coachProfile', picture_fn)
    # delete if user profile already exists
    if os.path.exists(picture_path):
        os.remove(picture_path)
    # resize the picture before saving it
    output_size = (200, 200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/updateCoachAccount', methods=['POST', 'GET'])
def updateCoachAccount():
    if request.method == 'GET':
        if session.get('role') != 'Manager':
            flash("Illegal visit. (Higher authentications required.)", 'info')
            return redirect(url_for('CustomerLogin'))
    form = UpdateCoachFrom()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture_coach(form.picture.data)
            current_user.cprofile = "../static/coachProfile/" + picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.sex = form.gender.data
        current_user.speciality = form.speciality.data
        try:
            db.session.commit()
            app.logger.info("Coach:" + current_user.username + " has updated account.")
        except Exception as e:
            db.session.rollback()
            app.logger.info("Coach:" + current_user.username + " update account failed.")
            app.logger.error('%s', e)
            raise e
        flash("Your Account has been updated!", 'warning')
        return redirect(url_for('CustomerLogin'))
    else:
        app.logger.warning(current_user.username + "update account failed")
        return render_template("error.html", errormessage=form.errors)


@app.route('/Manageraccount', methods=['POST', 'GET'])
@login_required
def Manageraccount():
    form = ManagerAccountFrom()
    form1 = ForgetPassword()
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.Email
    user = str(current_user.__class__)  # set the class of user one screen
    if "Customer" in user:
        user = 'Customer'
    elif "Coach" in user:
        user = "Coach"
    elif "Manager" in user:
        user = "Manager"
    return render_template("ajax/managerAccount.html", role=user, user=current_user, form=form, form1=form1)


@app.route('/updateManager', methods=['POST', 'GET'])
def updateManager():
    if request.method == 'GET':
        if session.get('role') != 'Manager' or current_user.id != 1:
            flash("Illegal visit. (Higher authentications required.)", 'info')
            return redirect(url_for('CustomerLogin'))
    form = ManagerAccountFrom()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s', e)
            raise e
        flash("Your Account has been updated!", 'warning')
        return redirect(url_for('CustomerLogin'))
    else:
        app.logger.warning(current_user.username + "update account failed")
        return render_template("error.html", errormessage=form.errors)


@app.route('/ShowManager', methods=['POST', 'GET'])
def ShowManager():
    if request.method == 'GET':
        if session.get('role') != 'Manager' or current_user.id != 1:
            flash("Illegal visit. (Higher authentications required.)", 'info')
            return redirect(url_for('CustomerLogin'))
    all_users = Manager.query.all()
    all_users.pop(0)  # the first one is the general manager himself
    # for manager online status
    online = 0
    offline = 0
    for test in all_users:
        if test.log == 0:
            offline = offline + 1
        if test.log == 1:
            online = online + 1
    status = {"Online": online, "Offline": offline}
    return render_template("ajax/Managers.html", members=all_users, status=status)


@app.route('/ShowCoach', methods=['GET'])
def ShowCoach():
    if request.method == 'GET':
        if session.get('role') == 'customer':
            my_coach = Coach.query.join(Connect, Coach.cid == Connect.cid) \
                .join(Customer, Connect.id == current_user.id).all()
            return render_template("ajax/ShowCoaches.html", members=my_coach)
        if session.get('role') != 'Manager':
            flash("Illegal visit. (Higher authentications required.)", 'info')
            return redirect(url_for('CustomerLogin'))


@app.route('/Showblog', methods=['POST', 'GET'])
def Showblog():
    form = PostFrom()
    # pagination of posts
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=3)
    return render_template("ajax/blog.html", form=form, user=current_user, posts=posts)


@app.route('/ShowblogInpage', methods=['POST', 'GET'])
def ShowblogInpage():  # separate page for blog display
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=3)
    return render_template("ajax/blogInpage.html", user=current_user, posts=posts)


def save_post_picture(form_picture):
    f_name, f_ext = os.path.splitext(form_picture.filename)
    # post is named after host's username and timestamp
    picture_fn = current_user.username + time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())) + f_ext
    picture_path = os.path.join(app.root_path, 'static/post', picture_fn)
    # delete if user profile already exists
    if os.path.exists(picture_path):
        os.remove(picture_path)
    # resize the picture before saving it
    output_size = (350, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/createPost', methods=['POST', 'GET'])
def createPost():
    if request.method == 'GET':
        flash("Url visit is not allowed!")
        return redirect(url_for('CustomerLogin'))
    target = request.form.get('target')
    form = PostFrom()
    if form.validate_on_submit():
        post = Post()
        post.uid = target
        post.description = form.description.data
        post.tag = form.tag.data
        if form.picture.data:
            picture_file = save_post_picture(form.picture.data)
            post.photo = "../static/post/" + picture_file
        try:
            db.session.add(post)
            db.session.commit()
            user = Customer.query.filter_by(id=target).first()
            user.posts = user.posts + 1
            db.session.commit()
            app.logger.info(current_user.username + " post a blog.")
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s' + current_user.username + " post a blog failed.", e)
            raise e
        flash("Your blog has been posted!", 'warning')
        app.logger.info(current_user.username + "has posted a blog.")
    else:
        app.logger.error(form.errors)
        flash("Post failed!" + form.errors)
    return redirect(url_for('CustomerLogin'))


@app.route('/deletePost', methods=['POST', 'GET'])
def deletePost():
    if request.method == 'Post':
        flash("Access denied!")
    if request.method == 'GET':
        target = request.args.get('target')
        delete = Post.query.filter_by(id=target).first()
        try:
            db.session.delete(delete)
            db.session.commit()
            flash("Blog has been deleted!", 'info')
            app.logger.info(current_user.username + " deleted blog: " + target)
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s' + current_user.username + " delete blog" + target + " failed.", e)
            flash("Blog deletion failed!", 'info')
            raise e
    return redirect(url_for('CustomerLogin'))


@app.route('/Showdata', methods=['POST', 'GET'])
def Showdata():
    if request.method == 'GET':
        if session.get('role') != 'Manager':
            flash("Illegal visit. (Higher authentications required.)", 'info')
            return redirect(url_for('CustomerLogin'))
    all_Customers = Customer.query.all()
    # for customer membership chart
    free = 0
    valid = 0
    overdue = 0
    frozen = 0
    for test in all_Customers:
        if test.status == 0:
            free = free + 1
        if test.status == 1:
            valid = valid + 1
        if test.status == 2:
            overdue = overdue + 1
        if test.status == 3:
            frozen = frozen + 1
    membership = {"Free trail": free, "Valid members": valid, "Overdue": overdue, "Frozen": frozen}
    # for customer gender chart
    unknown = 0
    male = 0
    female = 0
    for test in all_Customers:
        if test.sex == 0:
            unknown = unknown + 1
        if test.sex == 1:
            male = male + 1
        if test.sex == 2:
            female = female + 1
    sex = {"Unknown": unknown, "Male": male, "Female": female}
    # for customer online status
    online = 0
    offline = 0
    for test in all_Customers:
        if test.log == 0:
            offline = offline + 1
        if test.log == 1:
            online = online + 1
    status = {"Online": online, "Offline": offline}
    all_Coaches = Coach.query.all()
    # for coach gender chart
    unknown = 0
    male = 0
    female = 0
    for test in all_Coaches:
        if test.sex == 0:
            unknown = unknown + 1
        if test.sex == 1:
            male = male + 1
        if test.sex == 2:
            female = female + 1
    sex_0 = {"Unknown": unknown, "Male": male, "Female": female}
    # for coach speciality chart
    swim = 0
    strength = 0
    yoga = 0
    fitting = 0
    All = 0
    for test in all_Coaches:
        if test.speciality == 'swimming':
            swim = swim + 1
        if test.speciality == 'strength':
            strength = strength + 1
        if test.speciality == 'yoga':
            yoga = yoga + 1
        if test.speciality == 'fitting':
            fitting = fitting + 1
        if test.speciality == 'all':
            All = All + 1
    s_1 = {"Swimming": swim, "Strength": strength, "Yoga": yoga, "Fitting": fitting, "All": All}
    online = 0
    offline = 0
    all_managers = Manager.query.all()
    all_managers.pop(0)
    for test in all_managers:
        if test.log == 0:
            offline = offline + 1
        if test.log == 1:
            online = online + 1
    man_status = {"Online": online, "Offline": offline}
    # sales data
    swim_cus = 0
    strength_cus = 0
    yoga_cus = 0
    fitting_cus = 0
    a_ll_cus = 0
    swim_c = 0
    strength_c = 0
    yoga_c = 0
    fitting_c = 0
    a_ll_c = 0
    all_cus = Health.query.all()
    for cus in all_cus:
        if cus.prefer == 'swimming':
            swim_cus = swim_cus + 1
        if cus.prefer == 'strength':
            strength_cus = strength_cus + 1
        if cus.prefer == 'yoga':
            yoga_cus = yoga_cus + 1
        if cus.prefer == 'fitting':
            fitting_cus = fitting_cus + 1
        if cus.prefer == 'all':
            a_ll_cus = a_ll_cus + 1
    for coa in all_Coaches:
        if coa.speciality == 'swimming':
            swim_c = swim_c + 1
        if coa.speciality == 'strength':
            strength_c = strength_c + 1
        if coa.speciality == 'yoga':
            yoga_c = yoga_c + 1
        if coa.speciality == 'fitting':
            fitting_c = fitting_c + 1
        if coa.speciality == 'all':
            a_ll_c = a_ll_c + 1
    sales = [['Category', 'Swimming', 'Strength', 'Yoga', 'Fitting', 'All'],
             ['Customer', swim_cus, strength_cus, yoga_cus, fitting_cus, a_ll_cus],
             ['Coach', swim_c, strength_c, yoga_c, fitting_c, a_ll_c]]
    return render_template("ajax/visual.html", sex=json.dumps(sex), status=status, membership=membership,
                           sex_0=sex_0, s_1=s_1, sex_1=man_status, sales=json.dumps(sales), author=current_user.id)


@app.route('/ShowCustomer', methods=['POST', 'GET'])
def ShowCustomer():
    if request.method == 'GET':
        if session.get('role') != 'Manager':
            flash("Illegal visit. (Higher authentications required.)", 'info')
            return redirect(url_for('CustomerLogin'))
    all_users = Customer.query.all()
    form = Membership()
    return render_template("ajax/Customers.html", members=all_users, form=form)


@app.route('/Editmember', methods=['POST', 'GET'])
def Editmember():
    if request.method == 'GET':
        if session.get('role') != 'Manager':
            flash("Illegal visit. (Higher authentications required.)", 'info')
            return redirect(url_for('CustomerLogin'))
    form = Membership()
    target = request.form.get('target')
    target_user = Customer.query.filter_by(id=target).first()
    if form.validate_on_submit():
        target_user.status = form.membership.data
        try:
            db.session.add(target_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error('%s', e)
            raise e
        app.logger.info(target_user.username + " membership has been updated to level: " + str(form.membership.data)
                        + " Action by: " + current_user.username)
        flash(target_user.username + " has been updated")
    else:
        flash(target_user.username + "update failed" + form.errors)
        app.logger.warning("update failed" + form.errors + " Action by: " + current_user.username)
    return redirect(url_for('CustomerLogin'))


@app.route('/AddCourse', methods=['POST', 'GET'])
def AddCourse():
    form = NewCourse()
    return render_template("ajax/addCourse.html", form=form, user=current_user)


def save_course_profile(form_picture):
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = current_user.username + time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())) + f_ext
    picture_path = os.path.join(app.root_path, 'static/Course/cover', picture_fn)
    # delete if user profile already exists
    if os.path.exists(picture_path):
        os.remove(picture_path)
    # resize the picture before saving it
    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def save_course_video(form_video):
    f_name, f_ext = os.path.splitext(form_video.filename)
    video_fn = current_user.username + time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())) + f_ext
    video_path = os.path.join(app.root_path, 'static/Course/video', video_fn)
    # delete if user profile already exists
    if os.path.exists(video_path):
        os.remove(video_path)
    form_video.save(video_path)
    # resize large videos (>10MB)
    if os.path.getsize(video_path) > 10000000:
        clip = VideoFileClip(video_path)
        temp = video_path
        video_fn = "_Compressed_" + video_fn
        video_path = os.path.join(app.root_path, 'static/Course/video', video_fn)
        clip.write_videofile(video_path, bitrate='2500000', threads=None)
        os.remove(temp)  # delete the old video file
    return video_fn


@app.route('/newCourse', methods=['POST', 'GET'])
def newCourse():
    coach = request.form.get('coach')
    form = NewCourse()
    if request.method == "POST":
        if form.validate_on_submit():
            course = Course()
            course.cid = coach
            course.name = form.cname.data
            course.description = form.description.data
            course.start = form.start.data
            course.end = form.end.data
            if form.cprofile.data:
                cover_file = save_course_profile(form.cprofile.data)
                course.courseProfile = "../static/Course/cover/" + cover_file
            if form.video.data:
                video_file = save_course_video(form.video.data)
                course.video = "../static/Course/video/" + video_file
            try:
                db.session.add(course)
                db.session.commit()
                app.logger.info(current_user.username + " Created a course.")
            except Exception as e:
                db.session.rollback()
                app.logger.error('%s' + current_user.username + " Creat a course failed.", e)
                raise e
            flash("New course has been released!", 'warning')
            app.logger.info(current_user.username + "has posted a blog.")
        else:
            app.logger.error(form.errors)
            flash("Course creation failed!" + str(form.errors))
        return redirect(url_for('CustomerLogin'))
    if request.method == "GET":
        if session.get('role') != "Coach":
            flash("Illegal url visit!")
        else:
            flash("Do not use URL visit! Use panel instead.")
        return redirect(url_for('CustomerLogin'))


@app.route('/DeleteCourse', methods=['GET'])
def DeleteCourse():
    if request.method == "GET":
        if session.get('role') != "Coach":
            flash("Illegal url visit!")
        else:
            target = request.args.get('target')
            target_connect = Connect.query.filter_by(courseid=target).all()
            target_course = Course.query.filter_by(id=target).first()
            try:
                for item in target_connect:
                    db.session.delete(item)
                    db.session.commit()
                db.session.delete(target_course)
                db.session.commit()
                flash(current_user.username + " Deleted course:" + target_course.name, 'info')
                app.logger.info(current_user.username + " Deleted course:" + target_course.name)
            except Exception as e:
                db.session.rollback()
                flash(current_user.username + " Failed to deleted course:" + target_course.name, 'info')
                app.logger.error('%s' + current_user.username + " Failed to deleted course:" + target_course.name, e)
                raise e
        return redirect(url_for('CustomerLogin'))
    else:
        return render_template("error.html")


@app.route('/ShowAllCourse', methods=['POST', 'GET'])
def ShowAllCourse():
    if request.method == "GET":
        if session.get('role') != 'customer':
            return render_template('error.html', errormessage="Only gym customers can access this page!")
        else:
            page = request.args.get('page', 1, type=int)
            all_courses = db.session.query(Course, Coach).join(Course, Coach.cid == Course.cid) \
                .order_by(Course.start).paginate(page=page, per_page=3)
            return render_template("ajax/ShowCourses.html", course=all_courses, user=current_user)
    else:
        return render_template('error.html', errormessage="Invalid operation!")


@app.route('/ShowcourseInpage', methods=['GET'])
def ShowcourseInpage():  # separate page for course display
    page = request.args.get('page', 1, type=int)
    all_courses = db.session.query(Course, Coach).join(Course, Coach.cid == Course.cid) \
        .order_by(Course.start).paginate(page=page, per_page=3)
    return render_template("ajax/CourseInpage.html", user=current_user, course=all_courses)


@app.route('/JoinCourse', methods=['POST'])
def JoinCourse():
    operator = request.form.get('operator')
    target_coach = request.form.get('target')
    target_course = request.form.get('choose')
    chosen_courses = Connect.query.filter_by(id=operator).all()
    for item in chosen_courses:  # a course can't be chosen twice
        if item.courseid == int(target_course):
            flash("You have already chosen this course!", 'info')
            return redirect(url_for('CustomerLogin'))
    choose = Connect(operator, target_coach, target_course)
    coach = Coach.query.filter_by(cid=target_coach).first()
    try:
        db.session.add(choose)
        db.session.commit()
        flash("You have chosen course of coach: " + coach.username, 'info')
        app.logger.info(current_user.username + " joined course of coach:"
                        + coach.username)
    except Exception as e:
        db.session.rollback()
        flash("You have chosen course of coach: " + coach.username + " failed.", 'info')
        app.logger.error(current_user.username + " failed to joined course of coach:"
                         + coach.username, e)
        raise e
    return redirect(url_for('CustomerLogin'))


@app.route('/CancelCourse', methods=['GET'])
def CancelCourse():
    operator = request.args.get('operator')
    target_course = request.args.get('target')
    canceling = Course.query.filter_by(id=target_course).first()
    chosen_courses = Connect.query.filter_by(id=operator).all()
    for item in chosen_courses:  # a course can't be chosen twice
        if item.courseid == int(target_course):
            try:
                db.session.delete(item)
                db.session.commit()
                flash("You have canceled course:" + canceling.name, 'info')
                app.logger.info(current_user.username + " canceled course:" + canceling.name)
            except Exception as e:
                db.session.rollback()
                flash("Cancellation of course of coach: " + canceling.name + " failed.", 'info')
                app.logger.error(current_user.username + " failed to cancel course:" + canceling.name, e)
                raise e
    return redirect(url_for('CustomerLogin'))


@app.route('/ShowMycourse', methods=['GET'])
def ShowMycourse():
    page = request.args.get('page', 1, type=int)
    my_courses = Course.query.join(Connect, Course.id == Connect.courseid) \
        .join(Customer, Connect.id == current_user.id).paginate(page=page, per_page=3)
    return render_template("ajax/ShowMyCourses.html", user=current_user, course=my_courses)


@app.route('/ShowStudent', methods=['GET'])
def ShowStudent():
    if request.method == 'GET':
        if session.get('role') == 'Coach':
            students = Customer.query.join(Connect, Customer.id == Connect.id)\
                .join(Coach, Connect.cid == current_user.cid).all()
            return render_template("ajax/Students.html", members=students)
        if session.get('role') != 'Manager':
            flash("Illegal visit. (Higher authentications required.)", 'info')
            return redirect(url_for('CustomerLogin'))
    return render_template("error.html")


@app.route('/ShowMycourseInpage', methods=['GET'])
def ShowMycourseInpage():  # separate page for my_course display
    if request.method == "GET":
        if session.get('role') != 'customer':
            return render_template('error.html', errormessage="Only gym customers can access this page!")
        else:
            page = request.args.get('page', 1, type=int)
            my_courses = Course.query.join(Connect, Course.id == Connect.courseid) \
                .join(Customer, Connect.id == current_user.id).paginate(page=page, per_page=3)
            return render_template("ajax/MyCoursesInpage.html", user=current_user, course=my_courses)
    else:
        return render_template('error.html', errormessage="Invalid operation!")


@app.route('/ShowCoachcourse', methods=['GET'])
def ShowCoachcourse():
    if request.method == "GET":
        if session.get('role') != 'Coach':
            return render_template('error.html', errormessage="Only Coach can access this page!")
        else:
            page = request.args.get('page', 1, type=int)
            coach_courses = Course.query.filter_by(cid=current_user.cid).order_by(Course.start)\
                .paginate(page=page, per_page=3)
            return render_template("ajax/CoachCourses.html", course=coach_courses, user=current_user)
    else:
        return render_template('error.html', errormessage="Invalid operation!")


@app.route('/ShowCoachcourseInpage', methods=['GET'])
def ShowCoachcourseInpage():  # separate page for my_course display
    page = request.args.get('page', 1, type=int)
    coach_courses = Course.query.filter_by(cid=current_user.cid).order_by(Course.start) \
        .paginate(page=page, per_page=3)
    return render_template("ajax/MyCoursesInpage.html", user=current_user, course=coach_courses)
