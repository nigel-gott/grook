from flask import url_for


def test_app2(client):
    response = client.get(url_for('index'))
    assert response.status_code == 200



def test_app(client, dynamodb):
    resource = dynamodb[1]
    table = resource.create_table(
        TableName='chapters',
        KeySchema=[
            {
                'AttributeName': 'book_name',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'chapter_number',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'book_name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'chapter_number',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        }
    )
    table.put_item(Item={'book_name': 'The Book', 'chapter_number': 1, 'title': 'My Title', 'contents': 'Something'})
    response = client.get(url_for('index'))
    assert response.status_code == 200
    assert response.data.decode('utf-8') == '<h2> Chapter 1 : My Title </h2> <p> Something </p>'
