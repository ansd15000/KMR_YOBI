import boto3, hashlib, json
from boto3.dynamodb.conditions import Key
from pprint import pprint 

client = boto3.resource('dynamodb')
table = client.Table('YOBI')
ok = {"success": True}
no = {"success": False}

def __hash(pw):
    if str(type(pw)) == "<class 'int'>":
        pw = str(pw)
    return hashlib.sha256(pw.encode()).hexdigest()

def __key(user_id):
    return {'PK': 'USER#' + user_id, 'SK' : 'INFO#' + user_id}

# 로그인, 아이디 중복확인시 필요
def __isuser(user_id):
    res = table.get_item( # 단일값 반환시 이걸쓰자
        # KeyConditionExpression= Key('PK').eq('USER#' + user_id) & Key('SK').begins_with('INFO#'),
        Key = __key(user_id),
        AttributesToGet = ['user_pw']
    )
    return res

# 아이디 중복체크, 중복시 success False 반환
def overlap(userid):
    a = __isuser(userid)
    if "Item" in a.keys(): 
        print(f'overlap {userid}!')
        return no
    return ok

# 사용자 정보 반환.
def getUserInfo(user_id):
    try:
        res = table.get_item(
            Key= __key(user_id),
            AttributesToGet= ["user_name", "userInfo"], # 비슷한거로 ProjectionExpression 가 있음 
        )
        result = res['Item'] # 없을수도 있음
        pprint(result)
        return result
    except:
        return no

# 로그인
def login(user_id, user_pw):
    pw = __isuser(user_id)
    if pw['Item']['user_pw'] == __hash(user_pw): 
        return ok
    return no

# 회원가입
def sign_up(user_id, user_name, user_pw, userInfo):
    data = {
        'PK' : 'USER#' + user_id,
        'SK' : 'INFO#' + user_id,
        'user_pw' : __hash(user_pw),
        'user_name' : user_name,
        'userInfo' : json.loads(userInfo),
    }
    res = table.put_item( Item = data )
    pprint(res)
    print('회원가입 완료')
    return ok

# 회원정보 수정 (이름, 비밀번호 변경 가능)
def updateUser(user_id, user_pw, userInfo):
    isuser = login(user_id, user_pw)['success']
    print(isuser)
    if isuser: # 회원 확인 됐다면
        attr = ''
        values = dict()
        for k, v in userInfo.items():
            if k == 'user_pw':
                attr += f'{k} = :{k}, '
                values[f':{k}'] = __hash(v)
                continue
            elif k == 'user_name':
                attr += f'{k} = :{k}, '
                values[f':{k}'] = v
                continue

            attr += f'userInfo.{k} = :{k}, '
            values[f':{k}'] = v
            
        res = table.update_item(
            Key= __key(user_id),
            UpdateExpression = 'set ' + attr[:-2],
            ExpressionAttributeValues = values,
            ReturnValues='UPDATED_NEW'
        )
        pprint(res)
        return ok
    else:
        raise "INVALED USER"

# 회원탈퇴. 사용자 기본정보 및 재고정보까지 삭제.
# 삭제 키 조건엔 begins_with이 없어서 배치로 돌려야하는 불편함이 있음..
def deleteUser(user_id, user_pw):
    isuser = login(user_id, user_pw)['success']
    if isuser :
        res = table.query( KeyConditionExpression=Key('PK').eq('USER#' + user_id) )
        keys = [ {'PK' : i['PK'], 'SK': i['SK']} for i in res['Items'] ]
        with table.batch_writer() as batch:
            for key in keys:
                batch.delete_item( Key = key )
            return ok
    return no