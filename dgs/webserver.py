'''
Created on 2020-02-13

@author: wf
'''
from flask import Flask
from flask import render_template
from flask import request
from dgs.diagrams import Generators,Generator,Example
import os
from flask.helpers import send_from_directory

debug=True
port=5003
host='0.0.0.0'
scriptdir=os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,static_url_path='',static_folder=scriptdir+'/../web', template_folder=scriptdir+'/../templates')

@app.route('/')
def home():
    return index()
    
def index(err=None,gen='dot',source="",message="",genResult=None):    
    """ render index page with the given parameters"""
    return render_template('index.html',gen=gen,gens=Generators.generators(),err=err, message=message, source=source,genResult=genResult)

@app.route('/example/<generator>')
def example(generator):
    """ get the given example generator """
    txt=Example.get(generator)
    return txt

@app.route('/check/<generator>')
def check(generator):
    gen=Generators.get(generator)
    if gen is not None:
        return gen.getHtmlInfo()
    else:
        return "%s is not a valid generator" % generator
    
@app.route('/render/<outputType>/<crc32>')
def render(outputType,crc32):
    outputDirectory=Generator.getOutputDirectory()    
    filename="%s.%s" % (crc32,outputType)
    return send_from_directory(outputDirectory,filename)

@app.route('/diagrams', methods=['GET', 'POST']) #allow both GET and POST requests
def form_example():
    err=None
    genResult=None
    message=""
    if request.method == 'POST':
        try:
            source = request.form.get('source')
            alias=request.form.get('generator')
            generatorId=Generators.generatorIdForAlias(alias)
            outputType=request.form.get(generatorId+'-output')
            gen=Generators.get(generatorId)
            if gen is None:
                raise Exception("invalid generator %s",generatorId)
            genResult=gen.generate(alias,source,outputType,useCached=True)
            if not genResult.isValid():
                raise Exception("could not generate %s for %s",outputType,generatorId)
        except Exception as ex:
            err=ex
    return index(err=err, message=message,source=source,gen=gen,genResult=genResult)

if __name__ == '__main__':
    app.run(debug=debug,port=port,host=host)   
