"""
AWS module - Keep the aws services adpaters
Version: 1.0.0
"""


def change_endpoint(cls):
    endpoint_url = cls.config.get('LOCALSTACK_ENDPOINT', None)
    # Fix para tratar diff entre docker/local
    if endpoint_url == 'http://0.0.0.0:4583' or \
            endpoint_url == 'http://localstack:4583':
        old_value = endpoint_url
        cls.config.set('LOCALSTACK_ENDPOINT', 'http://localhost:4583')
        endpoint_url = cls.config.get('LOCALSTACK_ENDPOINT', None)
        cls.logger.debug(
            'Changing the endpoint from {} to {}'.format(old_value, endpoint_url))
        # override the property
        cls.endpoint_url = endpoint_url
