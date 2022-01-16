"""
post method를 처리하는 PWAA 함수를 생성함
request 내의 json 객체를 이용하여 request body로 들어온 json 값을 파싱함
body (key=entry)로부터 값을 불러온 뒤 ret 객체를 생성함
headers의 key: value가 authen=pass인 경우 reponse_entity_type에 '1000'과 ret을 입력함
headers의 key: value가 authen=pass가 아닌 경우 reponse_entity_type에 '1990'과 ret을 입력함
'1000'은 'message':'SUCCESS'를 의미하며, '1990'은 'message':'FAILURE'를 의미함
"""

from flask_restful import Resource
from common.response import response_entity_type
from service.service_inp import Service

from flask import request
import json


class PWAA(Resource):

    def post(self):
        tmp = Service(request.get_json())
        ret = tmp.inp()

        if request.headers.get('authorization') == 'nm00213':
            return response_entity_type('1000', ret)
        else:
            return response_entity_type('1990', ret)

        # if request.headers.get('authen') == 'pass':
        #     return response_entity_type('1000', ret)
        # else:
        #     return response_entity_type('1990', ret)

        # temp = request.get_json()
        # print(temp['title'])
        # print(temp['desc'])
        # print(type(temp))

        # print(request.headers, type(request.headers))

        # if request.headers.get('authorization') == 'nm00213':
        #     return json.dumps({'a': 'Hello~', 'b': 'bye~'})
        # else:
        #     return json.dumps({'a': 'no', 'b': 'accept'})

        # outp = json.dumps({'a': 'Hello~', 'b': 'bye~'})
        # return outp
