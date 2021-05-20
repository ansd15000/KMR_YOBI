from flask import Flask, request, jsonify # 서버 구현을 위한 Flask 객체 import
from flask_restx import Api, Resource     # Api 구현을 위한 Api 객체 import. reqparse는 인자값 타입 체크
from utils import getMethod               # 웹, 어플의 post 요청 형태에 따른 맞춤함수
import timeit                             # 로직 실행시간 체크용

app = Flask(__name__)  # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
api = Api(app)         # Flask 객체에 Api 객체 등록

# ========= 회원정보 컨테이너 ===============================
from models import users as user

# 회원 아이디 중복여부
@api.route('/user_overlap')
class Overlap(Resource):
    def post(self):
        a = getMethod(request)
        result = user.overlap(a['user_id'])
        return jsonify(result)

# 회원 로그인
@api.route('/user_login')
class Login(Resource):
    def post(self):
        a = getMethod(request)
        res = user.login(a['user_id'], a['user_pw'])
        return jsonify(res)

# 회원 정보 가입, 수정, 조회
@api.route('/user')
class User(Resource):
    # 유저정보 조회
    def get(self):
        data = request.args
        res = user.getUserInfo(data.get('user_id'), data.get('user_pw'))
        return jsonify(res)
    
    # 회원가입
    def post(self):
        a = getMethod(request.data.decode('utf-8'))
        print(a)
        result = user.sign_up(a['user_id'], a['user_name'], a['user_pw'], a['userInfo'])
        return jsonify(result)

    # 회원정보 수정
    def put(self):
        # a = request.get_json()
        a = getMethod(request)
        result = user.updateUser(a['user_id'], a['user_pw'], a['userInfo'])
        return jsonify(result)


# ========= 컨테이너요청으로 사용 예정 없음 ==================================
# from models import createTable as ct
# @api.route('/createTable')
# class CreateTable(Resource):
#     def get(self):
#         data = dict(request.args)
#         result = None
#         if 'sortKey' in data.keys():
#             result = ct.craeteTable(data['tablename'], data['partitionKey'], data['sortKey'])
#         else:
#             result = ct.craeteTable(data['tablename'], data['partitionKey'])
        
#         return jsonify(result)

# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0', port=80)