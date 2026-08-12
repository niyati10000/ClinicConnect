import os
import sys

# Ensure root project path is in sys.path
basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from clinic_connect import create_app

# Expose WSGI application callable
application = create_app()
app = application

if __name__ == "__main__":
    is_debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(debug=is_debug, host='127.0.0.1', port=5000)
