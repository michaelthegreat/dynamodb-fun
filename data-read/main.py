import boto3
from boto3.dynamodb.conditions import Key,Attr
from pydantic import BaseModel
from typing import List
import json

def read_test_item():
    test_table1 = "test_dynamo_table"
    test_table2 =  "MyTable"
    table_name = test_table2
    dynamodb = boto3.resource('dynamodb')
    # here you can change the table you reading
    table = dynamodb.Table(test_table2)

    # Write an item with a String Set
    try:
        if table_name == test_table1:
            table.put_item(
                Item={
                    'test_key': 'key_1',
                    'value': set(['A', 'B', 'C'])  # Use a Python set for DynamoDB String Set
                }
            )
    except Exception as e:
        print(f"Error writing item: {e}")
    # Retrieve it
    if table_name == test_table1:
        response = table.get_item(Key={'test_key': 'key_1'})
    else:
        response = table.get_item(Key={'i_type': 'test-type', 'i_name': 'test-name'})
    print("***********************")
    print("response: ", response)
    print("***********************")
    print("response['Item']: ", response.get('Item', 'No item found'))
    print("***********************")
    print("response['Item']['i_value']", response['Item']['i_value'])

def query_dynamodb_pagable(
    region_name='us-east-1',
    table_name=None,
    index_name=None,
    condition=None,
    filter_condition=None,
    last_evaluated_key=None,
    page_size=None,
    projection_expression=None
):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        if filter_condition and index_name:
            kwargs = {
                'IndexName': index_name,
                'KeyConditionExpression': condition,
                'FilterExpression': filter_condition
            }
        elif index_name:
            kwargs = {
                'IndexName': index_name,
                'KeyConditionExpression': condition
            }
        elif filter_condition:
            kwargs = {
                'FilterExpression': filter_condition,
                'KeyConditionExpression': condition
            }
        else:
            kwargs = {
                'KeyConditionExpression': condition
            }

        if projection_expression:
            kwargs['ProjectionExpression'] = projection_expression

        if page_size:
            kwargs['Limit'] = int(page_size)
        if last_evaluated_key:
            response = table.query(ExclusiveStartKey=last_evaluated_key, **kwargs)
        else:
            response = table.query(**kwargs)
        return response
    except Exception as e:
        print(f"Error querying items: {e}")

def query_dynamodb_all_pages(
    region_name='us-east-1',
    table_name=None,
    index_name=None,
    condition=None,
    filter_condition=None,
    projection_expression=None
):
    all_items = []
    response = query_dynamodb_pagable(
        region_name=region_name,
        table_name=table_name,
        index_name=index_name,
        condition=condition,
        filter_condition=filter_condition,
        projection_expression=projection_expression
    )
    if "Items" in response:
        all_items.extend(response["Items"])
    while response.get("LastEvaluatedKey"):
        response = query_dynamodb_pagable(
            region_name=region_name,
            table_name=table_name,
            index_name=index_name,
            condition=condition,
            filter_condition=filter_condition,
            last_evaluated_key=response.get("LastEvaluatedKey"),
            projection_expression=projection_expression
        )
        if "Items" in response:
            all_items.extend(response["Items"])
    return all_items

def get_item_by_type(
    i_type, name="", is_active = None
):
    condition = Key("i_type").eq(i_type)
    filter_condition = None
    if isinstance(is_active, bool):
        filter_condition = (
            Attr("is_active").eq("True") if is_active else Attr("is_active").ne("True")
        )
    if name:
        condition = condition & Key("i_name").eq(name)
    if filter_condition:
        results = query_dynamodb_all_pages(
            table_name="MyTable",
            region_name="us-east-1",
            condition=condition,
            filter_condition=filter_condition
        )
    else:
        results = query_dynamodb_all_pages(
            table_name="MyTable",
            region_name="us-east-1",
            condition=condition
        )
    if not results:
        return []
    return results

class testClass(BaseModel):
    class_id: int
    class_name: str

class TestParsedRecord(BaseModel):
    record_id: int
    attribute1: str
    class_list: List[testClass]

def insert_test_item_with_model():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test_cached_item_table')
    test_record = TestParsedRecord.parse_obj({
        'record_id': 1,
        'attribute1': "Sample Attribute",
        'class_list': [
            testClass(class_id=101, class_name="Class A"),
            testClass(class_id=102, class_name="Class B")
        ]
    })
    table.put_item(
        Item={
            'test_key': 'item_1',
            'i_value': test_record.model_dump_json()
        }
    )

def get_item_with_model():
    # read items from test_cached_item_table with test_key = 'item_1'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test_cached_item_table')
    item = table.get_item(Key={'test_key': 'item_1'})['Item']
    i_value = item['i_value']
    print("i_value: ", i_value)
    print("type of i_value: ", type(i_value))
    parsed_record = TestParsedRecord.model_validate(json.loads(i_value))
    print("Parsed Record: ", parsed_record)
    return parsed_record

READ_ITEM_WITH_MODEL = True

def main():
    if READ_ITEM_WITH_MODEL:
        print("Inserting test item with model...")
        insert_test_item_with_model()
        print("Getting item with model...")
        get_item_with_model()
        return
    print("Starting data read...")
    print("read_test_item()")
    read_test_item()
    print("----------------")
    print("get_item_by_type('test-type', 'test-name')")
    items = get_item_by_type('test-type', 'test-name')
    print("items: ", items)

# Using the special variable 
# __name__
if __name__=="__main__":
    main()