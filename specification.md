# API Specification

## 재측정 및 질환군 판정을 위한 PWAA 알고리즘

description
1. AI가 판정한 PPG 파형의 특이점과 신뢰성(Recognition Score, RS)을 기반으로 재측정 및 질환군 판정을 진행한다.
2. 재측정 판정: 3번의 재측정 판정을 진행한다.
   1. 첫 번째 재측정 판정: RS가 80이상인 단일 심박동 파형이 전체 심박동 파형의 90% 미만일 경우 환자에게 SpO2 재측정을 권장한다.
    2. 두 번째 재측정 판정: AI가 판정한 심박수와 SpO2 장비가 판정한 심박수의 오차가 10Hz 이상이라면 환자에게 SpO2 재측정을 권장한다.
    3. 세 번째 재측정 ㅍ나정: AI가 판정한 심박수와 BP 장비가 판정한 심박수의 오차가 10Hz 이상이라면 환자에게 BP 재측정을 권장한다.
3. 질환군 판정
    1. 단일 심박동 파형별 통계값(z-value)을 계산한 뒤 각 파형이 정상인군과 환자군 중 어느 쪽에 가까운지 판정한다.

> POST URL: /

### Request
1. Method: POST
2. URI: /1.1/pwaa
3. Data Type: json
```
{
  "entry": {
    "subject": "20-00010",
    "spo2_date": "2020-11-12T07:32:15+0900",
    "spo2_val": "97",
    "spo2_hr": "61",
    "wave": [
      "1198", "1198", "1198", "1198", "1192", ......, "0"
    ],
    "bp_date": "2020-11-12T22:20:40.000Z",
    "bp_hr": "54",
    "bps_val": "129",
    "bpd_val": "80"
  }
}

```
|이름|데이터타입|설명|예시|
|---|---|---|---|
|entry|Object|PWAA 입력데이터||
|subject|String|임상참여자의 고유 ID|"20-00010"|
|spo2_date|String|SpO2 장비 사용일|"2020-11-12"|
|spo2_val|String|SpO2 수치(%)|"97"|
|spo2_hr|String|SpO2 장비로 측정한 심박수(Hz)|"61"|
|wave|List|SpO2 장비로 측정한 PPG wave(n=7500, t(s)=30)|["1198","1198",...,"0"]|
|bp_date|String|BP 장비 사용일|"2020-11-12"|
|bp_hr|String|BP 장비로 측정한 심박수(Hz)|"54"|
|bps_val|String|수축기혈압(mmHg)|"129"|
|bpd_val|String|이완기혈압(mmHg)|"80"|

### Response

```
{
    "responseStatus": {
        "code": 1000,
        "message": "SUCCESS"
    },
    "entry": {
        "hr": {
            "value": "69.24",
            "name": "heart rate",
            "unit": "bpm"
        },
        "hrv": {
            "value": "83.62",
            "name": "heart rate variability",
            "unit": "millisecond"
        },
        "reliability": {
            "value": "94.12",
            "name": "PPG Waveform Reliability",
            "unit": "na"
        },
        "wave_warn": {
            "value": "normal",
            "name": "Motion Artifact detection",
            "unit": "na"
        },
        "spo2_warn": {
            "value": "normal",
            "name": "SpO2 equipment error",
            "unit": "na"
        },
        "bp_warn": {
            "value": "remeasurement",
            "name": "BP equipment error",
            "unit": "na"
        }
    },
    "z_val": {
        "z1": 10.447,
        "z2": 2.078,
        "z3": -2.312,
        "z4": -2.547,
        "z5": -3.527,
        "z6": -3.926,
        "z7": -3.493,
        "z8": -4.551,
        "z9": -1.357,
        "z10": 9.407,
        "z_avg": 0.022,
        "name": "Average value for each PPG section",
        "unit": "na"
    },
    "group": {
        "result": "group2",
        "name": "group1 or group2",
        "unit": "na"
    }
}
```

|이름|데이터타입|설명|예시|
|---|---|---|---|
|**responseStatus**|**Object**|**응답 상태**||
|code|Integer|응답 상태 코드|1000|
|message|String|응답 상태 메세지|"SUCCESS"|
|||||
|**entry**|**Object**|**AI 판정값**||
|**hr**|**Object**|**AI가 판정한 심박수(Hz)**||
|value|String|판정값|"62.63"|
|name|String|파라미터명|"heart rate"|
|unit|String|단위|"bpm"|
|**hrv**|**Object**|**AI가 판정한 심박변이도(ms)**||
|value|String|판정값|"86.09"|
|name|String|파라미터명|"heart rate variability"|
|unit|String|단위|"millisecond"|
|**reliability**|**Object**|**AI에 의한 PPG 파형의 신뢰성 판정**||
|value|String|판정값|"94.12"|
|name|String|파라미터명|"PPG Waveform Reliability"|
|unit|String|단위|"na"|
|**wave_warn**|**Object**|**AI가 판정한 RS 기반 재측정 판정**||
|value|String|판정값|"normal" or "remeasurement"|
|name|String|파라미터명|"Motion Artifact detection"|
|unit|String|단위|"n/a"|
|**spo2_warn**|**Object**|**AI 및 SpO2 정보 기반 재측정 판정**||
|value|String|판정값|"normal" or "remeasurement"|
|name|String|파라미터명|"SpO2 equipment error"|
|unit|String|단위|"n/a"|
|**bp_warn**|**Object**|**AI 및 BP 정보 기반 재측정 판정**||
|value|String|판정값|"normal" or "remeasurement"|
|name|String|파라미터명|"BP equipment error"|
|unit|String|단위|"n/a"|
|||||
|**z_val**|**Object**|**개인 특성**||
|z1|float|판정값|10.447|
|z2|float|판정값|2.078|
|z3|float|판정값|-2.312|
|z4|float|판정값|-2.547|
|z5|float|판정값|-3.527|
|z6|float|판정값|-3.926|
|z7|float|판정값|-3.493|
|z8|float|판정값|-4.551|
|z9|float|판정값|-1.357|
|z10|float|판정값|9.407|
|z_avg|float|판정값|0.022|
|name|String|파라미터명|"Average value for each PPG section"|
|unit|String|단위|"n/a"|
|||||
|**group**|**Object**|**환자군 구분**||
|value|String|판정값|"group1" or "group2"|
|name|String|파라미터명|"group1 or group2"|
|unit|String|단위|"n/a"|
