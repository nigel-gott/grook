from time import sleep

import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

def recreate():
    make_chapters()
    make_sentences()

def make_sentences():
    # proposed_sentences = dynamodb.Table('proposed_sentences')
    # proposed_sentences.delete()
    sleep(5)
    table = dynamodb.create_table(
        TableName='proposed_sentences',
        KeySchema=[
            {
                'AttributeName': 'book_name',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'proposed_time',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'book_name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'proposed_time',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        }
    )


def make_chapters():
    chapters = dynamodb.Table('chapters')
    chapters.delete()
    sleep(5)
    table = dynamodb.create_table(
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


if __name__ == '__main__':
    recreate()