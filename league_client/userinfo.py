from .logger import logger
from .rso import ClientSession
from .rso import get_basic_auth
from .rso_auth import parsing_auth_code
from .utils import parse_access_token, parse_userinfo

async def get_userinfo(
    username, password, proxy=None, proxy_user=None, proxy_pass=None
):
    try:
        proxy_auth = get_basic_auth(proxy_user, proxy_pass)
        async with ClientSession() as session:
            logger.info('Parsing authorization code...')
            data = {
                'client_id': 'riot-client',
                'nonce': '1',
                'redirect_uri': 'http://localhost/redirect',
                'scope': 'openid ban',
                'response_type': 'token id_token',
            }
            if not await parsing_auth_code(session, data, proxy, proxy_user, proxy_pass):
                logger.info('Failed.')
                return {'error': 'Failed to parse authorization code'}, 1
            logger.info('Success.')

            logger.info('Getting access token...')
            data = {
                'type': 'auth',
                'username': username,
                'password': password,
                'remember': True,
            }
            data, error = await parse_access_token(session, data, proxy, proxy_auth)
            if error:
                logger.info('Failed.')
                return data, 1
            access_token = data['access_token']
            logger.info('Success.')
            
            logger.info('Parsing userinfo...')
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            data, error = await parse_userinfo(session, headers, proxy, proxy_auth)
            if error:
                logger.info('Failed.')
                return data, 1
            logger.info('Success.')
            
            return data, None
    except Exception as exp:
        logger.error(f'Got exception type: {exp.__class__.__name__}')
        return {'error': 'Exception occurred'}, 1
