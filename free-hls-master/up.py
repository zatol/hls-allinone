import os, re, json,base64,zlib,math,time
from sys import argv
from os import getenv as _
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageDraw, ImageFont
from utils import api, md5, exec, execstr, tsfiles,pngfiles, safename, uploader, sameparams
import cv2
from LSBSteg import LSBSteg
# from lsb import embed
load_dotenv()
argv += [''] * 3

def checker(code):
  flag  = False
  limit = uploader().MAX_BYTES

  for file in pngfiles(code):
    if os.path.getsize(file) >= limit:
      flag = True
      print('File too large: tmp/%s' % file)

  return exit(1) if flag else code

def read_bytes(file):
  return open(file, mode='rb').read();


def draw_image(new_img, text, show_image=False):
  text = str(text)
  draw = ImageDraw.Draw(new_img)
  img_size = new_img.size
  draw.line((0, 0) + img_size, fill=128)
  draw.line((0, img_size[1], img_size[0], 0), fill=128)

  font_size = 40
  fnt = ImageFont.truetype('arial.ttf', font_size)
  fnt_size = fnt.getsize(text)
  while fnt_size[0] > img_size[0] or fnt_size[0] > img_size[0]:
    font_size -= 5
    fnt = ImageFont.truetype('arial.ttf', font_size)
    fnt_size = fnt.getsize(text)

  x = (img_size[0] - fnt_size[0]) / 2
  y = (img_size[1] - fnt_size[1]) / 2
  draw.text((x, y), text, font=fnt, fill=(255, 0, 0))

  if show_image:
    new_img.show()
  del draw


def new_image(width, height, text='default', color=(100, 100, 100, 255), show_image=False):
  new_img = Image.new('RGBA', (int(width), int(height)), color)
  draw_image(new_img, text, show_image)
  new_img_file_name = r'%s_%s_%s.png' % (width, height, text)
  new_img.save(new_img_file_name)
  return new_img_file_name
  del new_img


def encrypt(code):
  if _('ENCRYPTION_VERSION') == 'V1':
    print('ENCRYPTION_VERSION:%s' % _('ENCRYPTION_VERSION'))
    head = read_bytes('../dangdai-32x32.png')
    head1 = head[0:-12]
    head2 = head[-12:]
    tmpdir = os.getcwd()+'/tmp'
    if not os.path.exists(tmpdir):
      os.mkdir(tmpdir)
    os.chdir(tmpdir)
    for file in tsfiles(code):
      portion = os.path.splitext(file)
      if portion[1] == ".ts":
        newName = portion[0] + ".png"
        if os.path.isfile(newName):
          code = code.replace(file, newName)
          continue
        segment = read_bytes('../' + file)
        segment = zlib.compress(segment)
        done_segments = head1 + segment + head2
        open(newName, 'wb').write(done_segments)
        code = code.replace(file, newName)
      #break
    #os.chdir('../')

  if _('ENCRYPTION_VERSION') == 'V2':
    print('ENCRYPTION_VERSION:%s' % _('ENCRYPTION_VERSION'))
    tmpdir = os.getcwd()+'/tmp'
    if not os.path.exists(tmpdir):
      os.mkdir(tmpdir)
    os.chdir(tmpdir)

    for file in tsfiles(code):
      # 1，获取切片大小
      filesize = os.path.getsize('../' +file)+64
      wh=math.ceil(math.sqrt(filesize/3))*4
      # wh=math.ceil(math.sqrt(filesize*3))
      print('切片大小:%s，图片尺寸:%s' % (filesize,wh))
      data = open('../' + file, "rb").read()
      data = zlib.compress(data)
      print('压缩后切片大小:%s' % (len(data)))

      portion = os.path.splitext(file)
      newName = portion[0] + ".png"

      if os.path.isfile(newName):
        code = code.replace(file, newName)
        continue
      # 2，生成图片
      new_img_file_name = new_image(wh, wh, portion[0], show_image=False)
      print('生成图片:%s' % (new_img_file_name))

      # 3，隐写
      in_img = cv2.imread(new_img_file_name)
      steg = LSBSteg(in_img)
      starttime = time.time()
      res = steg.encode_binary(data)
      duration = time.time()-starttime
      print('隐写完成时间:%s' % (duration))
      cv2.imwrite(newName, res)
      print('隐写完成:%s' % (newName))

      # embed(new_img_file_name, '../' + file)
      # 4，替换
      code = code.replace(file, newName)

      """
      # 1，获取切片大小
      filesize = os.path.getsize('../' + file) + 64
      wh = math.ceil(math.sqrt(filesize / 3))
      print('切片大小:%s，图片尺寸:%s' % (filesize, wh))
      data = open('../' + file, "rb").read()
      new_img_file_name = r'%s_%s_%s.png' % (wh, wh, md5(data))
      if os.path.isfile('out' + new_img_file_name):
        code = code.replace(file, 'out' + new_img_file_name)
        continue
      # 2，生成图片
      new_image(wh, wh, md5(data), show_image=False)
      print('生成图片:%s' % (new_img_file_name))

      # 3，隐写
      in_img = cv2.imread(new_img_file_name)
      steg = LSBSteg(in_img)
      starttime = time.time()
      res = steg.encode_binary(data)
      duration = time.time() - starttime
      print('隐写完成时间:%s' % (duration))
      cv2.imwrite('out' + new_img_file_name, res)
      print('隐写完成:%s' % ('out' + new_img_file_name))
      # embed(new_img_file_name, '../' + file)
      # 4，替换
      code = code.replace(file, 'out' + new_img_file_name)
      
      """


  if not _('ENCRYPTION') == 'YES':
    return code

  for file in tsfiles(code):
    if file.startswith('enc.'):
      continue

    print('Encrypting %s to enc.%s ... ' % (file, file), end='')
    key = exec(['openssl','rand','16']).hex()
    iv  = execstr(['openssl','rand','-hex','16'])
    exec(['openssl','aes-128-cbc','-e','-in',file,'-out','enc.%s' % file,'-p','-nosalt','-iv',iv,'-K',key])

    key_id = api('POST', 'key', data={'iv': iv, 'key': key})
    if not key_id:
      print('failed')
      open('out.m3u8', 'w').write(code)
      exit()

    print('done')
    code = re.sub('(#EXTINF:.+$[\\r\\n]+^%s$)' % file, '#EXT-X-KEY:METHOD=AES-128,URI="%s/play/%s.key",IV=0x%s\n\\1' % (_('APIURL'), key_id, iv), code, 1, re.M)
    code = code.replace(file, 'enc.%s' % file)

  open('out.m3u8', 'w').write(code)
  return code

def publish(code, title=None):
  if _('NOSERVER') == 'YES':
    return print('The m3u8 file has been dumped to tmp/out.m3u8')

  r = api('POST', 'publish', data={'code': code, 'title': title,
                                   'params': json.dumps(uploader().params())})
  if r:
    url = '%s/play/%s' % (_('APIURL'), r)
    print('This video has been published to: %s' % url)
    print('You can also download it directly: %s.m3u8' % url)

def bit_rate(file):
  return int(execstr(['ffprobe','-v','error','-show_entries','format=bit_rate','-of','default=noprint_wrappers=1:nokey=1',file]))

def video_codec(file):
  codecs = execstr(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name','-of','default=noprint_wrappers=1:nokey=1',file])
  return 'h264' if set(codecs.split('\n')).difference({'h264'}) else 'copy'

def command_generator(file):

  sub          = ''
  rate         = bit_rate(file)
  vcodec       = video_codec(file)
  max_bits     = uploader().MAX_BYTES * 8
  segment_time = min(10, int(max_bits / (rate * 1.35)))


  #LIMITED
  if rate > 6e6 or argv[3] == 'LIMITED':
    maxrate = max_bits / 20 / 2.5
    sub    += ' -b:v %d -maxrate %d -bufsize %d' % (min(rate, maxrate*0.9), maxrate, maxrate/1.5)
    vcodec, segment_time = 'h264', 10

  #SEGMENT_TIME
  if argv[3].isnumeric():
    sub += ' -segment_time %d' % float(argv[3])
  else:
    sub += ' -segment_time %d' % segment_time

  return 'ffmpeg -i %s -vcodec %s -acodec aac -bsf:v h264_mp4toannexb -map 0:v:0 -map 0:a? -f segment -segment_list out.m3u8 %s out%%05d.ts' % (safename(file), vcodec, sub)

def upload(lines, uploadList):
  failures, completions = 0, 0
  executor = ThreadPoolExecutor(max_workers=15)
  futures = {executor.submit(uploader().handle, chunk): chunk for chunk in uploadList}
  uploadList = []

  for future in as_completed(futures):
    completions += 1
    result = future.result()

    if not result:
      failures += 1
      print('[%s/%s] Uploaded failed: %s' % (completions, len(futures), futures[future]))
      uploadList.append(futures[future])
      continue

    lines = lines.replace(futures[future], result)
    print('[%s/%s] Uploaded %s to %s' % (completions, len(futures), futures[future], result))

  if(len(uploadList)>0):
    print('retry upload')
    lines = upload(lines, uploadList)
  return lines

def main():

  title   = argv[2] if argv[2] else os.path.splitext(os.path.basename(argv[1]))[0]
  tmpdir  = os.path.dirname(os.path.abspath(__file__)) + '/tmp'
  command = command_generator(os.path.abspath(argv[1]))
  print('commend:%s'%command)


  if sameparams(tmpdir, command):
    os.chdir(tmpdir)
  else:
    os.mkdir(tmpdir)
    os.chdir(tmpdir)
    os.system(command)
    open('command.sh', 'w').write(command)


  lines    = checker(encrypt(open('out.m3u8', 'r').read()))
  #return

  # failures, completions = 0, 0
  # executor = ThreadPoolExecutor(max_workers=15)
  # futures  = {executor.submit(uploader().handle, chunk): chunk for chunk in pngfiles(lines)}
  #
  # for future in as_completed(futures):
  #   completions += 1
  #   result = future.result()
  #
  #   if not result:
  #     failures += 1
  #     print('[%s/%s] Uploaded failed: %s' % (completions, len(futures), futures[future]))
  #     continue
  #
  #   lines = lines.replace(futures[future], result)
  #   print('[%s/%s] Uploaded %s to %s' % (completions, len(futures), futures[future], result))

  # 上传
  lines = upload(lines, pngfiles(lines))

  """
  head = read_bytes(os.path.dirname(os.path.abspath(__file__)) + '/dangdai-32x32.png')
  head1 = head[0:-12]
  head2 = head[-12:]
  done = base64.b64encode(lines.encode('utf-8'))
  done = zlib.compress(done)
  open('out.png', 'wb').write(head1 + done+head2)
  """
  llen = len(lines)+64
  wh = math.ceil(llen/3)
  print('文本大小:%s，图片尺寸:%s' % (llen, wh))

  new_img_file_name = new_image(wh, wh, 'out', show_image=False)
  print('生成图片:%s' % (new_img_file_name))

  in_img = cv2.imread(new_img_file_name)
  steg = LSBSteg(in_img)
  done = base64.b64encode(lines.encode('utf-8'))
  done = zlib.compress(done)
  res = steg.encode_binary(done)
  cv2.imwrite('out.png', res)

  m3u8url = uploader().handle('out.png')
  print('This video\'s m3u8 has been published to: %s' % m3u8url)
  publish(lines, title)

  # if not failures:
  #   # Write to file
  #   head = read_bytes(os.path.dirname(os.path.abspath(__file__)) + '/dangdai-32x32.png')
  #   done = base64.b64encode(lines.encode('utf-8'))
  #   done = zlib.compress(done)
  #   open('out.png', 'wb').write(head + done)
  #   m3u8url = uploader().handle('out.png')
  #   print('This video\'s m3u8 has been published to: %s' % m3u8url)
  #   publish(lines, title)
  # else:
  #   print('Partially successful: %d/%d' % (completions-failures, completions))
  #   print('You can re-execute this program with the same parameters')



if __name__ == '__main__':
  main()
