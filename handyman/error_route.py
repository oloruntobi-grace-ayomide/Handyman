from flask import Flask,render_template,session
from handyman import app
from flask_wtf.csrf import CSRFError
# from handyman.models import User,db



@app.errorhandler(404)
def error404(error):
    return render_template('error/error404.html', error=error), 404

@app.errorhandler(500)
def error500(error):
    return render_template('error/error500.html', error=error), 500

@app.errorhandler(503)
def error503(error):
    return render_template('error/error503.html', error=error), 503

@app.errorhandler(401)
def error401(error):
    return render_template('error/error401.html', error=error), 401

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('error/error400.html', reason=e.description), 400

@app.errorhandler(403)
def error403(error):
    return render_template('error/error403.html', error=error), 403

@app.errorhandler(429)
def error429(error):
    return render_template('error/error429.html', error=error), 429


# @app.errorhandler(404)
# def error404(error):
#     allowed=db.session.query(User).filter(User.user_status=='active').all()
#     if allowed:
#         if session.get('user_id')!=None:
#             user_id=session.get('user_id')
#             user_online=db.session.query(User).get(user_id)   
#         else:
#             user_online=None
#     return render_template('error/error404.html',error=error,user_online=user_online),404

# @app.errorhandler(500)
# def error500(error):
#     allowed=db.session.query(User).filter(User.user_status=='active').all()
#     if allowed:
#         if session.get('user_id')!=None:
#             user_id=session.get('user_id')
#             user_online=db.session.query(User).get(user_id)   
#         else:
#             user_online=None
#     return render_template('error/error500.html',error=error,user_online=user_online),500


# @app.errorhandler(503)
# def error503(error):
#     allowed=db.session.query(User).filter(User.user_status=='active').all()
#     if allowed:
#         if session.get('user_id')!=None:
#             user_id=session.get('user_id')
#             user_online=db.session.query(User).get(user_id)   
#         else:
#             user_online=None
#     return render_template('error/error503.html',error=error,user_online=user_online),503

# @app.errorhandler(401)
# def error401(error):
#     allowed=db.session.query(User).filter(User.user_status=='active').all()
#     if allowed:
#         if session.get('user_id')!=None:
#             user_id=session.get('user_id')
#             user_online=db.session.query(User).get(user_id)   
#         else:
#             user_online=None
#     return render_template('error/error401.html',error=error,user_online=user_online),401

# @app.errorhandler(CSRFError)
# def handle_csrf_error(e):
#     allowed=db.session.query(User).filter(User.user_status=='active').all()
#     if allowed:
#         if session.get('user_id')!=None:
#             user_id=session.get('user_id')
#             user_online=db.session.query(User).get(user_id)   
#         else:
#             user_online=None
#     return render_template('error400.html',reason=e.description,user_online=user_online),400

# @app.errorhandler(403)
# def error403(error):
#     allowed=db.session.query(User).filter(User.user_status=='active').all()
#     if allowed:
#         if session.get('user_id')!=None:
#             user_id=session.get('user_id')
#             user_online=db.session.query(User).get(user_id)   
#         else:
#             user_online=None
#     return render_template('error/error403.html',error=error,user_online=user_online),403


# @app.errorhandler(429)
# def error429(error):
#     allowed=db.session.query(User).filter(User.user_status=='active').all()
#     if allowed:
#         if session.get('user_id')!=None:
#             user_id=session.get('user_id')
#             user_online=db.session.query(User).get(user_id)   
#         else:
#             user_online=None
#     return render_template('error/error429.html',error=error,user_online=user_online),429


