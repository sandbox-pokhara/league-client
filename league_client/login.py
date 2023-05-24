import json
import os
import time

import requests

from league_process.utils import is_running

from .logger import logger


def get_phases():
    dirname = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dirname, 'phases.json')) as fp:
        return json.load(fp)


def get_is_authorized(connection):
    res = connection.get('/rso-auth/v1/authorization')
    return res.ok


def get_is_agreement_required(connection):
    res = connection.get('/eula/v1/agreement')
    if not res.ok:
        return False
    res = res.json()
    if 'acceptance' not in res:
        return False
    return res['acceptance'] not in ['Accepted', 'WaitingForAllServiceData']


def get_is_age_restricted(connection):
    try:
        response = connection.get('/age-restriction/v1/age-restriction/products/league_of_legends')
        response = response.json()
        return response.get('restricted', False)
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return False


def get_is_country_region_missing(connection):
    try:
        response = connection.get('/riot-client-auth/v1/userinfo')
        response = response.json()
        return response.get('country', 'npl') == 'nan'
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return False


def accept_agreement(connection):
    connection.put('/eula/v1/agreement/acceptance')


def wait_until_patched(connection, timeout=7200):
    start_time = time.time()
    while True:
        try:
            time.sleep(10)
            time_elapsed = time.time() - start_time
            logger.info(f'Patching riot client. Time elapsed: {int(time_elapsed)}s.')
            if time_elapsed > timeout:
                return False
            res = connection.get('/rnet-lifecycle/v1/product-context-phase')
            phase = res.json()
            if phase not in ['PatchStatus', 'WaitingForPatchStatus']:
                return True
        except requests.exceptions.RequestException:
            pass


def authorize(connection, username, password):
    authorized = get_is_authorized(connection)
    if authorized:
        if get_is_age_restricted(connection):
            return {'ok': False, 'detail': 'Age restricted.'}
        if get_is_country_region_missing(connection):
            return {'ok': False, 'detail': 'Country/region missing.'}
        return {'ok': True, 'logged_in': True}
    if authorized and get_is_agreement_required(connection):
        accept_agreement(connection)
        return {'ok': True, 'logged_in': True}
    data = {'clientId': 'riot-client', 'trustLevels': ['always_trusted']}
    res = connection.post('/rso-auth/v2/authorizations', json=data)
    if not res.ok and 'rate_limited' in res.text:
        return {'ok': False, 'detail': 'Rate limited.'}
    data = {'username': username, 'password': password, 'persistLogin': False}
    res = connection.put('/rso-auth/v1/session/credentials', json=data)
    res_json = res.json()
    if 'message' in res_json:
        if res_json['message'] == 'authorization_error: consent_required: ':
            return {'ok': False, 'detail': 'Consent required.'}
    if 'error' in res_json:
        if res_json['error'] == 'auth_failure':
            return {'ok': False, 'detail': 'Auth failure.'}
        if res_json['error'] == 'rate_limited':
            return {'ok': False, 'detail': 'Rate limited.'}
    return {'ok': True, 'logged_in': False}


def launch_league(connection):
    connection.post('/product-launcher/v1/products/league_of_legends/patchlines/live')


def get_product_context_phase(connection):
    res = connection.get('/rnet-lifecycle/v1/product-context-phase')
    if res.status_code == 404:
        return None
    return res.json()


def login(connection, username, password, timeout=180, patch_timeout=7200):
    logger.info('Logging in...')
    start_time = time.time()
    phases = get_phases()
    while True:
        if time.time() - start_time >= timeout:
            return {'ok': False, 'detail': 'Timeout.'}

        phase = get_product_context_phase(connection)
        logger.info(f'Riot client phase: {phase}')

        # Bad phases
        if phase == 'Unknown':
            return {'ok': False, 'detail': 'Unknown phase.'}
        if phase in phases['region_missing']:
            return {'ok': False, 'detail': 'Region missing.'}
        if phase in phases['banned']:
            return {'ok': False, 'detail': 'Account banned.'}
        if phase in phases['consent_required']:
            return {'ok': False, 'detail': 'Consent required.'}
        if phase in phases['account_alias_change']:
            return {'ok': False, 'detail': 'Name change required.'}
        if phase in phases['vng_account_required']:
            return {'ok': False, 'detail': 'Vng account required.'}

        # Good phases
        if phase in phases['success']:
            if is_running('LeagueClient.exe'):
                return {'ok': True}
            launch_league(connection)
            time.sleep(2)
            continue
        if phase in phases['wait_for_launch']:
            launch_league(connection)
            time.sleep(2)
            continue
        if phase is None or phase in phases['login']:
            res = authorize(connection, username, password)
            if not res['ok']:
                return res
            if res['ok'] and res['logged_in']:
                if is_running('LeagueClient.exe'):
                    return {'ok': True}
                launch_league(connection)
                time.sleep(2)
                continue
            if res['ok'] and not res['logged_in']:
                time.sleep(2)
                continue
        if phase in phases['eula']:
            accept_agreement(connection)
            time.sleep(2)
            continue
        if phase in phases['patch_status']:
            if not wait_until_patched(connection, timeout=patch_timeout):
                return {'ok': False, 'detail': 'Patch timeout.'}
            time.sleep(2)
            continue
        time.sleep(2)
