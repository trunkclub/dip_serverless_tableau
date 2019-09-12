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

    for item in event['payload']:
        host = ssm.get_parameter(Name=f"/tableau/{item['database']}/host")['Parameter']['Value']

        logger.info(f"Connecting to {item['database']} server")
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
                response = server.datasources.refresh(resource)
                try:
                    created_at = response.created_at
                    logger.info(f'{resource.name} extract queued at {created_at}')
                except AttributeError:
                    logger.info(f'There was an error starting {resource.name}')
                    logger.error(response)
