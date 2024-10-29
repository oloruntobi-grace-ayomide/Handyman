from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail
from handyman.models import db

csrf=CSRFProtect()
migrate=Migrate()
mail=Mail()

def create_app():
    app=Flask(__name__,instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=True)


    csrf.init_app(app)
    migrate.init_app(app,db)
    db.init_app(app)
    mail.init_app(app)

    return app

app=create_app()



from handyman import user_route,admin_route,error_route,authentications_route
from handyman import form


class Meta():
    csrf=True
    csrf_time_limit=7200