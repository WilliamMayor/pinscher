from flask import Blueprint
from flask import render_template

website = Blueprint('website', __name__)


@website.route('/')
def index():
    return render_template('index.html')
