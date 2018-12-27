import boto3
from flask import Flask

# boto3 is the AWS SDK library for Python.
# We can use the low-level client to make API calls to DynamoDB.

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def hello():
        chapters = dynamodb.Table('chapters')
        return '\n'.join(
            '<h2> Chapter {number} : {title} </h2> <p> {contents} </p>'.format(**item)
            for item in chapters.scan()['Items']
        )

    return app


if __name__ == '__main__':
    app = create_app()
