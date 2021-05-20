import boto3, timeit
from pprint import pprint
from soynlp.tokenizer import MaxScoreTokenizer
import pandas as pd
from numpy import dot
from numpy.linalg import norm

client = boto3.resource('dynamodb')
table = client.Table('recipe')

def __get_recipesAll():
    codestart = timeit.default_timer()
    last_evaluated_key = None # 다이나모 디비 페이징 체크를 위한 값
    results = list()       # 조건에따라 스캔한 디비값을 담는 리스트

    while True:
        if last_evaluated_key:
            response = table.scan(
                ExclusiveStartKey=last_evaluated_key,
                AttributesToGet=['name', 'ingredient'],
                Limit = 100
            )
        else: 
            response = table.scan( 
                AttributesToGet=['name', 'ingredient'],
                Limit = 100
            )
        last_evaluated_key = response.get('LastEvaluatedKey')
        results.extend(response['Items'])

        if not last_evaluated_key:
            break

    print(len(results))
    # result = { i : v for i, v in enumerate(results)} # print(a[824]['ingredient'])
    # pprint(result)
    # result = {i['sortkey'] : int(i['ingredientInfo']['shelf_life']) for i in results}
    print(f'실행 완료시간: {timeit.default_timer() - codestart : 0.3f} 초')
    return results

# 디비 데이터 전처리, 
# 파라메터는 dict 이며, 여러 재료와 개수를 키벨류로 받지만 개수는 일단 1로 고정되있어야 함
def __data_pretreatment(scores):
    dbData = __get_recipesAll() # [ {}, {} ]

    # 클라이언트에서 인식된 전체 재료
    # scores = {'감자':1, '대파':1, '마늘':1, '돼지고기':1, '양파':1}
    df = pd.DataFrame(scores, index=['재료'])

    tokenizer = MaxScoreTokenizer(scores=scores)

    food_json = {i['name'] : i['ingredient'] for i in dbData} # 리스트들 꺼내오기
    list_ing = list(food_json.values())                  # 재료들만 리스트로
    sum_ing = [''.join(i) for i in list_ing]             # 각 레시피의 재료들을 문자열로변환
    sum_ing2 = [ tokenizer.tokenize(i) for i in sum_ing] # 토크나이징 한 재료리스트

    food_list = []
    for i in range(len(sum_ing2)):
        line=[]
        for key in scores:
            if key in sum_ing2[i]:
                line.append(1)
            else:
                line.append(0)
        food_list.append(line)

    for i , key in enumerate(food_json):
        key = key.replace(" ","")
        df.loc[key] = food_list[i]
    print(df)
    return df

# 코사인 유사도
def __cos_sim(A,B):
    return dot(A,B)/(norm(A)*norm(B))

# 주재료 선정. 주재료는 클라이언트단에서 최대 3개만 받아온다.
def searchMainRecipeNames(main, scores):
    if len(main) >= 4 : raise '너무 많은 주재료 개수!'

    df =__data_pretreatment(scores)
    sim, a = dict(), list()
    not_main = df.drop(main, axis=1)
    
    # 주재료 최대 3개 가능. 개수에 따라 순서대로 가중치 70 / 60 / 50
    w = [0.5, 0.3, 0.23]
    main_cnt = len(main)
    w1 = w[main_cnt - 1]
    w2 = ( 1 - (w1 * main_cnt) ) / ( len(df.columns) - main_cnt )   # 부재료 가중치
    main_food = pd.DataFrame(df[main][0:]*w1)
    not_main = not_main.iloc[:,:]*w2
    df = pd.concat([not_main,main_food], axis=1)
    
    for i in range(len(df)):
        b=df.values[i,0:]
        a.append(b)

    for i in range(len(df)):
        if i==0: continue
        sim[df.index[i]] = __cos_sim(a[0],a[i])
    df=pd.DataFrame(sim,index= ['코사인유사도'])
    df=df.T
        
    rec=df.sort_values('코사인유사도',ascending=False).head(10)
    # for i in range(len(rec)):
    #     print([i+1], rec.index[i], ':' , round(rec['코사인유사도'][i]*100, 2),'%')
    
    __result = rec.to_dict()['코사인유사도']
    result = list(__result.keys())
    return result

# searchMainRecipeNames(['참치', '김치', '계란'], {'계란':1, '참치':1, '김치':1, '양파':1, '감자':1})

# 주재료 하나만 인식되던 가중치 기반 코드
# def searchMainRecipeNames(main, scores):
#     df =__data_pretreatment(scores)
#     sim, a = dict(), list()
#     not_main = df.drop([main], axis=1)

#     if main in df.columns:
#         w1 = 0.5
#         w2 = 0.5/(len(df.columns)-1)
#         main=pd.DataFrame(df[main][0:]*w1)
#         not_main = not_main.iloc[:,:]*w2
#         df = pd.concat([not_main,main], axis=1)

#     for i in range(len(df)):
#         b=df.values[i,0:]
#         a.append(b)

#     for i in range(len(df)):
#         if i==0:
#             continue
#         sim[df.index[i]] = __cos_sim(a[0],a[i])
#     df=pd.DataFrame(sim,index= ['코사인유사도'])
#     df=df.T
#     # # #     print(data.index[i],":",__cos_sim(a[0],a[i]))    
#     rec=df.sort_values('코사인유사도',ascending=False).head(10)
#     # for i in range(len(rec)):
#     #     print([i+1], rec.index[i], ':' , round(rec['코사인유사도'][i]*100, 3),'%')

#     __result = rec.to_dict()['코사인유사도']
#     result = list(__result.keys())
#     return result

# 다이나모디비 배치검색. 잘쓰면 외래키 검색처럼 쓸 수 있을듯
# 마찬가지로 많은 데이터를 읽어올 경우 페이징 처리를 하는 값을 설정해줘야함
def batchGetItem(recipeNames):
    # recipeNames = searchMainRecipeNames(main, scores)
    print(recipeNames)
    keys = [{'name' : i} for i in recipeNames]
    print('====================')
    # print(keys)
    res = client.batch_get_item(
        RequestItems = {
            'recipe': {
                'Keys': keys ,
                'ConsistentRead': True, # 일관된 읽기가 뭐지
            }            
        },
        ReturnConsumedCapacity='TOTAL' # 이거 뭐지
    )
    # print(res['Responses']['recipe'])
    return res['Responses']['recipe']

# mainIngre('감자', {'감자':1, '대파':1, '마늘':1, '돼지고기':1, '양파':1})
# a= searchMainRecipeNames('양파', {'감자':1, '대파':1, '마늘':1, '돼지고기':1, '양파':1})
# print('==========================')
# print('병건이형 유사도')
# print(a)
# batchGetItem(a)