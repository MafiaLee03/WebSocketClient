from Core.BaseCase import BaseCase

class OtherCase(BaseCase):
    def run(self):
        self.correct_cnt = 100
        self.add_check('check_112',19991,'test')
        self.client.run_forever()
        send = self.get_send('check_112')
        res = self.get_res('check_112')
        self.do_assert(send,res,'check_112')