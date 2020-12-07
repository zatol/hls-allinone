from os import getenv as _
from utils import api, md5, upload_wrapper

class Uploader:
  MAX_BYTES = 20 << 20

  @classmethod
  def params(cls):
    return {'padding': 0}

  @classmethod
  @upload_wrapper
  def handle(cls, file):
    file = file.read()
    r = api('POST', 'upload', files={
      'file': ('%s.png' % md5(file), file, 'image/png')
    })

    if not r:
      return None

    return '%s/%s' % (_('APIURL'), r)
