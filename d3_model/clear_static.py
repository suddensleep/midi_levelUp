import os

for f in os.listdir('/home/john_gilling/eb_flask_app/static/'):
    os.remove('/home/john_gilling/eb_flask_app/static/' + f)
