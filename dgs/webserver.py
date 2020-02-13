'''
Created on 13 Feb 2020

@author: wf
'''
from flask import Flask
from flask import render_template
from flask import request
from dgs.diagrams import Generators, Example
import os

debug=True
port=5003
host='0.0.0.0'
scriptdir=os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,static_url_path='',static_folder=scriptdir+'/../web', template_folder=scriptdir+'/../templates')

@app.route('/')
def home():
    return index()
    
def index(err=None,gen='dot',source="",message=""):    
    return render_template('index.html',gen=gen,gens=Generators.generators(),err=err, message=message, source=source)

@app.route('/example/<generator>')
def example(generator):
    txt=Example.get(generator)
    return txt

@app.route('/diagrams', methods=['GET', 'POST']) #allow both GET and POST requests
def form_example():
    err=None
    message=""
    if request.method == 'POST':
        try:
            source = request.form.get('source')
            gen=request.form.get('generator')
        except Exception as ex:
            err=ex
    return index(err=err, message=message,source=source,gen=gen)

if __name__ == '__main__':
    app.run(debug=debug,port=port,host=host)   
