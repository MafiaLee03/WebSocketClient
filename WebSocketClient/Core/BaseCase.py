#!/usr/bin/python3
#coding=utf-8
#author: libiqi

from websocket import WebSocketConnectionClosedException,WebSocketApp
import json
import _thread
import time
import Logger as log
import random
import string
# ws = create_connection('ws://121.40.165.18:8800')
# ws.send('nihao')
# while True:
#     result = ws.recv()
#     if result:
#         print(result)
#     else:
#         break
# print(result)
# ws.close()

def create_string_number(n):
    """生成一串指定位数的字符+数组混合的字符串"""
    m = random.randint(1, n)
    a = "".join([str(random.randint(0, 9)) for _ in range(m)])
    b = "".join([random.choice(string.ascii_letters) for _ in range(n - m)])
    return ''.join(random.sample(list(a + b), n))

REGISTER_NAME_LEN = 7 # 随机生成的注册的账号名字长度
REGISTER_PASSWORD = 'a123456' # 注册密码

class BaseCase():
    def __init__(self,url) -> None:
        self.url = url
        self.correct_cnt = 0
        self.error_cnt = 0
        self.is_success = True
        self.error_detail =[]
        self.check_dict = {}
        self.uid_checkid = {} # 用于通过uid找check_id
        self.client = WebSocketApp(url,on_message=self.on_message,on_open=self.on_open)
        self.limit_wait_time = 15 # 秒 大于这个时间没收到的消息就算超时，超时的消息可能出现乱序，但是还是可能收得到的
        self.login_name = 'name'
        self.login_msg = {'name':self.login_name,'password':REGISTER_PASSWORD}
        self.login()

    def on_message(self,ws,message):
        try:
            msg_d = json.loads(message)
        except:
            log.logError('只接收json消息 错误消息：{0}'.format(message))
            return message
        server_id = msg_d.get('server_id')
        req = msg_d.get('req')
        if not msg_d.get('uid'):
            log.logError('返回消息中没有uid 错误消息：{0}'.format(message))
            return message
        else:
            uid = msg_d.get('uid')
            check_id = self.uid_checkid.get(uid)
            if check_id in self.check_dict:
                if check_id == 'register' and req != '200 ok':
                    log.logError('注册失败！{}'.format(req))
                    ws.close()
                if check_id == 'login' and req != '200 ok':
                    log.logError('登录失败！{}'.format(req))
                    ws.close()
                self.check_dict[check_id]['response'] = req
            else:
                log.logError('找不到的check_id，错误值：' + check_id)
        return message

    def on_open(self,ws):

        def send_msg():
            need_break = False
            for k,v in self.check_dict.items():
                current_check_id = k
                current_server_id = v['server_id']
                current_req = v['request']
                current_uid = v['uid']
                msg_dict = {
                    'server_id':current_server_id,
                    'req':current_req,
                    'uid':current_uid
                }
                msg_json = json.dumps(msg_dict)
                try:
                    ws.send(msg_json)
                except WebSocketConnectionClosedException:
                    log.logError('网络连接已关闭')
                    return
                start_time = time.time()
                while 'response' not in self.check_dict[k]:
                    cost_time = time.time() - start_time
                    if  cost_time >= self.limit_wait_time:
                        if k == 'register' or k == 'login':
                            need_break = True
                            break
                        self.check_dict[k]['response'] = 'time out'
                        log.logWarning('{0} 消息超时！'.format(k))
                if need_break:
                    log.logError('{}超时！'.format(k))
                    break
            ws.close()

        _thread.start_new_thread(send_msg,())

    def do_assert(self,want_value,get_value,check_id):
        if want_value == get_value:
            self.correct_cnt = self.correct_cnt + 1
        else:
            self.error_cnt = self.error_cnt + 1
            self.is_success = False
            self.error_detail.append([check_id,want_value,get_value])

    def add_check(self,check_id,server_id,request):
        """
        按照下面这个格式插入内容，uid是自动加的时间戳 check_dict：
        {
            'check_1':{
                'server_id':server_id,
                'request':request,
                'uid':uid
            },
            'check_2':{
                'server_id':server_id,
                'request':request,
                'uid':uid
            }
        }

        uid_checkid:
        {'uid':check_id,'uid2':check_id2}
        """
        uid = int(time.time()*1000000)
        time.sleep(0.001) # 不等一下运算太快时间戳会重复
        check_value_dict = {'server_id':server_id,'request':request,'uid':uid}
        self.check_dict[check_id] = check_value_dict
        self.uid_checkid[uid] = check_id

    def get_send(self,check_id):
        return self.check_dict[check_id]['request']

    def get_res(self,check_id):
        try:
            result = self.check_dict[check_id]['response']
        except:
            result = None
        return result

    def run(self):
        pass

    def login(self):
        self.login_name = create_string_number(REGISTER_NAME_LEN)
        register_msg = {'name':self.login_name,'password':REGISTER_PASSWORD}
        self.add_check('register',1,register_msg)
        self.add_check('login',10000,self.login_msg)

if __name__ =='__main__':
    ws = BaseCase('ws://121.40.165.18:8800')
    ws.add_check('check_1',19980,'test')
    ws.client.run_forever()
    # a = json.loads('{"server_id":19980,"req":"test","uid":1651135261952115}')
    # print(a)