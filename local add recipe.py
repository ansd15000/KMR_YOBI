# table_test.py
import boto3
from pprint import pprint
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from createTable import createTable
import time
import json
import os

client = boto3.resource('dynamodb')
table = client.Table('recipe')

# data는 전부 json타입으로 받아와서 하기로 하자
def batchWrite():
    path = './food list'
    with table.batch_writer() as batch:
        for i in os.listdir(path):
            if i == '.DS_Store' : continue
            print(i)
            with open(path + '/' + i, 'r') as f:
                jsondata = json.load(f)
                keys = jsondata.keys()
                data = { i : (jsondata[i].replace(" ", "") if i == 'name' else jsondata[i]) for i in keys }
                batch.put_item( Item = data )
                
    print('done')

def get_TableInfo():
    client = boto3.client('dynamodb')
    res = client.describe_table(TableName = 'recipe')
    pprint(res)

def get_recipes() :
    res = table.query (
        KeyConditionExpression=Key('name').eq('양배추사과샌드위치')
    )
    pprint(res)

def renameJsondata():
    path = '/root/food list'
    for i in os.listdir(path):
        if i == '.DS_Store' : continue

        cut = i.rfind('.')
        name = i[:cut].replace(' ', '')
        with open(path + '/' + i, 'r', encoding='UTF-8') as f:
            jsondata = json.load(f)
        jsondata['name'] = name
        
        with open(path + '/' + i, 'w') as f2:
            jsondata2 = json.dumps(jsondata, ensure_ascii=False)
            f2.write(jsondata2)
    print('done')

if __name__ == '__main__':
    # createTable('recipe', 'name')
    # renameJsondata()
    batchWrite()
    # get_recipes()
