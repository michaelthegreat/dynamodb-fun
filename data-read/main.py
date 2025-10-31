import boto3

def read_test_item():
    test_table1 = "test_dynamo_table"
    test_table2 =  "MyTable"
    table_name = test_table2
    dynamodb = boto3.resource('dynamodb')
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

def main():
    read_test_item()


# Using the special variable 
# __name__
if __name__=="__main__":
    main()