"""
'route'라는 이름의 blueprint를 route 객체로 생성함
blueprint 객체에 Api 객체를 등록함
api 객체에 '/1.1/pwaa' 경로를 라우팅(=경로를 선택함)하고 PWAA 함수를 매핑(하나의 값을 다른 값으로 대응시킴)함
"""

from flask import Blueprint
from flask_restful import Api
from resources.pwaa import PWAA

route = Blueprint('route', __name__)

api = Api(route)
# url = /version/pwaa
api.add_resource(PWAA, '/1.1/pwaa')
