"""
request body로 들어온 json 값에서 key=entry에 해당하는 value를 가져옴
value에 저장된 subject, spo2_date, spo2_val, spo2_hr, wave, bp_date, bp_hr, bps_val, bpd_val를 구분함
위 값을 출력함
"""

from module import dbmodule
import json


class Service:

    def __init__(self, request_body):
        self.request_body = request_body

    def inp(self):
        print('---service_inp.py---')
        print(self.request_body, type(self.request_body))
        print('---------------')

        entry = self.request_body

        name = entry['name']
        saved = entry['saved']
        spo2 = entry['spo2']
        hr = entry['hr']

        if 'ppg' in entry:
            ppg = [int(x) for x in entry['ppg']]
        else:
            ppg = 'n/a'

        '''
        mysql 관련 코드 임시 제거
        '''
        # spo2_db = json.dumps({'spo2': int(spo2), 'unit': 'percent'})
        # hr_db = json.dumps({'hr': int(hr), 'unit': 'bpm'})
        # ppg_db = json.dumps({'ppg': ppg})
        #
        # db_class = dbmodule.Database()
        # sql = "INSERT INTO medilearn_db.test_table (name, saved, created, spo2, hr, ppg) " \
        #       "VALUES ('%s', '%s', NOW(), '%s', '%s', '%s')" \
        #       % (name, saved, spo2_db, hr_db, ppg_db)
        # # print(sql)
        # db_class.execute(sql)
        # db_class.commit()

        return name, saved, spo2, hr, ppg
