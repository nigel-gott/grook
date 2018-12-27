from flask import url_for


def test_app(client, dynamodb):
    resource = dynamodb[1]
    table = resource.create_table(
        TableName='chapters',
        KeySchema=[
            {
                'AttributeName': 'number',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'number',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        }
    )
    table.put_item(Item={'number': 1, 'title': 'My Title', 'contents': 'Something'})
    response = client.get(url_for('hello'))
    assert response.status_code == 200
    assert response.data.decode('utf-8') == '<h2> Chapter 1 : My Title </h2> <p> Something </p>'
