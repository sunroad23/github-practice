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

    def __init__(self, ppg, major_s, major_o, rs):
        self.ppg = ppg
        self.major_s = major_s
        self.major_o = major_o
        self.rs = rs

    def Z_val(self):
        '''
        10 Segment 계산
        '''
        outp_data = np.array(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
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
                    temp_arr = np.array([mean_1, mean_2, mean_3, mean_4, mean_5,
                                         mean_6, mean_7, mean_8, mean_9, mean_10])
                    outp_data = np.vstack((outp_data, temp_arr))

        return outp_data
