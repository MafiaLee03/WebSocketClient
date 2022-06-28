from Core.BaseCase import BaseCase

class DemoCase(BaseCase):
    def run(self):
        self.correct_cnt = 100
        self.add_check('check_1',19990,'test')
        self.client.run_forever()
        send = self.get_send('check_1')
        res = self.get_res('check_1')
        self.do_assert('200 OK',res,'check_1')