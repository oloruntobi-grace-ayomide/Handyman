import os
import secrets
from flask import Flask,render_template,redirect,request,abort,flash,url_for,session,jsonify
from werkzeug.security import check_password_hash,generate_password_hash
from handyman import app,db
from handyman.form import ContactForm,SearchForm,AdminForm,AdminSignupForm,ServiceForm
from handyman.models import User,State,Lga,Handyservice,Review,Admin,AppReview


def confirm_admin(id):
    data=db.session.query(Admin).get(id)
    return data if data else None


@app.route('/handyman/admin/workspace/',methods=['GET'])
def admin_home():
        admin_id = session.get('admin_id')

        if admin_id:  
            admin_online = confirm_admin(admin_id)

            if admin_online is None:
                session.clear() 
                flash('You have been successfully logged out. Please log in again to continue.', 'info') 
                return redirect(url_for('admin_login'))  
  
            return render_template('admin/admin_dashboard.html',admin_online=admin_online)
        else:
            flash('You need to login to access this page','error')
            return redirect(url_for('admin_login'))



#login form

@app.route('/handyman/admin/login/')
def admin_login():
    form=AdminForm()
    admin_online=None
    admin_id = session.get('admin_id')

    if admin_id:  
        admin_online = confirm_admin(admin_id)

        if admin_online is None:
            session.clear() 
            flash('You have been successfully logged out. Please log in again to continue.', 'info') 
            return redirect(url_for('admin_login')) 
        
    return render_template('admin/login.html',form=form,admin_online=admin_online) 


#login validation
@app.route('/handyman/admin/validate/login/', methods=['POST'])
def admin_submit_login():
    form = AdminForm()

    if form.validate_on_submit():

        username = form.username.data
        email = form.email.data
        password = form.password.data

        if not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('admin_login'))
        
        valid_admin = db.session.query(Admin).filter(Admin.admin_username == username,Admin.admin_email == email).first()

        if valid_admin and check_password_hash(valid_admin.admin_password, password):
            session['admin_id'] = valid_admin.admin_id  
            flash('Successfully Logged in', 'success')
            return redirect(url_for('admin_home'))
        else:
            flash('Invalid username, email, or password', 'error')
            return redirect(url_for('admin_login'))
    else:
        flash('Please fill in all fields correctly', 'error')
        return redirect(url_for('admin_login'))



#logout


@app.route('/handyman/admin/logout/')
def admin_log_out():
    logged_in = session.get('admin_id')
    if logged_in != None:
        session.pop('admin_id')
        flash('You are now logged out','success')
    else:
        flash('You are not logged in', 'error')
    return redirect(url_for('home'))


#view all users profile


@app.route('/handyman/admin/view/profiles/',methods=['GET','POST'])
def view_profiles():
    admin_id = session.get('admin_id')

    if admin_id:  
        admin_online = confirm_admin(admin_id)

        if admin_online is None:
            session.clear() 
            flash('You have been successfully logged out. Please log in again to continue.', 'info') 
            return redirect(url_for('admin_login'))
        
        format = request.args.get('sortedby', 'asc') 
        limits=request.args.get('limits', 25)
        search=request.args.get('search')
        
        try:
            limits = int(limits)
        except ValueError:
            limits = 25
        
        if format == 'desc':
            if search:
                all_users=db.session.query(User).filter(User.user_username.ilike(f'%{search}%') |
                User.user_firstname.ilike(f'%{search}%') | User.user_lastname.ilike(f'%{search}%')
                    ).order_by(User.user_id.desc()).limit(limits).all()
            else:
                all_users=db.session.query(User).order_by(User.user_id.desc()).limit(limits).all()  
        else:
            if search:
                all_users=db.session.query(User).filter(User.user_username.ilike(f'%{search}%') |
                User.user_firstname.ilike(f'%{search}%') | User.user_lastname.ilike(f'%{search}%')
                    ).limit(limits).all()
            else:
                all_users=db.session.query(User).limit(limits).all()
        return render_template('admin/view_profiles.html', admin_online= admin_online, 
             limits=limits, all_users=all_users, sortedby=format)
    
    else:
        flash('Login to access this page', 'error')
        return redirect(url_for('admin_login'))     
    



#delete of account
@app.route('/admin/handyman/delete/acount/',methods=['POST'])
def delete_account():

    todelete=request.form.get('data2send')

    if todelete:
        account = db.session.query(User).filter(User.user_id==todelete).first()

        if account and account.user_deleted == 'false' :

            if account.user_status == 'active':
                account.user_status = 'disabled'

            account.user_deleted = 'true'
           
            db.session.commit()
            return f"User with id of {account} as been deleted successfully",200
        else:
            return f"User with id of {account} does not exit ",200
    else:
        return "Nothing was sent",400
    


# acitvating and deacivating of accounts

@app.route('/handyman/activate/disactivate/account/', methods=['POST','GET'])
def activate_account():

    status_info=request.form.get('statusmode')
    user_id=request.form.get('user_id')

    if status_info and user_id:

        user = User.query.filter_by(user_id=user_id).first()
        if user.user_status != status_info:
                user.user_status = status_info  
                db.session.commit()
                return f"User status updated to {status_info}",200
        else:
            return "No changes made. User already has this status.",404
    else:
        return "Something Went wrong",400



#display all handy services on admin dashboard

@app.route('/admin/handyman/handy/services/',methods=['GET'])
def handle_services():
        admin_id = session.get('admin_id')

        if admin_id:  
            admin_online = confirm_admin(admin_id)

            if admin_online is None:
                session.clear() 
                flash('You have been successfully logged out. Please log in again to continue.', 'info') 
                return redirect(url_for('admin_login'))
            
            sort=request.args.get('sortby','asc')
            limit=request.args.get('limit', 25)
            search=request.args.get('search')
            try:
                limit=int(limit)
            except ValueError:
                limit= 25
            if sort == 'desc':
                if search:
                    services=db.session.query(Handyservice).filter(Handyservice.handyservice_name.ilike(f'%{search}%') | 
                        Handyservice.handyservice_icon_alt.ilike(f'%{search}%') | 
                        Handyservice.handyservice_id.ilike(f'%{search}%') ).order_by(Handyservice.handyservice_id.desc()).limit(limit).all()
                else:
                    services=db.session.query(Handyservice).order_by(Handyservice.handyservice_id.desc()).limit(limit).all()
            else:
                if search:
                    services=db.session.query(Handyservice).filter(Handyservice.handyservice_name.ilike(f'%{search}%') |
                        Handyservice.handyservice_icon_alt.ilike(f'%{search}%') |
                        Handyservice.handyservice_id.ilike(f'%{search}%')).limit(limit).all()
                else:
                    services=db.session.query(Handyservice).limit(limit).all()
            form=ServiceForm()
            return render_template('admin/servicesview.html',
                admin_online=admin_online,services=services,form=form, limit=limit, sortby=sort)

        else:
            flash('Login to access this page', 'error')
            return redirect(url_for('admin_login'))     
        


#function to edit service
@app.route('/admin/handyman/edit/default/service/', methods=['POST'])
def edit_service():

    if session.get('admin_id') is None:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    try:

        service_id = request.form.get('serviceid')
        servicename = request.form.get('servicename')
        serviceiconalt = request.form.get('serviceiconalt')
        description = request.form.get('description')
        icon = request.files.get('icon')
        picture = request.files.get('picture')
        service = Handyservice.query.filter(Handyservice.handyservice_id==service_id).first()
        if not all((servicename,serviceiconalt,description)):
             return jsonify({'success': False, 'message': 'Service name field, service icon alt and sercice description caannot be empty  '}), 404
        if icon and icon.filename != '':
                original_icon = icon.filename
                ext = os.path.splitext(original_icon)[1]
                icon_filename = secrets.token_hex(10)
                icon.save(f"handyman/static/images/{icon_filename}{ext}")
                icon_path = icon_filename + ext
        else:
            icon_path= service.handyservice_icon
        if picture:
            orignal_filename = picture.filename
            ext = os.path.splitext(orignal_filename)[1]
            picture_filename = secrets.token_hex(10)
            picture.save(f"handyman/static/images/{ picture_filename}{ext}")
            picture_path =  picture_filename+ ext
        else:
           picture_path = service.handyservice_picture
        
        if not service:
            return jsonify({'success': False, 'message': 'Service not found'}), 404
        else:
            service.handyservice_name=servicename
            service.handyservice_description=description
            service.handyservice_icon_alt=serviceiconalt

            if icon:
                service.handyservice_icon = icon_path

            if picture:
                service.handyservice_picture = picture_path

            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Service updated successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500



#delete of account
@app.route('/admin/handyman/delete/service/',methods=['POST'])
def delete_service():
    todelete=request.form.get('data2send')
    if todelete:
        service= db.session.query(Handyservice).filter(Handyservice.handyservice_id==todelete).first()
        if service:
            db.session.delete(service)
            db.session.commit()
            return f"User with id of {service} as been deleted successfully",200
        else:
            return f"User with id of {service} does not exit ",200
    else:
        return "Nothing was sent",400




# function to add more services
@app.route('/admin/handyman/add/service/', methods=['POST'])
def add_services():
    form=ServiceForm()

    if form.validate_on_submit():
        servicename=form.service_name.data
        servicedescription=form.description.data
        service_alt=form.service_icon_alt.data
        service_icon=request.files.get('icon')
        service_picture=request.files.get('picture')
        original_icon=service_icon.filename
        original_picture=service_picture.filename

        if not servicename or not servicedescription or not service_alt  or not service_icon:
            flash('All fields are required except the sercice picture field')
            return redirect(url_for('handle_services'))
        
        else:

            if service_icon and service_icon.filename != '':
                original_icon = service_icon.filename
                ext = os.path.splitext(original_icon)[1]
                newfilename = secrets.token_hex(10)
                service_icon.save(f"handyman/static/images/{newfilename}{ext}")
                icon_path = newfilename + ext

            else:
                flash('Service Icon is required', 'error')
                return redirect(url_for('handle_services'))
            
            if service_picture and service_picture.filename != '':
                original_picture = service_picture.filename
                ext = os.path.splitext(original_picture)[1]
                extfilename = secrets.token_hex(10)
                service_picture.save(f"handyman/static/images/{extfilename}{ext}")
                picture_path = extfilename + ext
            else:
                picture_path = None

            toadd=Handyservice(
                handyservice_name=servicename,
                handyservice_description=servicedescription,
                handyservice_icon=icon_path,
                handyservice_icon_alt=service_alt,
                handyservice_picture=picture_path)
            
            try:
                db.session.add(toadd)
                db.session.commit()
                flash('Service added successfully','success')
                return redirect(url_for('handle_services'))
            except Exception as e:
                flash('Failed to add service', 'error')
                return redirect(url_for('handle_services'))
    flash('Form validation failed', 'error')
    return redirect(url_for('handle_services'))


# review function

@app.route('/admin/handyman/users/reviews/',methods=['POST','GET'])
def user_reviews():
    admin_id = session.get('admin_id')

    if admin_id:  
        admin_online = confirm_admin(admin_id)

        if admin_online is None:
            session.clear() 
            flash('You have been successfully logged out. Please log in again to continue.', 'info') 
            return redirect(url_for('admin_login'))
        
        sort_reviews = request.args.get('sortby')
        limit_reviews = request.args.get('limit', 25)
        search = request.args.get('search')
        try:
            limit_reviews = int(limit_reviews)
        except ValueError:
            limit_reviews = 25

        if sort_reviews =='desc':
            if search:
                reviews=db.session.query(Review).join(User.reviews_given).filter(Review.review_id.ilike(f'%{search}%') | 
                    User.user_username.ilike(f'%{search}%') |
                    User.user_username.ilike(f'%{search}%') | User.user_firstname.ilike(f'%{search}%') |
                    User.user_lastname.ilike(f'%{search}%')
                    ).order_by(Review.review_id.desc()).limit(limit_reviews).all()
            else:
              reviews=db.session.query(Review).order_by(Review.review_id.desc()).limit(limit_reviews).all()  
        else:
            if search:
                reviews=db.session.query(Review).join(User.reviews_given).filter(Review.review_id.ilike(f'%{search}%') | 
                    User.user_username.ilike(f'%{search}%') |
                    User.user_username.ilike(f'%{search}%')|
                    User.user_firstname.ilike(f'%{search}%') |
                    User.user_lastname.ilike(f'%{search}%')).limit(limit_reviews).all()
            else:
                reviews=db.session.query(Review).limit(limit_reviews).all()
        return render_template('admin/see_reviews.html',reviews=reviews,admin_online=admin_online, sort_reviews=sort_reviews , limit_reviews=limit_reviews)
    else:
        flash('Login to access this page','error')
        return redirect(url_for('admin_login'))


@app.route('/handyman/activate/disactivate/reviews/', methods=['POST'])
def activate_deactivate():

    status_info=request.form.get('statusmode')
    review_id=request.form.get('reviewid')

    if status_info and  review_id:
        review = Review.query.filter(Review.review_id == review_id).first()
        
        if review.review_status != status_info:
                
                review.review_status = status_info  
                db.session.commit()
                return f"User status updated to {status_info}",200
        else:
            return "No changes made. User already has this status.",404
    else:
        return "Something Went wrong",400



@app.route('/admin/handyman/delete/review/',methods=['POST'])
def delete_review():
    todelete=request.form.get('data2send')
    if todelete:
        review= db.session.query(Review).filter(Review.review_id==todelete).first()
        if review:
            db.session.delete(review)
            db.session.commit()
            return f"User with id of {review} as been deleted successfully",200
        else:
            return f"User with id of {review} does not exit ",200
    else:
        return "Nothing was sent",400




@app.route('/admin/handyman/see/app/reviews/',methods=['POST','GET'])
def app_reviews():
    admin_id = session.get('admin_id')

    if admin_id:  
        admin_online = confirm_admin(admin_id)

        if admin_online is None:
            session.clear() 
            flash('You have been successfully logged out. Please log in again to continue.', 'info') 
            return redirect(url_for('admin_login'))
        
        sort_app_reviews = request.args.get('sortby')
        limit_app_reviews = request.args.get('limit', 25)
        search = request.args.get('search')
        try:
            limit_app_reviews = int(limit_app_reviews)
        except ValueError:
            limit_app_reviews = 25

        if sort_app_reviews =='desc':
            if search:
                
                reviews=db.session.query(AppReview).join(User).filter(
                    AppReview.app_review_id.ilike(f'%{search}%') |
                    User.user_username.ilike(f'%{search}%') | User.user_firstname.ilike(f'%{search}%') |
                    User.user_lastname.ilike(f'%{search}%')).order_by(AppReview.app_review_id.desc()).limit(limit_app_reviews).all()
                
            else:
                reviews=db.session.query(AppReview).order_by(AppReview.app_review_id.desc()).limit(limit_app_reviews).all()
        else:
            if search:

                reviews=db.session.query(AppReview).join(User).filter(
                    AppReview.app_review_id.ilike(f'%{search}%') |
                    User.user_username.ilike(f'%{search}%') | User.user_firstname.ilike(f'%{search}%') |
                    User.user_lastname.ilike(f'%{search}%')).limit(limit_app_reviews).all()
                
            else:

                reviews=db.session.query(AppReview).limit(limit_app_reviews).all()
        return render_template('admin/app_review.html',reviews=reviews,admin_online=admin_online,
            sort_app_reviews=sort_app_reviews, limit_app_reviews=limit_app_reviews)
    else:
        flash('Login to access this page','error')
        return redirect(url_for('admin_login'))
    

@app.route('/handyman/activate/disactivate/app/reviews/', methods=['POST'])
def activate_deactivate_app_reviews():

    status_info=request.form.get('statusmode')
    review_id=request.form.get('reviewid')

    if status_info and  review_id:
        review = AppReview.query.filter(AppReview.app_review_id == review_id).first()

        if review.app_review_status != status_info:
                review.app_review_status = status_info  
                db.session.commit()
                return f"User status updated to {status_info}",200
        else:
            return "No changes made. User already has this status.",404
    else:
        return "Something Went wrong",400



@app.route('/admin/handyman/delete/app/review/',methods=['POST'])
def delete_app_review():
    todelete=request.form.get('data2send')

    if todelete:
        review= db.session.query(AppReview).filter(AppReview.app_review_id==todelete).first()
        if review:
            db.session.delete(review)
            db.session.commit()
            return f"User with id of {review} as been deleted successfully",200
        else:
            return f"User with id of {review} does not exit ",200
    else:
        return "Nothing was sent",400








#signup


# @app.route('/handyman/admin/validate/signup/', methods=['GET','POST'])
# def admin_submit_sign_up():
#     form=AdminSignupForm()
#     if form.validate_on_submit():
#         fullname=form.fullname.s
#         phone=form.phone_no.s
#         email=form.email.s
#         username=form.username.s
#         password=form.password.s
#         if username =='' or password=='' or email=='' or fullname=='' or phone=='':
#             flash('All fields are required','error')
#             redirect(url_for('admin_login'))
#         else:
#             hashed=generate_password_hash(password)
#             admin=Admin(admin_username=username,admin_fullname=fullname,admin_email=email,admin_phone=phone,admin_password=hashed)
#             try:
#                 db.session.add(admin)
#                 db.session.commit()
#                 return redirect(url_for('admin_login'))
#             except:
#                 flash('something went wrong','error')
#                 return redirect(url_for('admin_submit_sign_up'))
#     return render_template('admin/sign_up.html',form=form)