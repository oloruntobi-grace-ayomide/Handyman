from flask_wtf import FlaskForm
from wtforms import FileField,StringField,PasswordField,SearchField,SubmitField,BooleanField,RadioField,SelectField,TextAreaField,IntegerField
from wtforms.validators import DataRequired,EqualTo,Length,Email,NumberRange

class SignupForm(FlaskForm):
   
    firstname=StringField('Firstname',validators=[DataRequired(message='* Firstname field is required')])
    lastname=StringField('Lastname',validators=[DataRequired(message='* Lastname field is required')])
    phone_no=StringField('Phone_no',validators=[DataRequired(message='* Phone-no field is required')])
    email=StringField('Email',validators=[DataRequired(message='* Email field is required'),Email(message='Invalid email address')])
    username=StringField('Username',validators=[DataRequired(message='* Username field is required'),Length(max=12)])
    password=PasswordField('Password',validators=[DataRequired(message='* Password field is required'),Length(max=30)])
    confirmpassword=PasswordField('Confirm Password',validators=[DataRequired(message='* Confirm Password field is required'),Length(max=30)])
    address=StringField('Address',validators=[DataRequired(message='* Address field is required')])
    agreement=BooleanField(validators=[DataRequired(message='* Accept terms and conditions')])
    submit=SubmitField('Sign Up')

class UpdateForm(FlaskForm):
    password=PasswordField('Password',validators=[DataRequired(message='* Password field is required'),Length(max=30)])
    confirmpassword=PasswordField('Confirm Password',validators=[DataRequired(message='* Confirm Password field is required'),Length(max=30)])
    submit=SubmitField('Change Password')


class SetForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(message='* Username field is required'),Length(max=12)])
    password=PasswordField('Password',validators=[DataRequired(message='* Password field is required'),Length(max=30)])
    confirmpassword=PasswordField('Confirm Password',validators=[DataRequired(message='* Confirm Password field is required'),Length(max=30)])
    submit=SubmitField('Submit')


class LoginForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(message='* This field is required'),Length(max=12)])
    password=PasswordField('Password',validators=[DataRequired(message='* This field is required'),Length(max=30)])
    submit=SubmitField('Login')

class ContactForm(FlaskForm):
    customername=StringField('Name',validators=[DataRequired(message='* Name field is required')])
    customerphone=StringField('Phone_no',validators=[DataRequired(message='* Phone field is required')])
    customeremail=StringField('Email',validators=[DataRequired(message='* Email field is required'),Email(message='Invalid email address')])
    customermessage=TextAreaField('message',validators=[DataRequired(message='*Please we would like to know why you are contacting us')])
    besttime=SelectField('Best time to call:',choices=[('besttime','Please Select'),('morning','Morning'),('afternoon','Afternoon'),('evening','Evening')],validators=[DataRequired(message='* Pls select the best time to call')])
    submit=SubmitField('Send')


class SearchForm(FlaskForm):
    search=SearchField('Search',validators=[DataRequired()])
    submit=SubmitField('Search')

class NewsletterForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(message='* This field is required'),Email(message='Invalid email address')])
    submit=SubmitField('Subscribe')

class ProfileForm(FlaskForm):
   
    firstname=StringField('Firstname',validators=[DataRequired(message='* Firstname field is required')])
    lastname=StringField('Lastname',validators=[DataRequired(message='* Lastname field is required')])
    phone_no=StringField('Phone_no',validators=[DataRequired(message='* Phone-no field is required')])
    email=StringField('Email',validators=[DataRequired(message='* Email field is required'),Email(message='Invalid email address')])
    address=StringField('Address',validators=[DataRequired(message='* Address field is required')])
    businessname=StringField('Businessname',validators=[DataRequired(message='* businessname field is required')])
    biography=TextAreaField('biography',validators=[DataRequired(message='* This field is required')])
    dp=FileField('dp',validators=[DataRequired(message='* This field is required')])
    services=BooleanField('services')
    submit=SubmitField('Update')

class AdminSignupForm(FlaskForm):
    fullname=StringField('Fullname',validators=[DataRequired(message='* Firstname field is required')])
    username=StringField('Username',validators=[DataRequired(message='* This field is required')])
    phone_no=StringField('Phone_no',validators=[DataRequired(message='* Phone-no field is required')])
    email=StringField('Email',validators=[DataRequired(message='* Email field is required'),Email(message='Invalid email address')])
    password=PasswordField('Password',validators=[DataRequired(message='* This field is required')])
    submit=SubmitField('Admin Login')

class AdminForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(message='* This field is required')])
    email=StringField('Email',validators=[DataRequired(message='* Email field is required'),Email(message='Invalid email address')])
    password=PasswordField('Password',validators=[DataRequired(message='* This field is required')])
    submit=SubmitField('Admin Login')


class ServiceForm(FlaskForm):
    service_name=StringField('Service Name',validators=[DataRequired(message='* This field is required')])
    description=TextAreaField('Service Description',validators=[DataRequired(message='* This field is required')])
    service_icon_alt=StringField('Icon alt',validators=[DataRequired(message='* Email field is required')])
    submit=SubmitField('Add')
   
