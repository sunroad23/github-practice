"""
ID와 DNN.DNN() 출력값을 입력으로 하는 ID class를 생성함
[1] Z_val()
    1. 연속된 두 파형이 모두 rs가 80 이상인 경우 z_val를 계산함
    2. major_s와 major_o값을 이용하여 max, min값을 계산함
    3. max, min 값을 이용하여 표준화를 진행한 뒤 1차 미분시킴
    4. 이 후 적절히 10분할 한 뒤 구간별 평균값을 계산함
    5. 모든 pulse에 대해 위 과정을 반복함
    6 1개의 z_val array를 출력함
[2] Normal(z_val, thres_normal)
    1. Z_val() 출력값과 thres_normal값을 입력받음
    2. 정상인군과 환자군에 대한 10개씩의 평균과 표준편차를 입력함
    3. 정상인군의 구간별 평균과 표준편차를 이용하여 10개의 z_val를 계산함
        3.1 10개의 z_val의 평균(z_norm)을 계산함
    4. 환자군의 구간별 평균과 표준편차를 이용하여 10개의 z_val를 계산함
        4.1 10개의 z_val의 평균(z_patient)을 계산함
    5. z_norm - z_patient 값의 평균이 임계값보다 크면 group2 작으면 group1을 저장함
    6. pulse별 z_value, group이 저장된 array와 group 정보를 출력함
"""

import pickle
import numpy as np


class ID:

    def __init__(self, subject_id, spo2_date, ppg, major_s, major_o, rs):
        self.subject_id = subject_id
        self.spo2_date = spo2_date
        self.ppg = ppg
        self.major_s = major_s
        self.major_o = major_o
        self.rs = rs

    def Z_val(self):
        '''
        신원확인 시작
        '''
        outp_data = np.array(['date', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
        for i in range(0, len(self.rs)):

            if self.rs[i] >= 80:

                '''
                pre_W 찾기
                '''
                start_point = i

                '''
                post_W 찾기
                '''
                j = i + 1
                while 1:
                    # 종료조건
                    if j >= len(self.rs):
                        end_point = i + 1
                        break
                    ##########
                    if self.rs[j] >= 80:
                        end_point = j
                        break
                    j += 1

                '''
                start ~ end 길이 허용 기준(파형길이 허용 기준)
                '''
                # x초 = a / 62.5
                # 1박동 : x초 = y박동 : 60초
                # xy = 60
                # y = 60/x
                # y= 60*62.5/a [bpm]
                if 50 <= (60 * 62.5 / (end_point - start_point)) <= 120:

                    '''
                    Normalization(표준화)
                    '''
                    ppg_max = 0
                    ppg_min = 0

                    for k in range(start_point, end_point):
                        if self.major_s[k] >= 10:
                            ppg_max = self.ppg[k]
                        if self.major_o[k] >= 10:
                            ppg_min = self.ppg[k]

                    if start_point - 1 < 0:
                        ppg_beat = np.append(np.array([0]), self.ppg[start_point:end_point])
                    else:
                        ppg_beat = np.array(self.ppg[start_point - 1:end_point])

                    for k in range(0, len(ppg_beat)):
                        ppg_beat[k] = 2 * (ppg_beat[k] - ppg_min) / (ppg_max - ppg_min) - 1

                    '''
                    미분
                    '''
                    diff_beat = np.array([])
                    for k in range(1, len(ppg_beat)):
                        diff_val = (ppg_beat[k] - ppg_beat[k - 1]) * 62.5
                        diff_beat = np.append(diff_beat, diff_val)

                    '''
                    10 분할
                    '''
                    gap_x = end_point - start_point
                    round_x = round(gap_x, -1)
                    extra_x = gap_x - round_x

                    div_x = round_x / 10
                    div_arr = np.array([])

                    for div_i in range(0, 10):
                        div_arr = np.append(div_arr, div_x)

                    extra_i = 1
                    while 1:
                        # 종료조건
                        if extra_x == 0:
                            break
                        ##########
                        div_arr[extra_i] = div_arr[extra_i] + extra_x / abs(extra_x)
                        extra_i += 2
                        extra_x -= extra_x / abs(extra_x)

                    div_temp = np.array([div_arr[0]])
                    for div_i in range(1, len(div_arr)):
                        div_temp = np.append(div_temp, sum(div_arr[0:div_i + 1]))
                    div_arr = np.array(div_temp, dtype='int32')

                    mean_1 = np.mean(diff_beat[0: div_arr[0]])
                    mean_2 = np.mean(diff_beat[div_arr[0]: div_arr[1]])
                    mean_3 = np.mean(diff_beat[div_arr[1]: div_arr[2]])
                    mean_4 = np.mean(diff_beat[div_arr[2]: div_arr[3]])
                    mean_5 = np.mean(diff_beat[div_arr[3]: div_arr[4]])

                    mean_6 = np.mean(diff_beat[div_arr[4]: div_arr[5]])
                    mean_7 = np.mean(diff_beat[div_arr[5]: div_arr[6]])
                    mean_8 = np.mean(diff_beat[div_arr[6]: div_arr[7]])
                    mean_9 = np.mean(diff_beat[div_arr[7]: div_arr[8]])
                    mean_10 = np.mean(diff_beat[div_arr[8]: div_arr[9]])

                    '''
                    저장 데이터 구성
                    '''
                    temp_arr = np.array(
                        [self.spo2_date, mean_1, mean_2, mean_3, mean_4, mean_5, mean_6, mean_7, mean_8, mean_9,
                         mean_10])
                    outp_data = np.vstack((outp_data, temp_arr))

        return outp_data

    def Normal(self, z_val, thres_normal):
        '''
        정상인군 및 환자군 구분
        '''
        normal_ref_avg = [10.69212, 0.09444, -4.56011, -2.04733, -1.65606, -2.95036, -3.30288, -4.21415, -0.89546,
                          9.35399]
        normal_ref_std = [2.08018, 1.60424, 1.73688, 1.70885, 1.38747, 1.41167, 1.31885, 1.49500, 1.47752, 2.25465]
        patient_ref_avg = [10.43759, 1.87684, -3.48909, -3.68604, -3.82318, -3.74391, -2.96788, -3.79808, -0.36366,
                           9.67341]
        patient_ref_std = [2.56858, 2.11944, 1.16013, 0.91668, 0.59909, 0.59505, 0.64350, 0.99043, 2.08266, 3.13927]

        normal_outp = np.array(['z:1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'z:avg'])
        patient_outp = np.array(['z:1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'z:avg'])
        for z_i in range(1, len(z_val)):
            outp_val = np.array(z_val[z_i, 1:11], dtype='float32')

            normal_temp = np.array([])
            for n_i in range(0, 10):
                val = (outp_val[n_i] - normal_ref_avg[n_i]) / normal_ref_std[n_i]
                normal_temp = np.append(normal_temp, abs(val))
            normal_temp = np.append(normal_temp, np.mean(normal_temp))
            normal_outp = np.vstack((normal_outp, normal_temp))

            patient_temp = np.array([])
            for p_i in range(0, 10):
                val = (outp_val[p_i] - patient_ref_avg[p_i]) / patient_ref_std[p_i]
                patient_temp = np.append(patient_temp, abs(val))
            patient_temp = np.append(patient_temp, np.mean(patient_temp))
            patient_outp = np.vstack((patient_outp, patient_temp))

        diff_z = np.array(['date', 'z(normal-patient)', 'result'])
        for z_i in range(1, len(normal_outp)):
            val = float(normal_outp[z_i, -1]) - float(patient_outp[z_i, -1])
            if val > float(thres_normal):
                result = 'group2'
            else:
                result = 'group1'
            diff_z_temp = np.array([self.spo2_date, val, result])
            diff_z = np.vstack((diff_z, diff_z_temp))

        result_outp = ''
        if np.mean(diff_z[1::, 1].astype('float32')) > float(thres_normal):
            result_outp = 'group2'
        else:
            result_outp = 'group1'

        return diff_z, result_outp
