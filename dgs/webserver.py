'''
Created on 13 Feb 2020

@author: wf
'''
from flask import Flask
from flask import render_template
from flask import request
from dgs.diagrams import Generators, Example

debug=True
port=5003
host='0.0.0.0'
app = Flask(__name__,static_url_path='',static_folder='../web', template_folder='../templates')

@app.route('/')
def home():
    return index()
    
def index(err=None):    
    return render_template('index.html',gens=Generators.generators(),err=err)

@app.route('/example/<generator>')
def example(generator):
    txt=Example.get(generator)
    return txt

@app.route('/diagrams', methods=['GET', 'POST']) #allow both GET and POST requests
def form_example():
    err=None
    if request.method == 'POST':
        try:
            source = request.form.get('source')
        except Exception as ex:
            err=ex
    return index(err=err)

if __name__ == '__main__':
    app.run(debug=debug,port=port,host=host)   