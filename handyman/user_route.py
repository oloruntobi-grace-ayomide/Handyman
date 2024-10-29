import re
from datetime import datetime, timedelta
from flask import Flask,render_template,redirect,request,abort,flash,url_for,session,jsonify
from flask_mail import Message
from handyman import app,db,mail
from handyman.form import ContactForm,SearchForm
from handyman.models import User,State,Lga,Handyservice,Review,Userservice,Newlettersubscriber,AppReview,Notification

@app.after_request
def after_request(response):
    response.headers['Cache-Control']='no-cache, no-store, must-revalidate'
    return response

def confirm_logs(id):
    data=db.session.query(User).get(id)
    return data if data else None


@app.route('/handyman/subscribe/email/', methods=['POST'])
def subscribe_email():
    user_id = session.get('user_id')

    if not user_id:
        flash('Please log in to subscribe to our newsletter', 'error')
        return redirect(url_for('login'))

    user_online = confirm_logs(user_id)

    if not user_online:
        session.clear()
        flash('You have been successfully logged out. Please log in again to continue.', 'info')
        return redirect(url_for('login'))

    subscriber = request.form.get('subscriber-email')
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if not subscriber:
        flash('Email field cannot be empty.', 'error')
        return redirect(request.referrer)

    if not re.match(email_regex, subscriber):
        flash('Please enter a valid email address.', 'error')
        return redirect(request.referrer)


    
    check_user = db.session.query(User).filter_by(user_email=subscriber).first()
    if not check_user or user_online.user_email != subscriber:
        flash('You can only subscribe with the email you used in registering', 'error')
        return redirect(request.referrer)
    
    if user_online.user_status != 'active' or user_online.user_deleted == 'true':
        session.clear()
        flash('Account has been banned due to suspicious activity on the platform.', 'error')
        return redirect(url_for('home'))

    
    existing_subscription = db.session.query(Newlettersubscriber).filter_by(subscriber_email=subscriber).first()
    if existing_subscription:
        flash('You are already a subscriber.', 'success')
        return redirect(request.referrer)

   

    new_subscriber = Newlettersubscriber(subscriber_email=subscriber)
    db.session.add(new_subscriber)
    db.session.commit()
    flash('Thanks for subscribing to our newsletter.', 'success')
    return redirect(request.referrer)



@app.route('/',methods=['GET', 'POST'])
def home_page():
    if request.method == 'GET':

        user_online=None
        user_id = session.get('user_id')

        if user_id:  
            user_online = confirm_logs(user_id)

            if user_online is None:
                session.clear() 
                flash('You have been successfully logged out. Please log in again to continue.', 'info') 
                return redirect(url_for('login'))  

        services = db.session.query(Handyservice).limit(8).all()
        app_reviews = db.session.query(AppReview).limit(4).all()
        return render_template('user/index.html',services=services,user_online=user_online, app_reviews=app_reviews)  
    




@app.route('/handyman/home/',methods=['GET', 'POST'])
def home():
    if request.method == 'GET':

        user_online=None
        user_id = session.get('user_id')

        if user_id:  
            user_online = confirm_logs(user_id)

            if user_online is None:
                session.clear() 
                flash('You have been successfully logged out. Please log in again to continue.', 'info') 
                return redirect(url_for('login'))  

        services = db.session.query(Handyservice).limit(8).all()
        app_reviews = db.session.query(AppReview).limit(4).all()
        return render_template('user/index.html',services=services,user_online=user_online, app_reviews=app_reviews)  
    


@app.route('/handyman/about-us/')
def about_us():
    user_online=None
    user_id = session.get('user_id')

    if user_id:  
            user_online = confirm_logs(user_id)

            if user_online is None:
                session.clear() 
                flash('You have been successfully logged out. Please log in again to continue.', 'info') 
                return redirect(url_for('login'))     
    return render_template('user/about.html',user_online=user_online)



@app.route('/handyman/contact-us/',methods=['GET','POST'])
def contact_us():
    form=ContactForm()
    if form.validate_on_submit():
        customer_name=form.customername.data
        customer_phone=form.customerphone.data
        customer_email=form.customeremail.data
        customer_message=form.customermessage.data
        customer_time=form.besttime.data

        if customer_name is None or customer_phone is None or customer_email is None or customer_message is None or customer_time is None:
            flash('Please fill or fields','error')
            return redirect(url_for('contact_us'))
        else:
            admin_email = "ayomigrace291@gmail.com"
            msg = Message(
                subject="New Contact Us Form Submission",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[admin_email]
            )
            msg.html= f"""
            <h3 style='color:white; background-color:blue; text-align:center; padding:20px 5px;'> You have a new message from the contact form</h3>
            <p> Name: {customer_name} </p>
            <p> Phone: {customer_phone} </p>
            <p> Email: {customer_email} </p>
            <p> Best Time to Contact: {customer_time} </p>
            
            Message:
            {customer_message}
            """
            try:
                mail.send(msg)
                flash('Your message has been sent successfully!', 'success')
            except Exception as e:
                flash('There was an issue sending your message. Please try again.', 'error')
                print(f"Email send error: {e}")
            return redirect(url_for('contact_us'))
    else:
        user_online=None
        user_id = session.get('user_id')

        if user_id:  
                user_online = confirm_logs(user_id)

                if user_online is None:
                    session.clear() 
                    flash('You have been successfully logged out. Please log in again to continue.', 'info') 
                    return redirect(url_for('login')) 
        return render_template('user/contact.html',form=form,user_online=user_online)




@app.route('/handyman/faqs/')
def frequently_ask_questions():
    user_online=None
    user_id = session.get('user_id')

    if user_id:  
            user_online = confirm_logs(user_id)

            if user_online is None:
                session.clear() 
                flash('You have been successfully logged out. Please log in again to continue.', 'info') 
                return redirect(url_for('login'))
             
    return render_template('user/faq.html',user_online=user_online)



@app.route('/handyman/services/',methods=['GET'])
def services():
    user_online = None
    user_id = session.get('user_id')

    if user_id:  
            user_online = confirm_logs(user_id)

            if user_online is None:
                session.clear() 
                flash('You have been successfully logged out. Please log in again to continue.', 'info') 
                return redirect(url_for('login'))   
              
    services_match=[]
    input = request.args.get('search')

    if input:
        services=db.session.query(Handyservice).filter(Handyservice.handyservice_name.ilike(f'%{input}%')).all()
        if services:
            services_match=services
        else:
            flash('We presently do not have the service you are looking for on our services list. Kindly contact our  customer service','error')
            return redirect(url_for('services'))

    services=db.session.query(Handyservice).all()
    states=db.session.query(State).all()

    return render_template('user/services.html',user_online=user_online,
                           services=services,states=states,services_match=services_match)



@app.route('/handyman/reviews/',methods=['GET','POST'])
def reviews():
    user_online = None
    user_id = session.get('user_id')

    if user_id:  
            user_online = confirm_logs(user_id)

            if user_online is None:
                session.clear() 
                flash('You have been successfully logged out. Please log in again to continue.', 'info') 
                return redirect(url_for('login'))
            
    app_reviews = db.session.query(AppReview).filter(AppReview.app_review_status=='allowed').all()   
    return render_template('user/reviews.html',user_online=user_online,app_reviews = app_reviews)


@app.route('/handyman/submit/app/reviews/', methods=['POST'])
def submit_app_reviews():
    user_id=session.get('user_id')
    if user_id:
        app_rating=request.form.get('rating')
        app_comment=request.form.get('comment')

        if not all((app_rating, app_comment)): 
            flash('Please choose a rating from 1 to 5,and please add a comment', 'error')
            return redirect(url_for('reviews'))
        else:
            review=AppReview(
                    review_from_user_id =user_id,
                    app_review_rating=app_rating,
                    app_review_content=app_comment
                    )
            try:

                db.session.add(review)
                db.session.commit()
                flash('Your review has been submitted successfully!', 'success')
                return redirect(url_for('reviews'))
            
            except Exception as e:
                db.session.rollback()  
                flash('Something went wrong, please try again. Error: {}'.format(str(e)), 'error')
                return redirect(url_for('reviews'))
    else:
        flash('Please log in to make a review.', 'error')
        return redirect(url_for('login'))
   
  

@app.route('/handyman/click/services/get/proffessional/', methods=['GET', 'POST'])
def handyman_service_renderer():
    user_id = session.get('user_id')

    if user_id:
        user_online = confirm_logs(user_id)

        if user_online is None:
            session.clear()
            flash('You have been successfully logged out. Please log in again to continue.', 'info')
            return redirect(url_for('login'))

        else:
            selected_id = request.args.get('service')
            state_id = request.args.get('state')
            providers = []

            if selected_id:
                if not state_id or state_id == 'all':
                    providers = db.session.query(User).join(Userservice).filter(
                        User.user_status == 'active', User.user_deleted == 'false', Userservice.handyservice_id == selected_id
                    ).all()
                else:
                    providers = db.session.query(User).join(Userservice).filter(
                        User.user_status == 'active', User.user_deleted == 'false', Userservice.handyservice_id == selected_id,
                        User.user_state_id == state_id
                    ).all()

            no_providers = 'No service provider for the selected service yet' if not providers else None
            return render_template('user/handymanshow.html', user_online=user_online, providers=providers, no_providers=no_providers)
    else:    
        flash('You need to log in to access this page.', 'error')
        return redirect(url_for('login'))


@app.route('/handyman/professionals/review/', methods=['POST'])
def prof_review():
    user_id = session.get('user_id')

    if user_id:
        user_online = confirm_logs(user_id)

        if user_online is None:
            session.clear()
            flash('You have been successfully logged out. Please log in again to continue.', 'info')
            return redirect(url_for('login'))
        else:
            handyman_id=request.form.get('handyman-id')
            handyman_rating=request.form.get('rating')
            handyman_comment=request.form.get('comment')
            
            if not handyman_rating:  
                flash('Please choose a rating from 1 to 5, comments are optional', 'error')
                return redirect(f'/handyman/personalised/{handyman_id}/')
            else:
                comment = handyman_comment if handyman_comment else ''
                review=Review(
                    from_user_id=user_id,
                    to_user_id=handyman_id,
                    review_rating=handyman_rating,
                    review_content=comment
                    )
                
              
                user = db.session.query(User).filter(User.user_id == user_id).first()

                if user:
                    notification = Notification(
                        recipient_id=handyman_id,
                        reviewer_id=user_id,
                        message=f"You received a new review from {user.user_lastname} {user.user_firstname}.",
                        content=comment,
                        rating=handyman_rating,
                        is_read=False
                    )

                    try:
                        db.session.add(review)
                        db.session.add(notification)
                        db.session.commit()
                        flash('Your review has been submitted successfully!', 'success')
                        return redirect(f'/handyman/personalised/{handyman_id}/')
                    
                    except Exception as e:
                        db.session.rollback()
                        flash('Something went wrong, please try again. Error: {}'.format(str(e)), 'error')
                        return redirect(f'/handyman/personalised/{handyman_id}/')
                else:
                    flash('Error: User not found.', 'error')
                    return redirect(f'/handyman/personalised/{handyman_id}/')

    else:
        flash('You need to log in to access this page.', 'error')
        return redirect(url_for('login'))




@app.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
def mark_notification_as_read(notification_id):

    notification = Notification.query.get(notification_id)

    if notification and not notification.is_read:

        notification.is_read = True

        db.session.commit()
        return jsonify({'success': True, 'message': 'Notification marked as read.'})
    
    return jsonify({'success': False, 'message': 'Notification not found or already read.'})
    




@app.route('/notifications/delete/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id):
    notification = Notification.query.get(notification_id)
    
    if notification:
        try:
            db.session.delete(notification)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Notification deleted successfully.'})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Failed to delete notification: ' + str(e)})
    
    return jsonify({'success': False, 'message': 'Notification not found.'})





@app.route('/handyman/personalised/<int:id>/',methods=['GET','POST'])
def see_more(id):
    user_id = session.get('user_id')

    if user_id:
        user_online = confirm_logs(user_id)

        if user_online is None:
            session.clear()
            flash('You have been successfully logged out. Please log in again to continue.', 'info')
            return redirect(url_for('login'))
        
        else:
            handyman = db.session.query(User).join(Userservice).filter(User.user_id == id).first_or_404()
            services_provided = db.session.query(Userservice).filter(Userservice.user_id == id).all()

            reviews = db.session.query(Review).filter(Review.review_status != 'disabled',
            Review.to_user_id == id).order_by(Review.review_updated_on.desc()).limit(6).all()
            if handyman:
                return render_template('user/handy_personalized.html',user_online=user_online, reviews=reviews,handyman=handyman,services_provided=services_provided)
    else:
        flash('You need to log in to access this page.', 'error')
        return redirect(url_for('login'))




@app.route('/handyman/myprofile/')
def my_profile():
    user_id = session.get('user_id')

    if user_id:
        user_online = confirm_logs(user_id)

        if user_online is None:
            session.clear()
            flash('You have been successfully logged out. Please log in again to continue.', 'info')
            return redirect(url_for('login'))
        else:
            user_services = db.session.query(Userservice).filter_by(user_id=user_id).all()

            reviews=db.session.query(Review).filter(Review.review_status != 'disabled',
            Review.to_user_id==user_id).order_by(Review.review_updated_on.desc()).limit(6).all()
            return render_template('user/profile.html',user_online=user_online,user_services=user_services,reviews=reviews)
    else:
        flash('You need to login to access this page','error')
        return redirect(url_for('login'))



@app.route('/handyman/mydashboard/',methods=['POST','GET'])
def user_dashboard():
    user_online=None
    user_id = session.get('user_id')

    if user_id:  
        user_online = confirm_logs(user_id)

        if user_online is None:
            session.clear() 
            flash('You have been successfully logged out. Please log in again to continue.', 'info') 
            return redirect(url_for('login'))    
        else:
                unread_notifications = Notification.query.filter_by(recipient_id=user_id).order_by(Notification.created_at.desc()).all()

                three_days_ago = datetime.now() - timedelta(days=3)

           
                unread_count = Notification.query.filter_by(recipient_id=user_id).filter(Notification.created_at >= three_days_ago).count()

                
                
                return render_template('user/user_dashboard.html',user_online=user_online, unread_notifications=unread_notifications, unread_count=unread_count)
    else:
        flash('Login to see dashboard','error')
        return redirect(url_for('login'))
    





@app.route('/handyman/professional/handymen/', methods=['GET','POST'])
def handymanpage():
    user_id = session.get('user_id')

    if user_id:
        user_online = confirm_logs(user_id)

        if user_online is None:
            session.clear()
            flash('You have been successfully logged out. Please log in again to continue.', 'info')
            return redirect(url_for('login'))
        else:
            selected_state = request.args.get('state')
            handyman = request.args.get('search')

            if not selected_state or selected_state == 'all':
            
                if handyman:
                    providers = db.session.query(User).join(Userservice).join(Handyservice).filter(
                        User.user_status == 'active', User.user_deleted == 'false',
                        Handyservice.handyservice_name.ilike(f'%{handyman}%')
                    ).all()
                else:      
                    providers = db.session.query(User).join(Userservice).filter(
                        User.user_status == 'active', User.user_deleted == 'false'
                    ).all()
            else:
                selected_state = int(selected_state)

                if handyman:
                    providers = db.session.query(User).join(Userservice).join(Handyservice).filter(
                        User.user_status == 'active', User.user_deleted == 'false',
                        User.user_state_id == selected_state,
                        Handyservice.handyservice_name.ilike(f'%{handyman}%')
                    ).all()
                else:
                
                    providers = db.session.query(User).join(Userservice).filter(
                        User.user_status == 'active', User.user_deleted == 'false',
                        User.user_state_id == selected_state
                    ).all()
        states = db.session.query(State).all()
        no_providers_message = "We currently do not have service providers in this state." if not providers else None
        
        return render_template('user/handymenpage.html', user_online=user_online, providers=providers, states=states, no_providers_message=no_providers_message)
    else:
        flash('Login to see handyman page','error')
        return redirect(url_for('login'))

