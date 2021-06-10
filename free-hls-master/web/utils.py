import os
import json, time
import base64, hashlib

def md5(s):
  md5 = hashlib.md5(s.encode('utf-8')).hexdigest()
  return md5[8:24]

def readkey(id):
  return json.load(open('keys/%s' % id, 'r'))

def writekey(key, iv):
  id = md5(key + iv)

  with open('keys/%s' % id, 'w') as f:
    f.write(json.dumps({
      'iv': iv,
      'key': key,
      'created_at': int(time.time())
    }))

  return id

def listfile(skip=0):
  i, entities = 0, []

  try:
    with open('userdata/index') as f:
      for _ in range(skip):
        next(f)

      for line in f:
        if i >= 50:
          break

        i += 1
        entities.append(json.loads(line))
  except: pass
  return entities

def readfile(key):
  return json.load(open('userdata/%s' % key, 'r'))

def writefile(code, params, title=None):
  key  = md5(code)
  meta = {
    'key': key,
    'file': 'userdata/%s' % key,
    'title': title or 'untitled',
    'params': params or '{}',
    'created_at': int(time.time())
  }

  if not os.path.isfile(meta['file']):
    with open('userdata/index', 'a') as f:
      f.write(json.dumps(meta) + '\n')

  with open(meta['file'], 'w') as f:
    meta['raw'] = code
    meta['code'] = base64.b64encode(code.encode('utf-8')).decode('ascii')
    f.write(json.dumps(meta))

  return key

def validjson(s):
  try:
    json.loads(s)
    return True
  except:
    return False

def is_base64_code(s):
  _base64_code = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                  'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                  'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a',
                  'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                  'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                  't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1',
                  '2', '3', '4', '5', '6', '7', '8', '9', '+',
                  '/', '=']
  # Check base64 OR codeCheck % 4
  code_fail = [i for i in s if i not in _base64_code]
  if code_fail or len(s) % 4 != 0:
    return False
  return True