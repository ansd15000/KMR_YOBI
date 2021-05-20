# createTable.py

import boto3
client = boto3.resource('dynamodb')
# table = client.Table('User')
def createTable(tablename, partitionKey, sortKey = None) :
    schema = [{
        'AttributeName': partitionKey,
        'KeyType': 'HASH'  # Partition key
    }]
    attr = [{
        'AttributeName': partitionKey,
        'AttributeType': 'S' # S:string N:number B: binary
    }]
    if sortKey is not None :
        schema.append({
            'AttributeName': sortKey,
            'KeyType': 'RANGE'  # Partition key
        })
        attr.append({
            'AttributeName': sortKey,
            'AttributeType': 'S'
        })
    table = client.create_table(
        TableName= tablename,
        KeySchema = schema,
        AttributeDefinitions = attr,
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

if __name__ == '__main__':
    # a = createTable('test_ingredient', 'ingredient')
    # a = createTable('recipe', 'name')
    a = createTable('user', 'user_id', 'user_pw')
    print(a.table_status)

