import os
from clinic_connect import create_app

# Instantiate the modular Flask application package
app = create_app()

if __name__ == '__main__':
    # Start the local development server
    # Running debug mode conditionally based on FLASK_ENV
    is_debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(debug=is_debug, host='127.0.0.1', port=5000)