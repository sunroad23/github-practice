"""
response_body를 통해 출력되는 responseStatus를 결정함
key:value가 "code":"message" 형태로 구성함
클라이언트(7290, 7291, 7390) 이해가 필요함
"""

response_status = {
    # 공통
    "1000": {"code": 1000, "message": "SUCCESS"},
    "1990": {"code": 1990, "message": "FAILURE"},
    # 클라이언트
    "7290": {"code": 7290, "message": "CLIENT_NOT_VERIFIED"},
    "7291": {"code": 7291, "message": "CLIENT_NOT_VERIFIED_SERVICEKEY"},
    "7390": {"code": 7390, "message": "INVALID_CLIENT"}
}
