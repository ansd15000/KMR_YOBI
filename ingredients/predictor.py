from flask import Flask, request, jsonify # 서버 구현을 위한 Flask 객체 import
from flask_restx import Api, Resource     # Api 구현을 위한 Api 객체 import. reqparse는 인자값 타입 체크
from utils import getMethod               # 웹, 어플의 post 요청 형태에 따른 맞춤함수
import timeit                             # 로직 실행시간 체크용

app = Flask(__name__)  # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
api = Api(app)         # Flask 객체에 Api 객체 등록

# ========= 재료 컨테이너 ==================================
from models import ingredient as ingre

# 재료 정보 조회 추가 수정 삭제
@api.route('/ingredient')
class Ingredient(Resource): 
    def get(self):
        data = dict(request.args)
        ingredient = data['ingredient']
        res = ingre.get_Ingredient(ingredient)
        return jsonify(res)

    # 재료 입력
    def post(self):
        # a = request.get_json()
        a = getMethod(request)
        res = ingre.put_Ingredient(a['ingredient'], a['calorie'], a['shelf_life'])
        return jsonify(res)

    # 재료 수정
    def put(self):
        # a = request.get_json()
        a = getMethod(request)
        calorie, shelf_life = None, None
        for k, v in a.items():
            if k == 'calorie':
                calorie = v
            elif k == 'shelf_life':
                shelf_life = v
            continue
        res = ingre.update_Ingredient(a['ingredient'], calorie = calorie, shelf_life = shelf_life)
        return jsonify(res)

    # 재료 삭제. (소지한 유저 데이터도 삭제됨)
    def delete(self):
        # a = request.get_json()
        a = getMethod(request)
        res = ingre.delete_Ingredient(a['ingredient'])
        return jsonify(res)

@api.route('/ingredient_all')
class Ingredient_all(Resource):
    def post(self):
        res = ingre.get_Ingredient_all()
        return jsonify(res)

# 재료 있는지 체크
@api.route('/ingredient_user_chk')
class Ingredient_user_chk(Resource):
    def post(self):
        a = getMethod(request)
        ingredient = a['ingredient']
        res = ingre.get_Ingredient(ingredient)
        if res['result'] != False : 
            res['result'] = True
        print(res)
        return res

# 사용자의 특정 재료 검색 추가 수정 삭제 
@api.route('/ingredient_user')
class Ingredient_user(Resource): 
    def get(self):
        data = dict(request.args)
        user_id, ingredient = data['user_id'], data['ingredient']
        res = ingre.get_userIngredient(user_id, ingredient)
        return jsonify(res)

    # 사용자 재료 추가
    def post(self):
        # a = request.get_json()
        a = getMethod(request)
        res = ingre.put_userIngredient(a['user_id'], a['ingredient'])
        return jsonify(res)

    # 사용자 재료 수정
    # 받아오는 값: 유저아이디, 추가/삭제할 재료명(띄어쓰기 구분 문자열)
    # add, delete 둘 중 값이 없는 경우도 있어야함
    def put(self):
        a = getMethod(request)
        add_Ingredients = a['add'].split(" ") if a['add'] else None
        delete_Ingredients = a['delete'].split(" ") if a['delete'] else None
        print(f'add_Ingredients: {add_Ingredients}')
        print(f'delete_Ingredients: {delete_Ingredients}')
        
        res = ingre.update_userIngredient(a['user_id'], add_Ingredients, delete_Ingredients)
        res['success'] = True
        print(res)
        return jsonify(res)

    def delete(self):
        # a = request.get_json()
        a = getMethod(request)
        res = ingre.delete_userIngredient(a['userId'], a['ingredient'])
        return jsonify(res)

# 사용자 전체 재료 반환
@api.route('/ingredient_user_all')
class Ingredient_user_all(Resource):
    def post(self):
        a = getMethod(request)
        user_id = a['user_id']
        res = ingre.get_UserIngredient_all(user_id)
        res['success'] = True
        print(res)
        return jsonify(res)

