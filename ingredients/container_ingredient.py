import boto3, json, time, timeit
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from utils import getFreshLevel
from pprint import pprint 

client = boto3.resource('dynamodb')
table = client.Table('YOBI')
ok = {"success": True}
no = {"success": False}

############### 공통함수 ##################

# 항목 여러개 추가, # 파라메터 타입: 리스트
def __batchWriter(data):
    with table.batch_writer() as batch:
        for item in data:
            batch.put_item( Item= item )
    print('batchWrite Done!')

# 데이터 여러개 삭제 # 파라메터 타입: 리스트
def __batchDeleter(keys):
    with table.batch_writer() as batch:
        for key in keys:
            batch.delete_item(Key=key)
    print('batchDelete Done!')

############### 재고 테이블 ##################

def __ingreKey(key):
    return {'PK': 'INGREDIENT', 'SK' : 'INGREDIENT#' + key}

####### 세컨더리 인덱스가 먼저 추가되어 있어야함. #######
# 재료 이름을 받아와 재료를 소유한 사람의 정보와, 재료 정보를 반환한다.
# 해당 재료를 가진 모든 유저들의 정보까지 업댓하기 위해서 혹은 
# 재료정보 삭제시 유저 정보까지 삭제할때 활용한다.
def getAboutIngre(ingre):
    while True:
        if not table.global_secondary_indexes or table.global_secondary_indexes[0]['IndexStatus'] != 'ACTIVE':
            print('Waiting for index to backfill...')
            time.sleep(5)
            table.reload()
        else:
            break

    res = table.query(
        IndexName = "ingredient",
        KeyConditionExpression=Key('SK').eq('INGREDIENT#' + ingre)
    )
    return res['Items']

# 재료 추가
def put_Ingredient(ingredient, calorie, shelf_life) :
    data = {
        "PK": "INGREDIENT",
        "SK": "INGREDIENT#" + ingredient,
        "calorie" : calorie,
        "shelf_life" : shelf_life,
        "ingredient": ingredient
    }
    res = table.put_item( Item = data )
    print('재료추가!')
    return ok

# 재료 정보조회
def get_Ingredient(ingredient) :
    res = table.get_item( Key = __ingreKey(ingredient) )
    # 재료와 유통기한 반환
    if 'Item' in res.keys():
        return {
            'success': True,
            'ingredient': res['Item']['ingredient'],
            'shelf_life': res['Item']['shelf_life'],
            'calorie': res['Item']['calorie']
        }
    return no
        
# 재료정보 업데이트, calorie, shelf_life
def update_Ingredient(ingredient, **kwargs) :
    try:
        txt = ''
        values = dict()
        # key: calorie , value: 999
        for key, value in kwargs.items():
            if value is None : continue
            if txt : txt += ', '
            txt += f'{key} = :{key}'
            values[f':{key}'] = value

        res = table.update_item(
            Key = __ingreKey(ingredient),
            UpdateExpression = 'set ' + txt,
            ExpressionAttributeValues = values,
            ReturnValues='UPDATED_NEW'
        )
        pprint(res)
        return ok
        
    except ClientError as e:
        pprint(e.response['Error']['Message'])
        return no 
        
# 재료정보 삭제. 
# 삭제된 재료를 가진 유저들의 데이터도 삭제된다.
def delete_Ingredient(ingredient) :
    keys = [{'PK':i['PK'], 'SK': i['SK']} for i in getAboutIngre(ingredient)]
    __batchDeleter(keys)
    return ok

# 모든 재료정보 반환
def get_Ingredient_all():
    res = table.query(
        KeyConditionExpression=Key('PK').eq('INGREDIENT') & Key('SK').begins_with('INGREDIENT#'),
    )
    result = list()
    for i in res['Items']:
        result.append( {
            i["ingredient"] : {
                "calorie" : i["calorie"],
                "shelf_life": i["shelf_life"]      
            }
        })
    return result
############### 사용자 재고 테이블 ##################

def __userIngreKey(pk, sk):
    return {'PK': 'USER#' + pk, 'SK' : 'INGREDIENT#' + sk}

# 다이나모디비 쿼리후 데이터 분할
# 이때 재고항목에 데이터가 없는경우 유저 재고항목의 신선도레벨 갱신시 제외됨
def __divElenment(user_id, result):
    users = list()
    for i in result:
        try:
            shelf_life = i['shelf_life']
            user = {
                'PK'         : 'USER#' + user_id,
                'SK'         : i['SK'],
                'shelf_life' : shelf_life,
                'freshness'  : getFreshLevel(shelf_life, shelf_life),
            }
            users.append(user)
        except :
            print(f"사용자 재고를 갱신할 {i['ingredient']} 가 없습니다.")
            continue
    
    return users

# 사용자의 모든 재고와 일반 재고 정보 불러와 freshness, shelf_life 갱신
def __add_aboutIngredients(user_id, ingredients):
    keys1 = [ __userIngreKey(user_id, ingre) for ingre in ingredients ]
    keys2 = [ __ingreKey(ingre) for ingre in ingredients ]
    keys = keys1 + keys2
    
    res = client.batch_get_item(
        RequestItems = {
            'YOBI': {
                'Keys': keys ,
                'ConsistentRead': True, # 일관된 읽기가 뭐지
            }            
        },
        ReturnConsumedCapacity='TOTAL' # 이거 뭐지
    )
    # 이거로 유통기한 체크하기
    result = res['Responses']['YOBI']
    users = __divElenment(user_id, result)
    __batchWriter(users)


# 사용자가 가진 모든 재료 조회
def get_UserIngredient_all(userid):
    # last_evaluated_key = None # 다이나모 디비 페이징 체크를 위한 값
    # returnData = list()       # 조건에따라 쿼리 디비값을 담는 리스트
    # # while True:
    #     if last_evaluated_key:
    #         response = table.query(
    #             KeyConditionExpression=Key('id').eq(userid),
    #             # ExclusiveStartKey=last_evaluated_key,
    #             # Limit=100, # 한번 스캔에 100개만
    #         )
    #     else: 
    #         response = table.query(
    #             KeyConditionExpression=Key('id').eq(userid),
    #             # Limit=100,                                    # 한번에 스캔할 데이터 갯수
    #         )
    #     last_evaluated_key = response.get('LastEvaluatedKey')
    #     returnData.extend(response['Items'])

    #     if not last_evaluated_key:
    #         break
    # return returnData
    # TypeError: Object of type Decimal is not JSON serializable // Werkzeug Debugger</title>
    res = table.query( 
        KeyConditionExpression=Key('PK').eq('USER#' + userid) & Key('SK').begins_with('INGREDIENT#')
    )
    result = {"result": res['Items']}
    return result


# 사용자가 가진 재료 정보 조회
def get_userIngredient(userid, ingredient):
    try :
        res = table.get_item(
            Key=__userIngreKey(userid, ingredient),
            AttributesToGet= ["freshness", "shelf_life"]
        )
        if 'Item' in res.keys() :
            print('있는재료')
            return { "success": True, "result" : res['Item'] }
        else :
            print(f'없는재료 {ingredient}')
            return { "success": True, "result" : False }
    except:
        return no
        
# 사용자의 소유 재료 항목 추가
def put_userIngredient(user_id, ingredient):
    shelf_life = get_Ingredient(ingredient)['shelf_life']
    data = {
        'PK': 'USER#' + user_id,
        'SK': 'INGREDIENT#' + ingredient,
        "freshness": getFreshLevel(shelf_life, shelf_life),
        "shelf_life": shelf_life,
    }
    res = table.put_item( Item = data)
    pprint(res)
    return ok

# 유저 재고정보 수정
# 유저아이디, 추가할 재료명, 삭제할 재료명
def update_userIngredient(user_id, add_ingredeints, delete_Ingredients) :
    if delete_Ingredients is not None :
        willDelete_Ingredients = [__userIngreKey(user_id, ingre) for ingre in delete_Ingredients]
        __batchDeleter(willDelete_Ingredients)
    if add_ingredeints is not None :
        __add_aboutIngredients(user_id, add_ingredeints)
    print('userIngredient Update!')
    return get_UserIngredient_all(user_id)

# 사용자가 가진 재료 삭제
def delete_userIngredient(userid, ingredient):
    try:
        table.delete_item( Key = __userIngreKey(userid, ingredient) )
        print(f'delete {ingredient}!')
        return ok
        
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
            return no
        else:
            raise


