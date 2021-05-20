# table_test.py
import boto3
from pprint import pprint
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import time

client = boto3.resource('dynamodb')
table = client.Table('YOBI')

def addSecondaryKey():
    try:
        resp = table.update(
            # 글로벌 세컨더리 인덱스를 사용해본적이 업으니 어떤것을 활용할지 해당 속성을 정의해주어야 한다
            AttributeDefinitions=[{
                "AttributeName": "SK", # SK의 ingredients# 로 시작하는 값들을 가져올 예정
                "AttributeType": "S"
            }],
            # This is where you add, update, or delete any global secondary indexes on your table.
            GlobalSecondaryIndexUpdates=[
                {
                    "Create": {
                        # 세컨더리 인덱스의 이름 지정. 쿼리시 해당 이름을 선언해주어야 함
                        "IndexName": "ingredient",
                        # Like the table itself, you need to specify the key schema for an index.
                        # For a global secondary index, you can use a simple or composite key schema.
                        "KeySchema": [{
                            "AttributeName": "SK",
                            "KeyType": "HASH"
                        }],
                        # You can choose to copy only specific attributes from the original item into the index.
                        # You might want to copy only a few attributes to save space.
                        "Projection": {
                            "ProjectionType": "ALL"
                        },
                        # Global secondary indexes have read and write capacity separate from the underlying table.
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 1,
                            "WriteCapacityUnits": 1,
                        }
                    }
                }
            ],
        )
        print("Secondary index added!")
        pprint(resp)
    except Exception as e:
        print("Error updating table:")
        print(e)

# addSecondaryKey()
def getItemBySecondaryKey():
    while True:
        if not table.global_secondary_indexes or table.global_secondary_indexes[0]['IndexStatus'] != 'ACTIVE':
            print('Waiting for index to backfill...')
            time.sleep(5)
            table.reload()
        else:
            break

    resp = table.query(
        IndexName = "ingredient",
        KeyConditionExpression=Key('SK').eq('INGREDIENT#감자')
        # res = table.get_item(Key={'id' : 'qwe', 'sortkey': sortkey })
    )

    print("The query returned the following items:")
    for item in resp['Items']:
        print(item)

getItemBySecondaryKey()