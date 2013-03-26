from flask import Flask
from api import api
from website import website

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(website)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
