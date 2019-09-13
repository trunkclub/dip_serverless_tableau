import json
import logging

import boto3
import tableauserverclient as TSC


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info(event)
    session = boto3.Session(region_name='us-east-1')
    ssm = session.client('ssm')
    user = ssm.get_parameter(Name='/tableau/user', WithDecryption=True)['Parameter']['Value']
    password = ssm.get_parameter(Name='/tableau/password', WithDecryption=True)['Parameter']['Value']

    body = json.loads(event['body'])
    extract_responses = []
    for item in body['payload']:
        server_name = item['server_name']
        host = ssm.get_parameter(Name=f"/tableau/{server_name}/host")['Parameter']['Value']

        logger.info(f"Connecting to {server_name} server")
        server = TSC.Server(host, use_server_version=True)
        auth = TSC.TableauAuth(user, password)

        with server.auth.sign_in(auth):
            for extract in item['extracts']:
                extract_name = extract

                ro = TSC.RequestOptions()
                filter = TSC.Filter(
                    TSC.RequestOptions.Field.Name,
                    TSC.RequestOptions.Operator.Equals,
                    extract_name
                )
                ro.filter.add(filter)

                resource, pagination = server.datasources.get(ro)
                resource = resource[0]
                logger.info(f'Refreshing datasource - {resource.name}')
                tableau_response = server.datasources.refresh(resource)
                extract_response = {
                    'server_name': server_name,
                    'extract_name': resource.name,
                    'queued_at': None,
                    'errors': []
                }
                try:
                    created_at = tableau_response.created_at
                    message = f'{resource.name} extract queued at {created_at}'
                    logger.info(message)
                    extract_response['queued_at'] = str(created_at)
                except AttributeError:
                    message = f'There was an error starting {resource.name}'
                    logger.info(message)
                    logger.error(tableau_response)
                    extract_response['errors'].append(message)
                extract_responses.append(extract_response)

    return {
        'headers': {'content-type': 'application/json'},
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Success',
            'extracts': extract_responses
        })
    }
