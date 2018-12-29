import time
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from flask import Flask, render_template, url_for, request
from werkzeug.utils import redirect


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        chapters_table = dynamodb.Table('chapters')
        triggers = dynamodb.Table('triggers')
        try:
            last_trigger = triggers.get_item(Key={'key': 'latest'})['Item']
        except Exception:
            print("use zero why")
            last_trigger = {
                'key': 'latest',
                'time': Decimal(0)
            }
        sentences_table = dynamodb.Table('proposed_sentences')
        sentences = sentences_table.query(
            KeyConditionExpression=Key('proposed_time').gt(last_trigger['time']) & Key('book_name').eq('main'))[
            'Items']
        print(sentences)
        print(last_trigger)
        chapters = chapters_table.query(KeyConditionExpression=Key('book_name').eq('main'))['Items']
        return render_template('index.html', chapters=chapters, sentences=sentences)

    @app.route("/trigger", methods=['POST'])
    def trigger():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        chapters_table = dynamodb.Table('chapters')
        triggers = dynamodb.Table('triggers')
        try:
            last_trigger = triggers.get_item(Key={'key': 'latest'})['Item']
        except Exception:
            last_trigger = {
                'key': 'latest',
                'time': Decimal(0)
            }
        sentences_table = dynamodb.Table('proposed_sentences')
        sentences = sentences_table.query(
            KeyConditionExpression=Key('proposed_time').gt(last_trigger['time']) & Key('book_name').eq('main'))[
            'Items']
        last_trigger['time'] = int(time.time())
        triggers.put_item(Item=last_trigger)

        chapters = chapters_table.query(KeyConditionExpression=Key('book_name').eq('main'), ScanIndexForward=False)[
            'Items']
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

        return redirect(url_for('index'))

    @app.route("/add", methods=['POST'])
    def add():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        sentences_table = dynamodb.Table('proposed_sentences')

        proposed_time = int(time.time())

        ttl = proposed_time + 60 * 30
        sentences_table.put_item(Item={
            'book_name': 'main',
            'proposed_time': Decimal(proposed_time),
            'ttl': Decimal(ttl),
            'votes': 0,
            'sentence': request.form['sentence']
        })

        return redirect(url_for('index'))

    @app.route("/vote/<proposed_time>", methods=['POST'])
    def vote(proposed_time):
        decimal_proposed_time = Decimal(proposed_time)
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        sentences_table = dynamodb.Table('proposed_sentences')
        sentence = sentences_table.get_item(Key={'proposed_time': decimal_proposed_time, 'book_name': 'main'})['Item']
        sentences_table.put_item(Item={
            'proposed_time': decimal_proposed_time,
            'book_name': 'main',
            'votes': sentence['votes'] + 1,
            'sentence': sentence['sentence']
        })

        return redirect(url_for('index'))

    return app


if __name__ == '__main__':
    app = create_app()
