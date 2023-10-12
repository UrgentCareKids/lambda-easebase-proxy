import boto3
import psycopg2
import json
from botocore.exceptions import ClientError

def get_secret():
    secret_name = "easebase/internal_datamovement"
    region_name = "us-east-2"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])
    return secret

def handler(event, context):
    secret = get_secret()

    try:
        # Use the secret to establish a database connection
        connection = psycopg2.connect(
            host=secret['host'],
            port=secret['port'],
            dbname='postgres',
            user=secret['username'],
            password=secret['password']
        )

        cursor = connection.cursor()

        # Execute SQL query
        cursor.execute("SELECT * FROM phi.patient LIMIT 1;")

        # Fetch result
        result = cursor.fetchone()

        # Close resources
        cursor.close()
        connection.close()

        return {
            'statusCode': 200,
            'body': json.dumps('Query Result: {}'.format(result))
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps('An error occurred: {}'.format(e))
        }
