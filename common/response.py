"""
pwaa 알고리즘 실행을 위한 response_entity_type 함수를 생성함
[1] response_code가 '1000'인 경우
    1. __name__=='__main__' 위치('.')에서 학습모델(dnn_model.pickle)을 불러옴
    2. entity_body를 입력하여 DNN 클래스의 인스턴스인 input_data 객체를 생성함
        DNN.DNN(): ppg, diff, major_s, major_o, rs와 같은 continous data를 생성함
        DNN.Re_m(rs): n00, n80, hr, hrv, warn, spo2_warn, bp_warn과 같은 numeric data를 생성함
    3. entity_body와 DNN.DNN() 출력값을 입력하여 ID 클래스의 인스턴스인 rs_data 객체를 생성함
        ID.Z_val(): 각 pulse당 10개 구간별 평균값을 생성함
        ID.Normal(): ID.Z_val() 출력값과 임계값(=-0.770)을 이용하여 pulse별 z_value와 최종 판정값(group1/2)을 생성함
    4. 입력된 PPG에 대한 10개 구간별 평균값과 전체 평균(=10개 구간별 평균값의 평균값)을 저장함
    5. response_body를 출력함
        "responseStatus": SUCCESS,
        "entry": {"hr": , "hrv": , "reliability": , "wave_warn": , "spo2_warn": , "bp_warn": },
                "z_val": {"z1": , "z2": , "z3": , "z4": , "z5": , "z6": , "z7": , "z8": , "z9": , "z10": , "z_avg": },
        "group": {"result": }
[1] response_code가 '1000'이 아닌 경우
    5. response_body를 출력함
        "responseStatus": FAILURE

(210919) 출력값에 파라미터별 풀네임과 단위 추가
"""

from common.response_status import response_status
from pwaa.pwaa_dnn import DNN
from pwaa.pwaa_id import ID

import numpy as np
import json


def response_entity_type(response_code, entity_body):

    if response_code == '1000':

        # # entity_body = (name, saved, spo2, hr, ppg)
        # input_data = DNN(entity_body[4])
        #
        # dnn_outp = input_data.DNN()
        # ppg = dnn_outp[:, 0]
        # diff = dnn_outp[:, 1]
        # major_s = dnn_outp[:, 2]
        # major_o = dnn_outp[:, 3]
        # major_w = dnn_outp[:, 4]
        # rs = dnn_outp[:, 5]
        #
        # re_m_outp = input_data.Re_m(rs)
        # n00 = re_m_outp[0]
        # n80 = re_m_outp[1]
        # hr = re_m_outp[2]
        # hrv = re_m_outp[3]
        #
        # rs_data = ID(ppg, major_s, major_o, rs)
        # z_val = rs_data.Z_val()
        #
        # z_arr = np.array([])
        # for z_i in range(0, 10):
        #     z_mean = np.mean(z_val[1::, z_i].astype('float32'))
        #     z_arr = np.append(z_arr, z_mean)
        # z_arr = np.append(z_arr, np.mean(z_arr))
        # for z_i in range(0, len(z_arr)):
        #     z_arr[z_i] = round(z_arr[z_i], 3)
        #
        # # np.savetxt('K:/s01.csv', dnn_outp, fmt='%s', delimiter=",")
        # # np.savetxt('K:/s02.csv', re_m_outp, fmt='%s', delimiter=",")
        # # np.savetxt('K:/s03.csv', z_val, fmt='%s', delimiter=",")

        response_body = {
            'spo2': 1,
            'spo2_hr': 2,
            'ai_hr': 3,
            'ai_hrv': 4,
            'reliability': 5
        }

        # response_body = {
        #     'responseStatus': response_status.get(response_code),
        #     'spo2': entity_body[2],
        #     'spo2_hr': entity_body[3],
        #     'ai_hr': hr,
        #     'ai_hrv': hrv,
        #     'reliability': int(100*n80/n00),
        #     'z_val': z_arr[-1]
        # }

        # print('type')
        # print(type(response_status.get(response_code)))
        # print(type(entity_body[2]))
        # print(type(entity_body[3]))
        # print(type(hr))
        # print(type(hrv))
        # print(type(int(100*n80/n00)))
        # print(z_arr[-1])
        # print('---')

        response_body = json.dumps(response_body)
        return response_body

    else:
        response_body = {
            'responseStatus': response_status.get(response_code)
        }

        response_body = json.dumps(response_body)
        return response_body
