import datetime
from time import sleep

import boto3
from boto3.dynamodb.conditions import Key
from flask import Flask, render_template, url_for, request
from werkzeug.utils import redirect


def delete_sentences():
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    dynamodb_client = boto3.client('dynamodb', region_name='eu-west-1')

    proposed_sentences = dynamodb.Table('proposed_sentences')
    proposed_sentences.delete()
    while 'proposed_sentences' in dynamodb_client.list_tables()['TableNames']:
        print('Waiting for chapters to be deleted!')
        sleep(1)
    create_table()


def create_table():
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    dynamodb.create_table(
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


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        chapters_table = dynamodb.Table('chapters')
        sentences_table = dynamodb.Table('proposed_sentences')
        chapters = chapters_table.query(KeyConditionExpression=Key('book_name').eq('main'))['Items']
        for i in range(10):
            try:
                sentences = sentences_table.scan()['Items']
            except Exception:
                sleep(1)
                pass
        return render_template('index.html', chapters=chapters, sentences=sentences)

    @app.route("/trigger", methods=['POST'])
    def trigger():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        chapters_table = dynamodb.Table('chapters')
        sentences_table = dynamodb.Table('proposed_sentences')
        chapters = chapters_table.query(KeyConditionExpression=Key('book_name').eq('main'), ScanIndexForward=False)[
            'Items']
        sentences = sentences_table.scan()['Items']
        if sentences:
            best = sentences[0]
            for sentence in sentences:
                if sentence['votes'] > best['votes']:
                    best = sentence

            if chapters:
                latest = chapters[0]
                latest['contents'] = latest['contents'] + best['sentence']
            else:
                latest = {
                    'book_name': 'main',
                    'chapter_number': 1,
                    'title': 'The Start',
                    'contents': best['sentence']
                }

            chapters_table.put_item(Item=latest)

            if len(latest['contents']) > 1000:
                next_chapter_number = latest['chapter_number'] + 1
                latest = {
                    'book_name': 'main',
                    'chapter_number': next_chapter_number,
                    'title': 'Chapter ' + str(next_chapter_number),
                    'contents': ' '
                }

                chapters_table.put_item(Item=latest)

            delete_sentences()

        return redirect(url_for('index'))

    @app.route("/add", methods=['POST'])
    def add():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        sentences_table = dynamodb.Table('proposed_sentences')

        proposed_time = datetime.datetime.now().strftime("%Y:%m:%dT%H:%M:%S:%f")

        sentences_table.put_item(Item={
            'book_name': 'main',
            'proposed_time': proposed_time,
            'votes': 0,
            'sentence': request.form['sentence']
        })

        return redirect(url_for('index'))

    @app.route("/vote/<proposed_time>", methods=['POST'])
    def vote(proposed_time):
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        sentences_table = dynamodb.Table('proposed_sentences')
        sentence = sentences_table.get_item(Key={'proposed_time': proposed_time, 'book_name': 'main'})['Item']
        sentences_table.put_item(Item={
            'proposed_time': proposed_time,
            'book_name': 'main',
            'votes': sentence['votes'] + 1,
            'sentence': sentence['sentence']
        })

        return redirect(url_for('index'))

    return app


if __name__ == '__main__':
    app = create_app()
