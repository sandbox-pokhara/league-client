def get_summoner_by_name(connection, name):
    res = connection.get(f'/lol-summoner/v1/summoners?name={name}')
    if not res.ok:
        return {'ok': False, 'status_code': res.status_code, 'detail': res.json()}
    return {'ok': True, 'data': res.json()}
