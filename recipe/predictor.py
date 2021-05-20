from flask import Flask, request, jsonify # 서버 구현을 위한 Flask 객체 import
from flask_restx import Api, Resource     # Api 구현을 위한 Api 객체 import. reqparse는 인자값 타입 체크
from utils import getMethod               # 웹, 어플의 post 요청 형태에 따른 맞춤함수
import timeit                             # 로직 실행시간 체크용

app = Flask(__name__)  # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
api = Api(app)         # Flask 객체에 Api 객체 등록

# ========= 레시피 컨테이너 ==================================
from models import container_recipe as recipe

# 추천 레시피 반환
# 인자값에 유저아이디가 있다면 인식된 재료들 그대로 사용자 재료 테이블에 추가하기
@api.route('/recipe')
class Recipe(Resource):
    # 전체 재료 하나, 주 재료 하나 받아올예정 
    def post(self):
        codestart = timeit.default_timer()
        a = getMethod(request)
        result = {"success": True}

        # 띄어쓰기 기준 문자열 반환된 주재료 데이터
        grocery_list = a['grocery_list'].split(' ') # 인식된 전체 재료
        main_list    = a['main_list'].split(' ')    # 유저가 선택한 주 재료
        if '달걀' in main_list : main_list.append('계란') # 모델이 달걀만 인식하는 문제로 같은재료인 계란도 검색할수 있도록 수동으로 값 추가
        if '달걀' in grocery_list : grocery_list.append('계란')
        elif '계란' in grocery_list : grocery_list.append('달걀')

        print('==== grocery_list ====')
        print(grocery_list) # 전체 재료
        print('==== main_list ====')
        print(main_list)

        # 병건이형 코드
        scores = {i : 1 for i in grocery_list} # 전체 재료
        recipeNames = recipe.searchMainRecipeNames(main_list, scores)
        recipes = recipe.batchGetItem(recipeNames)

        # 성한이 코드, 메인재료 2개이하를 권장한대. 요청은 최대 1.3초 미만
        # recipes = recipe2.getRecipe(main_list, grocery_list)

        #  전달해줄 값 [ {} {} ]
        result['recipe_list'] = recipes
        print(f'메인코드 처리시간: {timeit.default_timer() - codestart : 0.3f} 초')
        return jsonify(result)

# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0', port=5001)