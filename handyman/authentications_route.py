import os
import secrets
from flask import Flask,render_template,redirect,request,flash,url_for,session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash,generate_password_hash
from handyman import app 
from handyman.form import SignupForm,LoginForm,ProfileForm,UpdateForm,SetForm
from handyman.models import User,State,Lga,db,Handyservice,Userservice

def confirm_log(id):
    data=db.session.query(User).get(id)
    return data if data else None

@app.route('/handyman/email/checks/')
def email_checks():
    email_supplied=request.args.get('email')
    status='Email Available'
    email_checks=db.session.query(User).filter(User.user_email==email_supplied).first()
    if email_checks:
        status='Email already in use'
    return status





@app.route('/handyman/username/checks/')
def username_checks():
    username_supplied=request.args.get('username')
    status='Username is available'
    username_checks=db.session.query(User).filter(User.user_username==username_supplied).first()
    if username_checks:
        status='Username Taken'
    return status
    





@app.route('/handyman/lga/loads/')
def load_lgas():
    state_id=request.args.get('id')
    lgas=db.session.query(Lga).filter(Lga.lga_state_id==state_id).all()
    opt=''
    for lga in lgas:

        lgaid=lga.lga_id
        lganame=lga.lga_name

        opt=opt+f"<option value='{lgaid}'>{lganame}</option>"
    return opt




#signup authentication
@app.route('/handyman/signup/user/',methods=['POST','GET'])
def sign_up():
    user_online=None
    user_id = session.get('user_id')

    if user_id:  
        user_online = confirm_log(user_id)

        if user_online is None:
            session.clear() 
            flash('You have been successfully logged out. Please log in again to continue.', 'info') 
            return redirect(url_for('login'))
                            
    services=db.session.query(Handyservice).all()
    form=SignupForm()
    if form.validate_on_submit():
        fname=form.firstname.data
        lname=form.lastname.data
        phone=form.phone_no.data
        email=form.email.data
        username=form.username.data
        pass1=form.password.data
        pass2=form.confirmpassword.data
        address=form.address.data
        state_id=request.form.get('state')            
        lga_id=request.form.get('lga')
        services_selected=request.form.getlist('services')
        agree=form.agreement.data
        
        if state_id=='' or lga_id=='':
            flash('Please all field are required','error')
            return redirect(url_for('sign_up'))
        elif pass1!=pass2:
            flash('The two passwords must match','error')
            return redirect(url_for('sign_up'))
        else:
            hashed=generate_password_hash(pass1)
            data=User(
                user_firstname=fname,
                user_lastname=lname,
                user_phone=phone,
                user_email=email,
                user_username=username,
                user_address=address,
                user_password=hashed,
                user_state_id=state_id,
                user_lga_id=lga_id)
            try:
                db.session.add(data)
                if services_selected:
                    for service_id in services_selected:
                        userservices=Userservice(
                            handyservice_id=service_id,
                            user_id=data.user_id)
                        db.session.add(userservices)
                db.session.commit()
                flash('An account has been created for you','success')
                return redirect(url_for('login'))
            except:
                db.session.rollback()
                flash('Email or Username already exists . Please use a different email and usename.','error')
                return redirect(url_for('sign_up'))  
    else:
        states=db.session.query(State).all()
        return render_template('user/signup.html',states=states,form=form,services=services,user_online=user_online)    






# login form        

@app.route('/handyman/login/')
def login():
    form=LoginForm()
    user_online=None
    user_id = session.get('user_id')

    if user_id:  
        user_online = confirm_log(user_id)

        if user_online is None:
            session.clear() 
            flash('You have been successfully logged out. Please log in again to continue.', 'info') 
            return redirect(url_for('login')) 
        
    return render_template('user/login.html',form=form,user_online=user_online)





# login validation

@app.route('/handyman/submit/login/',methods=['POST','GET'])
def login_submit():
    form=LoginForm()
    if form.validate_on_submit():

        username=form.username.data
        password=form.password.data

        valid_user=db.session.query(User).filter(User.user_username == username).first()
        if valid_user:
            hashed_password=valid_user.user_password
            check=check_password_hash(hashed_password,password)
            if valid_user.user_status=='active' and valid_user.user_deleted == 'false':
                if check:
                    session['user_id']=valid_user.user_id
                    flash('Successfully logged in please make use of the side menu to carry out tasks on this platform','success')
                    return redirect('/handyman/mydashboard/')
                else:
                    flash('Password is incorrect','error')
                    return redirect(url_for('login'))
            else:
                flash('Your account has been banned due to supicious activity','error')
                return redirect(url_for('home'))
        else:
            flash('Invalid username','error')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    




# logout validation

@app.route('/handyman/logout/')
def log_out():
    if session.get('user_id') != None:
        session.pop('user_id')
        flash('You are now logged out','success')
    else:
        flash('You are not logged in', 'error')
    return redirect(url_for('home'))


#forgot password
@app.route('/handyman/forgot/password/',methods=['GET','POST'])
def set_new_password():
    form=SetForm()
    user_online=None
    user_id = session.get('user_id')

    if user_id:  
        user_online = confirm_log(user_id)

        if user_online is None:
            session.clear() 
            flash('You have been successfully logged out. Please log in again to continue.', 'info') 
            return redirect(url_for('login'))
          
    return render_template('user/change_pwd.html',form=form,user_online=user_online)



#forgot password validation
@app.route('/submit/forgot/password/',methods=['POST'])
def submit_new_password():
    form=SetForm()
    if form.validate_on_submit():

        username=form.username.data
        pwd=form.password.data
        confirmpwd=form.confirmpassword.data
        
        if not pwd or not confirmpwd or not username:

            flash('Please all fields are required', 'error')
            return redirect(url_for('set_new_password'))
        
        elif pwd != confirmpwd:

            flash('The two passwords must match', 'error')
            return redirect(url_for('set_new_password'))
        
        else:

            user=db.session.query(User).filter(User.user_username==username).first()
            if not user:
                flash('The username you entered is incorrect', 'error')
                return redirect(url_for('set_new_password'))
            
            elif user.user_status == 'disabled' or user.user_deleted == 'true':
                flash('Your account has been banned due to suspicious activity', 'error')
                return redirect(url_for('home'))
            
            else:
                hashed = generate_password_hash(pwd)
                user.user_password = hashed
                db.session.commit()
                flash('Passord sucessfully Updated','Success')
                return redirect(url_for('login'))
    
    flash('Form validation failed. Please try again.', 'error')
    return redirect(url_for('set_new_password'))    


# update password
@app.route('/handyman/update/password/', methods=['GET', 'POST'])
def update_password():
    form = UpdateForm()
    user_id = session.get('user_id')

    if user_id:  
        user_online = confirm_log(user_id)

        if user_online is None:
            session.clear() 
            flash('User not found', 'error')
            return redirect(url_for('login'))
        return render_template('user/update_pwd.html', form=form, user_online=user_online)
    else:
        flash('You need to log in to access this page', 'error')
        return redirect(url_for('login'))


# update password page
@app.route('/submit/updated/password/', methods=['POST'])
def submit_updated_password():
    form = UpdateForm()
    user_id = session.get('user_id')

    if user_id:
        if form.validate_on_submit():
            pwd = form.password.data
            confirmpwd = form.confirmpassword.data
            
            
            if not pwd or not confirmpwd:
                flash('Please fill in all fields', 'error')
                return redirect(url_for('update_password'))
            
            
            if pwd != confirmpwd:
                flash('Passwords do not match', 'error')
                return redirect(url_for('update_password'))
            
            
            user = db.session.query(User).filter_by(user_id=user_id, user_status='active', user_deleted='false'
            ).first()
            
            if user:
                hashed_pwd = generate_password_hash(pwd)
                user.user_password = hashed_pwd
                db.session.commit()
                
                flash('Password successfully updated', 'success')
                return redirect(url_for('user_dashboard'))
            else:
                session.clear()
                flash('An issue occurred. Please log in and try again.', 'error')
                return redirect(url_for('login'))
    else:
        flash('Please log in to update your password', 'error')
        return redirect(url_for('login'))

     
    


# profile update default display and  validation

# @app.route('/handyman/editprofile/',methods=["POST","GET"])
# def edit_profile():
    form = ProfileForm()
    if session.get('user_id') != None:
        user_id = session.get('user_id')
        user_online = db.session.query(User).get(user_id)
        user_services = db.session.query(Userservice).filter_by(user_id=user_id).all()
        all_services=db.session.query(Handyservice).all()
        if request.method=='GET':
            form.firstname.data=user_online.user_firstname
            form.lastname.data=user_online.user_lastname
            form.phone_no.data=user_online.user_phone
            form.email.data=user_online.user_email
            form.address.data=user_online.user_address
            state=user_online.state.state_name
            lga=user_online.lga.lga_name
            if user_online.user_business_name != None or user_online.user_business_name !='':
                form.businessname.data=user_online.user_business_name
            else:
                form.businessname.data=''

            if user_online.user_bio != None or user_online.user_bio != '':
                form.biography.data=user_online.user_bio
            else:
                form.biography.data=''

            if user_online.user_dp != None:
                form.dp.data=user_online.user_dp
            else:
                form.dp.data = None

            if len(user_services) == 0 or user_services==[]:
                    user_services = None
            else:      
                # for sev in user_services:
                #     sev.handy_service.handyservice_name
                #     print(sev.handy_service.handyservice_name)
                pass
        else:
            if form.validate_on_submit():
                firstname=form.firstname.data
                lastname=form.lastname.data
                phone_no=form.phone_no.data
                email=form.email.data
                address=form.address.data
                state_name=request.form.get('state')
                lga_name=request.form.get('lga')
                business_name=form.businessname.data
                user_bio=form.biography.data
                profile_pic=request.files.get('profile_pic')
                orginal_pic=profile_pic.filename
                services=request.form.getlist('services')
                allowed=['jpg','png','gif']
                user_table=db.session.query(User).filter(User.user_id==user_id).first()
                if orginal_pic != '':
                    if orginal_pic in allowed:
                        pieces=os.path.split(orginal_pic)
                        ext=pieces[1]
                        name_ext=secrets.token_hex(12)
                        profile_pic.save('/static/users_images/'+name_ext+ext)
                        user_table.user_dp=name_ext+ext
                    else:
                        flash('Please picture format should only be in "JPG", "PNG", "GIF" format ')
                user_table.user_firstname=firstname
                user_table.user_lastname=lastname
                user_table.user_phone=phone_no
                user_table.user_email=email
                user_table.user_address=address
                user_table.user_state_id=state_name
                user_table.user_lga_id=lga_name
                user_table.user_business_name=business_name
                user_table.user_bio=user_bio
                if services:
                    for service in services:
                        user_services.user_id=user_id
                        user_services.handyservice_id=service
                db.session.commit()
                flash('Click on view profile to confirm all changes made','success')
                return redirect(url_for('user_dashboard'))
        states=db.session.query(State).all()
        return render_template('user/edit_profile.html', form=form, user_online=user_online, all_services=all_services,states=states)
    else:
        flash('You need to log in to edit your profile.', 'error')
        return redirect(url_for('login'))
    



@app.route('/handyman/editprofile/', methods=["POST", "GET"])
def edit_profile():
    user_id = session.get('user_id')

    if user_id:  
        user_online = confirm_log(user_id)

        if user_online is None:
            session.clear() 
            flash('Session expired or user not found', 'error')
            return redirect(url_for('login'))
        else:
            states = db.session.query(State).all()
            user_services = db.session.query(Userservice).filter_by(user_id=user_id).all()
            all_services = db.session.query(Handyservice).all()
            selected_services = [service.handyservice_id for service in user_services]
            
            return render_template('user/edit_profile.html', user_online=user_online, selected_services=selected_services, 
                                    all_services=all_services, states=states)
    else:
        flash('You need to log in to access this page', 'error')
        return redirect(url_for('login'))
    

@app.route('/handyman/submit/updated/profile/',methods=['POST'])
def submit_updated_profile():
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        phone_no = request.form.get('phone_no')
        email = request.form.get('email')
        address = request.form.get('address')
        state_id = request.form.get('state')
        lga_id = request.form.get('lga')
        business_name = request.form.get('businessname')
        biography = request.form.get('biography')
        profile_pic = request.files.get('profile_pic')
        services = request.form.getlist('services')

        user_id = session.get('user_id')
        user_profile = db.session.query(User).filter(User.user_id == user_id).first()
        if not all((firstname,lastname,phone_no,email,address,state_id,lga_id)):
            flash('Please the listed fields (firstname, lastname, phone_no, email, address, state_name ,lga_name) cannot be empty','error')
            return redirect(url_for('edit_profile'))
        if profile_pic:
            allowed = ['jpg', 'png', 'gif']
            original_pic = profile_pic.filename
            if original_pic.split('.')[-1] in allowed:
                ext = os.path.splitext(original_pic)[1]
                name_ext = secrets.token_hex(12) + ext
                profile_pic.save('handyman/static/users_images/'+name_ext)
                user_profile.user_dp = name_ext
            else:
                flash('Please upload an image in JPG, PNG, or GIF format', 'error')
                return redirect(url_for('edit_profile'))
        user_profile.user_firstname = firstname
        user_profile.user_lastname = lastname
        user_profile.user_phone = phone_no
        user_profile.user_email = email
        user_profile.user_address = address
        user_profile.user_state_id = state_id
        user_profile.user_lga_id = lga_id
        user_profile.user_business_name = business_name
        user_profile.user_bio = biography

        if services:
            db.session.query(Userservice).filter_by(user_id=user_id).delete()
            for service_id in services:
                new_service = Userservice(user_id=user_id, handyservice_id=service_id)
                db.session.add(new_service)
        try:
            db.session.commit()
            flash('Profile updated successfully. Check your profile to confirm changes.', 'success')
            return redirect(url_for('edit_profile'))
        except Exception as e:
            db.session.rollback()
            flash('Something went wrong. Please try again','error')
            print(f'Something went wrong : {e}')
            return redirect(url_for('edit_profile'))






    # if session.get('user_id') != None:
    #     user_id = session.get('user_id')
    #     user_online = db.session.query(User).get(user_id)
    #     user_services = db.session.query(Userservice).filter_by(user_id=user_id).all()
    #     all_services = db.session.query(Handyservice).all()

        
        
    #    

    #         

    #         
                
    #        
    #        

    #        

    #     states = db.session.query(State).all()
    #     return render_template('user/edit_profile.html', 
    #                            user_online=user_online, 
    #                            user_services=user_services, 
    #                            all_services=all_services, 
    #                            states=states)

    # else:
    #     flash('You need to log in to edit your profile.', 'error')
    #     return redirect(url_for('login'))










