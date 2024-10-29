from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_firstname = db.Column(db.String(30),nullable=False)
    user_lastname = db.Column(db.String(30),nullable=False)
    user_phone = db.Column(db.String(15),nullable=False)
    user_email = db.Column(db.String(50),nullable=False,unique=True)
    user_username = db.Column(db.String(20),nullable=False,unique=True)
    user_password = db.Column(db.String(255),nullable=False)
    user_address = db.Column(db.String(100),nullable=False)
    user_status = db.Column(db.Enum('active','disabled'),nullable=False, server_default=("active"))
    user_state_id = db.Column(db.Integer,db.ForeignKey('state.state_id'))
    user_lga_id = db.Column(db.Integer,db.ForeignKey('lga.lga_id'))
    user_bio = db.Column(db.Text,nullable=True)
    user_business_name = db.Column(db.String(70),nullable=True)
    user_dp = db.Column(db.String(100), nullable=True)
    user_date_joined = db.Column(db.DateTime,default=datetime.utcnow)
    user_deleted = db.Column(db.Enum('true','false'),nullable=False, server_default=("false"))
    # set relationship
    state=db.relationship('State',backref='user')
    lga=db.relationship('Lga',backref='user')
    
    def __repr__(self):
        return "<{}:{}:{}>".format(self.user_firstname,self.user_lastname,self.user_email)
    

class State(db.Model):
    __tablename__ = 'state'
    state_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    state_name = db.Column(db.String(30),nullable=False,unique=True)

    def __repr__(self):
        return "<{}:{}>".format(self.state_id,self.state_name)
    

class Lga(db.Model):
    __tablename__ = 'lga'
    lga_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    lga_name = db.Column(db.String(70),nullable=False)
    lga_state_id = db.Column(db.Integer,db.ForeignKey('state.state_id'))
    # set relationship
    state=db.relationship('State',backref='lgas') 



class Handyservice(db.Model):
    __tablename__ = 'handyservice'
    handyservice_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    handyservice_name = db.Column(db.String(50),nullable=False,unique=True)
    handyservice_description = db.Column(db.String(250),nullable=False)
    handyservice_picture = db.Column(db.String(150),nullable=True)
    handyservice_icon = db.Column(db.String(150),nullable=False)
    handyservice_icon_alt=db.Column(db.String(30),nullable=False)
    handydate_added = db.Column(db.DateTime,default=datetime.utcnow, nullable=False)


class Userservice(db.Model):
    __tablename__ = 'userservice'
    userservice = db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'))
    handyservice_id = db.Column(db.Integer,db.ForeignKey('handyservice.handyservice_id'))


    handy_service = db.relationship('Handyservice',backref='user_service')
    user = db.relationship('User',backref='user_service')



class Review(db.Model):
    __tablename__ = 'review'
    review_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    review_status = db.Column(db.Enum('allowed','disabled'),nullable=False,server_default=('allowed'))
    review_rating = db.Column(db.Integer,nullable=False,)
    review_content = db.Column(db.Text,nullable=True)    
    from_user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    to_user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    review_date = db.Column(db.DateTime,default=datetime.utcnow)
    review_updated_on = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    #set relationship
    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='reviews_given')
    to_user = db.relationship('User', foreign_keys=[to_user_id], backref='reviews_received')

    def __repr__(self):
        return "<{}:{}:{}:{}:{}>".format(self.review_rating,self.review_status,self.review_content,self.review_date,self.from_user_id,self.to_user_id)



class AppReview(db.Model):
    __tablename__ = 'appreview'
    app_review_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    app_review_status = db.Column(db.Enum('allowed','disabled'),nullable=False,server_default=('allowed'))
    app_review_rating = db.Column(db.Integer,nullable=True,)
    app_review_content = db.Column(db.Text,nullable=False)    
    review_from_user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    review_date = db.Column(db.DateTime,default=datetime.utcnow)
    review_updated_on = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    #set relationship
    app_from_user = db.relationship('User', foreign_keys=[review_from_user_id], backref='review_given')
   


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False) 
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer,nullable=False,)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
 
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_notifications')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='sent_notifications')

    def __repr__(self):
        return "<{}:{}:{}:{}>".format(self.id, self.recipient_id ,self.reviewer_id,self.is_read)
        





class Newlettersubscriber(db.Model):
    __tablename__='newlettersubscriber'
    subscriber_id = db.Column(db.Integer,primary_key=True,autoincrement=True)  
    subscriber_email = db.Column(db.String(50),nullable=False,unique=True)
    subscriber_status = db.Column(db.Enum('active', 'disabled'), nullable=False, server_default='active')




class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    admin_fullname=db.Column(db.String(30),nullable=False)
    admin_phone = db.Column(db.String(15),nullable=False)
    admin_email = db.Column(db.String(50),nullable=False,unique=True)
    admin_username = db.Column(db.String(20),nullable=False,unique=True)
    admin_password = db.Column(db.String(200),nullable=False)
    admin_date_joined = db.Column(db.DateTime,default=datetime.utcnow)
    admin_last_logged_in = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)







