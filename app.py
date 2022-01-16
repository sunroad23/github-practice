"""
app이라는 이름의 Flask 웹 어플리케이션 객체를 생성함
CORS(Cross Origin Resource Sharing) 설정: 동일 출처(같은 호스트네임)가 아니더라도 api 등의 리소스 호출을 정상적으로 가능하게 함
app이라는 Flask에 route라는 blueprint를 등록함
port값 설정을 위한 if문 작성
app 실행: host='0.0.0.0'을 통해 모든 IP에 대한 접근을 허용함(미기재시 localhost(=127.0.0.1)에서만 접근 가능)
"""

import os
import sys
from flask import Flask
from flask_cors import CORS
from route import route

app = Flask(__name__)
CORS(app)

app.register_blueprint(route)

if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 5000

if "FLASK_PRODUCTION" not in os.environ and __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=port)
