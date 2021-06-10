import os,base64,requests
from os import getenv as _
from urllib.parse import urlparse
import time, json, binascii
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from middleware import same_version, auth_required
from utils import readkey, writekey, listfile, readfile, writefile, validjson,is_base64_code
from flask import (Flask, Response, abort, request, jsonify,
                    make_response, render_template, send_from_directory, redirect)

load_dotenv()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 << 20

@app.route('/')
def hello():
  return 'Hello, World!'

@app.route('/favicon.ico')
def favicon():
  return abort(404)

@app.route('/key', methods=['POST'])
@auth_required
@same_version
def key():
  iv  = request.form.get('iv')
  key = request.form.get('key')

  if len(iv) != 32 or len(key) != 32:
    return jsonify({'err': 1, 'message': 'Invalid key or iv'})

  return jsonify({'err': 0, 'data': writekey(key, iv)})

@app.route('/play/<key>')
def play(key):
  real = os.path.splitext(key)[0]

  try:
    if key[-4:] == '.key':
      meta = readkey(real)
      r = Response(binascii.unhexlify(meta['key']), mimetype='application/octet-stream')
      r.headers.add('Access-Control-Allow-Origin', '*')
      return r

    meta = readfile(real)
    if key[-5:] == '.m3u8':
      r = Response(meta['raw'], mimetype='application/vnd.apple.mpegurl')
      r.headers.add('Access-Control-Allow-Origin', '*')
      return r

    return render_template('play.html', meta=meta)
  except:
    return jsonify({'err': 1, 'message': 'File does not exist'})

@app.route('/videos/<skip>', methods=['GET'])
@auth_required
@same_version
def videos(skip):
  try:
    skip = (int(skip) - 1) * 50
  except:
    skip = 0
  return jsonify({'err': 0, 'data': listfile(skip)})

@app.route('/upload', methods=['POST'])
@auth_required
@same_version
def upload():
  if not _('ENABLE_UPLOAD') == 'YES':
    return jsonify({'err': 1, 'message': 'Upload is not enabled'})

  if 'file' not in request.files:
    return jsonify({'err': 1, 'message': 'No file part'})

  file = request.files['file']
  if not file or file.filename == '':
    return jsonify({'err': 1, 'message': 'No selected file'})

  name = secure_filename(file.filename)
  path = os.path.join('uploads',time.strftime("%Y%m%d", time.localtime()))
  if not os.path.exists(path):
    os.mkdir(path)
  file.save(os.path.join(path, name))
  return jsonify({'err': 0, 'data': os.path.join(path, name)})

@app.route('/publish', methods=['POST'])
@auth_required
@same_version
def publish():
  code = request.form.get('code')
  params = request.form.get('params')
  if not code:
    return jsonify({'err': 1, 'message': 'Code cannot be empty'})
  elif len(code) > 500*1024:
    return jsonify({'err': 1, 'message': 'Code size cannot exceed 500K'})
  elif not validjson(params):
    return jsonify({'err': 1, 'message': 'Invalid params'})

  key = writefile(code, params, request.form.get('title'))
  return jsonify({'err': 0, 'data': key})

@app.route('/assets/<path:path>')
def send_js(path):
  return send_from_directory('assets', path)

@app.route('/uploads/<path:path>')
def send_file(path):
  r = make_response(send_from_directory('uploads', path))
  r.headers.add('Access-Control-Allow-Origin', '*')
  return r

@app.route('/r/<path:path>')
def make_redirect(path):
  if(is_base64_code(path)):
    url = base64.b64decode(path)
  else:
    url = path
  r = redirect(url)
  r.headers.add('Access-Control-Allow-Origin', '*')
  return r

@app.route('/p/<path:path>')
def make_proxy(path):
  if len(path) == 0:
    return abort(404)
  if(is_base64_code(path)):
    url = str(base64.b64decode(path), 'UTF8')
  else:
    url = path
  parsed_result = urlparse(url)
  scheme = {'http','https'}
  if parsed_result.scheme.lower() not in scheme:
    return abort(404)
  netloc = parsed_result.netloc
  proxyUrl = {'inews.gtimg.com'}
  if len(netloc) == 0:
    return abort(404)
  if netloc in proxyUrl:
    r = Response(requests.get(url).content, mimetype="image/png")
  else:
    r = redirect(url)
  r.headers.add('Access-Control-Allow-Origin', '*')
  return r

if __name__ == '__main__':
  app.run(host='0.0.0.0', port='3395', debug=True)
