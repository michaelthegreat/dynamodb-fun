import boto3

def read_test_item():

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test_dynamo_table')

    # Write an item with a String Set
    try:
        table.put_item(
            Item={
                'test_key': 'key_1',
                'value': set(['A', 'B', 'C'])  # Use a Python set for DynamoDB String Set
            }
        )
    except Exception as e:
        print(f"Error writing item: {e}")
    # Retrieve it
    response = table.get_item(Key={'test_key': 'key_1'})
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