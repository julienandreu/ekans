from flask import Flask
from middlewares.request_id import with_request_id

app = Flask(__name__)

app.wsgi_app = with_request_id(app.wsgi_app)

import routes.root