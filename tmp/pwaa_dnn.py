"""
ID, SpO2, PPG, BP, DNN_model 정보를 입력으로 하는 DNN class를 생성함
[1] DNN.DNN()
    1. pickle 형태의 학습모델(dnn_model.pickle)을 불러옴
    2. 입력된 PPG 데이터를 4분주한 뒤 Raw 데이터와 1차 미분 데이터로 구분함
    3. 74 크기의 윈도우를 이동시키며 학습데이터 가공 및 학습모델 적용을 시작함
        3.1 특이점 계산(Peak, Low, Surgy)
        3.2 포커싱 및 표준화 알고리즘 적용
        3.3 입력데이터 생성(n=124) 후 6개의 심층신경망(S, O, W, Z, ES, EE)에 적용
        3.4 다수결 판정
        3.5 인식률 계산
    3. 5개의 Continous Data(ppg, diff, major_s, major_o, rs)를 출력함
[2] DNN.Re_m(rs)
    1. 연속된 두 파형이 모두 rs가 80이상인 경우 HR과 HRV를 계산함
    2. n00 = int(hr/2)이며 n80은 rs가 80이상인 비율로 정의한 뒤
        2.1 rs가 80이상인 비율(n80/n00)이 90% 이상인 경우를 "정상"으로 정의함
        2.2 그 외의 경우 "재측정" 판정을 내림
    3. SpO2 장비가 측정한 HR과 AI가 판정한 HR의 오차를 비교하여
        3.1 오차가 10 이상인 경우 "재측정" 판정을 내림
        3.2 그 외 "정상" 판정을 내림
    4. BP 장비가 측정한 HR과 AI가 판정한 HR의 오차를 비교하여
        4.1 오차가 10 이상인 경우 "재측정" 판정을 내림
        4.2 그 외 "정상" 판정을 내림
    5. 7개의 Numeric Data(n00, n80, hr, hrv, warn, spo2_warn, bp_warn)를 출력함
"""

import pickle
import numpy as np
from datetime import datetime


class DNN:

    def __init__(self, subject_id, spo2_date, spo2_val, spo2_hr, wave, bp_date, bp_hr, bps_val, bpd_val, dnn_path):
        self.subject_id = subject_id
        self.spo2_date = spo2_date
        self.spo2_val = spo2_val
        self.spo2_hr = spo2_hr
        self.wave = wave
        self.bp_date = bp_date
        self.bp_hr = bp_hr
        self.bps_val = bps_val
        self.bpd_val = bpd_val
        self.dnn_path = dnn_path

    def DNN(self):
        sys_start_time = (datetime.now().hour * 3600) + (datetime.now().minute * 60) + datetime.now().second + (datetime.now().microsecond * 0.000001)
        '''
        심층신경망 파라미터 불러오기
        '''
        # ---------------1안---------------
        # for dnn_i in range(0, 24):
        #     if dnn_i == 6 or dnn_i == 7 or dnn_i == 8 or dnn_i == 15 or dnn_i == 16 or dnn_i == 17:
        #         continue
        #
        #     w_name = self.dnn_path + '/' + 'w' + str(dnn_i) + ".pickle"
        #     with open(w_name, 'rb') as f:
        #         globals()['w{0}'.format(str(dnn_i))] = pickle.load(f)
        #
        #     b_name = self.dnn_path + '/' + 'b' + str(dnn_i) + ".pickle"
        #     with open(b_name, 'rb') as f:
        #         globals()['b{0}'.format(str(dnn_i))] = pickle.load(f)

        # ---------------2안---------------
        # f_name = self.dnn_path + '/' + 'dnn_model' + ".pickle"
        # with open(f_name, 'rb') as f:
        #     dnn_model = pickle.load(f)
        #
        # dnn_ref = 0
        # for dnn_i in range(0, 24):
        #     if dnn_i == 6 or dnn_i == 7 or dnn_i == 8 or dnn_i == 15 or dnn_i == 16 or dnn_i == 17:
        #         continue
        #     if (dnn_ref + 1) % 3 == 0:
        #         globals()['w{0}'.format(str(dnn_i))] = dnn_model[dnn_ref][0:124, 0:21].astype('float32')
        #         globals()['b{0}'.format(str(dnn_i))] = dnn_model[18, dnn_ref, :][0:21].astype('float32')
        #     else:
        #         globals()['w{0}'.format(str(dnn_i))] = dnn_model[dnn_ref][0:124, 0:124].astype('float32')
        #         globals()['b{0}'.format(str(dnn_i))] = dnn_model[18, dnn_ref, :][0:124].astype('float32')
        #     dnn_ref += 1

        # ---------------3안---------------
        f_name = self.dnn_path + '/' + "dnn_model.pickle"
        with open(f_name, 'rb') as f:
            dnn_model = pickle.load(f)

        for dnn_i in range(0, 24):
            if dnn_i == 6 or dnn_i == 7 or dnn_i == 8 or dnn_i == 15 or dnn_i == 16 or dnn_i == 17:
                continue
            globals()['w{0}'.format(str(dnn_i))] = np.array(dnn_model['w{0}'.format(str(dnn_i))], dtype='float32')
            globals()['b{0}'.format(str(dnn_i))] = np.array(dnn_model['b{0}'.format(str(dnn_i))], dtype='float32')

        '''
        입력데이터 4분주
        '''
        def NDivision(arr, n):
            outp = np.array([])
            for i in range(0, len(arr)):
                if i % n == 0:
                    outp = np.append(outp, arr[i])
            return outp
        ppg = NDivision(self.wave, int(250 / 62.5))

        '''
        1차 미분
        '''
        # Bionics IRB 데이터의 미분값 잡음을 제거하기 위해 아래와 같은 모듈을 설계함
        def Differential(arr, period):
            # diff와 raw의 원소 수를 맟추기 위해 diff는 [0]에서 시작함
            outp = np.array([0])
            for i in range(0, len(arr)):
                # 종료조건
                if i + 4 > len(arr):
                    break
                ###############
                # 계속조건
                if i - 2 < 0:
                    outp = np.append(outp, 0)
                    continue
                ###############
                outp = np.append(outp, (np.mean(arr[i - 1:i + 4]) - np.mean(arr[i - 2:i + 3])) / period)
            return outp

        diff_arr = Differential(ppg, 1/62.5)
        raw = np.array(ppg[0:len(diff_arr)])

        '''
        학습데이터 가공 및 학습모델 적용 시작
        '''
        major_ref = 0
        for i in range(0, len(raw)):

            # if i % 100 == 0:
            #     print('진행률: %d %%'%(int(100*(i+1)/len(raw))))

            # 종료 조건
            if i + 73 >= len(raw):
                break
            ###############

            inp = raw[i:i + 74]
            diff = diff_arr[i:i + 74]

            '''
            특이점 계산
            '''
            # Peak, Low, Surgy
            # ref가 0이면 Peak, 1이면 Notch
            def SingularPoint(arr, ref):

                outp = np.zeros(len(arr))
                for i in range(0, len(arr)):
                    # 종료 조건
                    if i + 5 >= len(arr):
                        break
                    ###############
                    # 통과 조건
                    if i - 5 < 0:
                        continue
                    ###############
                    if ref == 0:
                        if arr[i] == np.max(arr[i - 5:i + 6]):
                            outp[i] = 1
                    elif ref == 1:
                        if arr[i] == np.min(arr[i - 5:i + 6]):
                            outp[i] = 1

                # 1이 연속으로 나올 경우에 맨 앞의 1만 유지함
                for i in range(0, len(outp)):
                    # 종료조건
                    if i + 5 >= len(outp):
                        break
                    ###############
                    if outp[i] == 1:
                        for j in range(i + 1, i + 6):
                            outp[j] = 0

                return outp

            peak = SingularPoint(inp, 0)
            low = SingularPoint(inp, 1)
            surgy = SingularPoint(diff, 0)

            '''
            심층신경망 입력데이터 가공
            '''
            # ref = 0 이면 raw 표준화, ref = 1 이면 diff 표준화
            def Focusing(arr, ref):

                # 포커싱(Focusing)
                outp = np.array([])
                # x[n], x[n+7], x[n+13], x[n+18], x[n+22], x[n+25]
                k = 0
                for j in range(0, 6):
                    outp = np.append(outp, arr[k])
                    k = k + (7 - j)
                # x[n+27], x[n+28], ...... , x[n+46]
                for j in range(0, 20):
                    outp = np.append(outp, arr[k])
                    k = k + 1
                # x[n+48], x[n+51], x[n+55], x[n+60], x[n+66], x[n+73]
                k = k + 1
                for j in range(0, 6):
                    outp = np.append(outp, arr[k])
                    k = k + (3 + j)

                foc_data = np.array(outp)

                # 표준화(Standardization)
                x_max = np.max(foc_data)
                x_min = np.min(foc_data)
                amp = x_max - x_min
                # RuntimeWarning: invalid value encountered in double_scalars 문제 해결을 위해
                if abs(amp) < 0.01:
                    amp = 0.01
                ##############################
                if ref == 0:
                    for j in range(0, len(foc_data)):
                        foc_data[j] = (2 * (foc_data[j] - x_min) / amp) - 1
                elif ref == 1:
                    for j in range(0, len(foc_data)):
                        foc_data[j] = (2 * foc_data[j] / amp)

                st_data = np.array(foc_data)

                return st_data

            dnn_raw = Focusing(inp, 0)
            dnn_diff = Focusing(diff, 1)

            '''
            심층신경망의 입력데이터로 가공
            '''
            dnn_peak = peak[27:47]
            dnn_low = low[27:47]
            dnn_surgy = surgy[27:47]

            # 심층신경망 입력데이터
            dnn_inp = np.hstack((dnn_raw, dnn_diff, dnn_peak, dnn_low, dnn_surgy))

            '''
            심층신경망 적용
            '''
            def DNN(arr, h1_w, h1_b, h2_w, h2_b, o_w, o_b, print_name):

                x = arr

                def Dnn_Relu(arr):
                    for i in range(0, arr.shape[0]):
                        if arr[i] < 0:
                            arr[i] = 0
                        else:
                            pass
                    return arr

                # h1_w = h1_w[0:124, 0:124]
                # h2_w = h2_w[0:124, 0:124]
                # o_w = o_w[0:124, 0:21]
                # h1_b = h1_b[0:124]
                # h2_b = h2_b[0:124]
                # o_b = o_b[0:21]

                z1 = np.matmul(x, h1_w) + h1_b
                z1 = Dnn_Relu(z1)
                z2 = np.matmul(z1, h2_w) + h2_b
                z2 = Dnn_Relu(z2)
                z = np.matmul(z2, o_w) + o_b
                outp = np.zeros(len(z))
                outp[np.argmax(z)] = 1

                return outp

            dnn_hp1 = DNN(dnn_inp, w0, b0, w1, b1, w2, b2, 'Systolic Point')
            dnn_lp1 = DNN(dnn_inp, w3, b3, w4, b4, w5, b5, 'Onset Point')
            dnn_s1 = DNN(dnn_inp, w9, b9, w10, b10, w11, b11, 'Derivative Peak Point')
            dnn_s2 = DNN(dnn_inp, w12, b12, w13, b13, w14, b14, 'Derivative Peak Point')
            dnn_es = DNN(dnn_inp, w18, b18, w19, b19, w20, b20, 'Error Start Point')
            dnn_ee = DNN(dnn_inp, w21, b21, w22, b22, w23, b23, 'Error End Point')

            '''
            다수결 판정
            '''
            # dnn_hp1, dnn_lp1, dnn_lp2, dnn_s1, dnn_s2, dnn_s3, dnn_es, dnn_ee
            # 20 + (927-1)
            # x[n], x[n+7], x[n+13], x[n+18], x[n+22], x[n+25]
            # x[n+27], x[n+28], ...... , x[n+46]
            # x[n+48], x[n+51], x[n+55], x[n+60], x[n+66], x[n+73]
            if major_ref == 0:
                major_hp1 = np.append(np.zeros(27), dnn_hp1[0:20])
                major_lp1 = np.append(np.zeros(27), dnn_lp1[0:20])
                major_s1 = np.append(np.zeros(27), dnn_s1[0:20])
                major_s2 = np.append(np.zeros(27), dnn_s2[0:20])
                major_es = np.append(np.zeros(27), dnn_es[0:20])
                major_ee = np.append(np.zeros(27), dnn_ee[0:20])
                major_ref = 1
            else:
                major_hp1 = np.append(major_hp1, 0)
                dnn_hp1 = np.append(np.zeros(len(major_hp1) - 20), dnn_hp1[0:20])
                major_hp1 = major_hp1 + dnn_hp1

                major_lp1 = np.append(major_lp1, 0)
                dnn_lp1 = np.append(np.zeros(len(major_lp1) - 20), dnn_lp1[0:20])
                major_lp1 = major_lp1 + dnn_lp1

                major_s1 = np.append(major_s1, 0)
                dnn_s1 = np.append(np.zeros(len(major_s1) - 20), dnn_s1[0:20])
                major_s1 = major_s1 + dnn_s1

                major_s2 = np.append(major_s2, 0)
                dnn_s2 = np.append(np.zeros(len(major_s2) - 20), dnn_s2[0:20])
                major_s2 = major_s2 + dnn_s2

                major_es = np.append(major_es, 0)
                dnn_es = np.append(np.zeros(len(major_es) - 20), dnn_es[0:20])
                major_es = major_es + dnn_es

                major_ee = np.append(major_ee, 0)
                dnn_ee = np.append(np.zeros(len(major_ee) - 20), dnn_ee[0:20])
                major_ee = major_ee + dnn_ee

        '''
        인식률 계산
        '''
        recog_score = np.zeros(len(major_hp1))
        for i in range(0, len(major_s1)):

            if major_s1[i] >= 10:
                '''
                W(S1) 인식률
                '''
                recog_s1 = major_s1[i]
                recog_es = np.sum(major_es[i - 30:i + 30])
                recog_ee = np.sum(major_ee[i - 30:i + 30])

                '''
                S(HP1) 인식률
                '''
                j = i + 1
                while 1:
                    # 종료조건
                    if j >= len(major_s1):
                        recog_hp1 = max(major_hp1[i:j + 1])
                        break
                    ##########
                    # 종료조건
                    if major_s1[j] >= 10:
                        recog_hp1 = max(major_hp1[i:j + 1])
                        break
                    ##########
                    if major_hp1[j] >= 10:
                        recog_hp1 = major_hp1[j]
                    j += 1

                '''
                O(LP1) 인식률
                '''
                j = i - 1
                while 1:
                    # 종료조건
                    if j <= 0:
                        recog_lp1 = max(major_lp1[j:i])
                        break
                    ##########
                    # 종료조건
                    if major_s1[j] >= 10:
                        recog_lp1 = max(major_lp1[j:i])
                        break
                    ##########
                    if major_lp1[j] >= 10:
                        recog_lp1 = major_lp1[j]
                    j -= 1

                recog_score[i] = recog_hp1 + recog_lp1 + recog_s1 + (40 - recog_es - recog_ee)

        sys_end_time = (datetime.now().hour * 3600) + (datetime.now().minute * 60) + datetime.now().second + (datetime.now().microsecond * 0.000001)
        # print('SYS 진행시간(초): %.2f' % (sys_end_time - sys_start_time), end='\n')

        return np.vstack((raw[0:len(major_hp1)], diff_arr[0:len(major_hp1)], major_hp1, major_lp1, recog_score)).T

    def Re_m(self, rs):
        recog_score = np.array(rs)

        # x초 = a / 62.5
        # 1박동 : x초 = y박동: 60초
        # xy = 60
        # y = 60 / x
        # y = 60 * 62.5 / a [bpm]
        hr_arr = np.array([])
        hrv_arr = np.array([])

        for rs_i in range(0, len(recog_score)):
            if recog_score[rs_i] >= 80:

                rs_j = rs_i + 1
                while 1:
                    # 종료조건
                    if rs_j >= len(recog_score):
                        break
                    ##########
                    if recog_score[rs_j] >= 80:

                        if 60 * 62.5 / (rs_j - rs_i) >= 50 and 60 * 62.5 / (rs_j - rs_i) <= 120:
                            hr_arr = np.append(hr_arr, 60 * 62.5 / (rs_j - rs_i))
                            hrv_arr = np.append(hrv_arr, (rs_j - rs_i)/62.5)

                        break
                    rs_j += 1

        hr = round(np.mean(hr_arr), 2)
        hrv = round(np.std(hrv_arr)*1000, 2)

        '''
        재측정 1: RS가 80이상인 박동이 90% 이하인 경우
        '''
        n00 = int(hr / 2)
        n80 = 0
        for rs_i in range(0, len(recog_score)):
            if recog_score[rs_i] >= 80:
                n80 += 1

        warn = ''
        if n00 == 0:
            warn = "remeasurement"
        else:
            if 100 * n80 / n00 >= 90:
                warn = "normal"
            else:
                warn = "remeasurement"

        '''
        재측정 2: AI가 계산한 HR과 SpO2 장비가 측정한 HR의 오차가 10 Hz 이상인 경우
        '''
        spo2_warn = ''
        if abs(hr - self.spo2_hr) >= 10:
            spo2_warn = "remeasurement"
        else:
            spo2_warn = "normal"

        '''
        재측정 3: AI가 계산한 HR과 NIBP 장비가 측정한 HR의 오차가 10 Hz 이상인 경우
        '''
        bp_warn = ''
        if abs(hr - self.bp_hr) >= 10:
            bp_warn = "remeasurement"
        else:
            bp_warn = "normal"

        '''
        데이터 출력
        '''
        return np.array([n00, n80, hr, hrv, warn, spo2_warn, bp_warn])
