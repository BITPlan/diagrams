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
import argparse
import sys
from pydevd_file_utils import setup_client_server_paths

scriptdir=os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,static_url_path='',static_folder=scriptdir+'/../web', template_folder=scriptdir+'/../templates')

@app.route('/')
def home():
    return index()
    
def index(err=None,gen='dot',outputType='png',source="",message="",genResult=None):    
    """ render index page with the given parameters"""
    return render_template('index.html',outputType=outputType,gen=gen,gens=Generators.generators(),err=err, message=message, source=source,genResult=genResult)

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
    
@app.route('/render/<outputType>/<crc32>', methods=['GET'])
def render(outputType,crc32):
    # allow extension ending for direct rendering e.g. in wikis
    ext="."+outputType
    if crc32.endswith(ext):
        crc32=crc32[:-len(ext)]
    outputDirectory=Generator.getOutputDirectory()    
    filename="%s.%s" % (crc32,outputType)
    return send_from_directory(outputDirectory,filename)

def getParam(name):
    value=request.form.get(name)
    if value is None:
        value=request.args.get(name)
    return value

@app.route('/render', methods=['POST'])
def renderForWikiExtension():
    """ endpoint for diagrams extension"""
    generator=getParam('generator')
    source=getParam('source')
    targetFormat=getParam('types')
    if targetFormat is None or targetFormat=="None":
        targetFormat="png"
    gen=Generators.get(generator)
    # use for DOS attack prevention
    ip=request.remote_addr
    result=gen.generate('dot',source,targetFormat)
    # force SSL
    json=result.asJson(request.base_url.replace('http:','https:'))
    return json
    
@app.route('/diagrams', methods=['GET', 'POST']) #allow both GET and POST requests
def form_example():
    err=None
    genResult=None
    message=""
    source=None
    gen=None
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
    return index(err=err, message=message,source=source,gen=alias,outputType=outputType,genResult=genResult)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Diagrams rendering webservice")
    parser.add_argument('--debug',
                                 action='store_true',
                                 help="run in debug mode")
    parser.add_argument('--port',
                                 type=int,
                                 default=5003,
                                 help="the port to use")
    parser.add_argument('--host',
                                 default="0.0.0.0",
                                 help="the host to serve for")
    parser.add_argument('--debugServer',
                                 help="remote debug Server")
    parser.add_argument('--debugPort',type=int,
                                 help="remote debug Port",default=5678)
    parser.add_argument('--debugPathMapping',nargs='+',help="remote debug Server path mapping - needs two arguments 1st: remotePath 2nd: local Path")

    args=parser.parse_args(sys.argv[1:])
    if args.debugServer:
        import pydevd
        print (args.debugPathMapping,flush=True)
        if args.debugPathMapping:
            if len(args.debugPathMapping)==2:
                remotePath=args.debugPathMapping[0] # path on the remote debugger side
                localPath=args.debugPathMapping[1]  # path on the local machine where the code runs
                MY_PATHS_FROM_ECLIPSE_TO_PYTHON = [
                    (remotePath, localPath),
                ]
                setup_client_server_paths(MY_PATHS_FROM_ECLIPSE_TO_PYTHON)
                #os.environ["PATHS_FROM_ECLIPSE_TO_PYTHON"]='[["%s", "%s"]]' % (remotePath,localPath)
                #print("trying to debug with PATHS_FROM_ECLIPSE_TO_PYTHON=%s" % os.environ["PATHS_FROM_ECLIPSE_TO_PYTHON"]);
     
        pydevd.settrace(args.debugServer, port=args.debugPort,stdoutToServer=True, stderrToServer=True)

    app.run(debug=args.debug,port=args.port,host=args.host)   
