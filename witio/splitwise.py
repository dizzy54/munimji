from requests_oauthlib import OAuth1Session

from django.conf import settings

client_key = settings.SPLITWISE_CLIENT_KEY
client_secret = settings.SPLITWISE_CLIENT_SECRET


def get_request_token():
    """ obtain generic resource owner key and secret from splitwise
    """
    request_token_url = 'https://secure.splitwise.com/api/v3.0/get_request_token'
    oauth = OAuth1Session(client_key, client_secret=client_secret)
    fetch_response = oauth.fetch_request_token(request_token_url)

    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    return oauth, resource_owner_key, resource_owner_secret


def get_splitwise_response(access_token, access_token_secret, protected_uri, *args, **kwargs):
    oauth = OAuth1Session(
        client_key,
        client_secret=client_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )
    response = oauth.get(protected_uri)
    return response


def post_splitwise_request(access_token, access_token_secret, protected_uri, params_dict, *args, **kwargs):
    oauth = OAuth1Session(
        client_key,
        client_secret=client_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )
    response = oauth.post(protected_uri, **params_dict)
    return response


def get_user_by_auth(access_token, access_token_secret):
    """ returns splitwise response json for user with input ouath access token
    """
    protected_uri = 'https://secure.splitwise.com/api/v3.0/get_current_user'
    response = get_splitwise_response(access_token, access_token_secret, protected_uri)
    return response.json()


def create_equal_expense(access_token, access_token_secret, participant_list, total_amount, description):
    """
    """
    protected_uri = 'https://secure.splitwise.com/api/v3.0/create_expense'
    n_payers = 0
    n_payees = 0
    for participant in participant_list:
        if participant['payer']:
            n_payers += 1
        if participant['payee']:
            n_payees += 1
    amount_paid = total_amount / n_payers
    amount_split = total_amount / n_payees
    params_dict = {
        'payment': False,
        'cost': total_amount,
        'description': description,
    }
    '''
    participant_list = []
    for payer in payers:
        participant_list.append({'participant': payer, 'payer': True, 'payee': False})
    for payee in payees:
        if payee in payers:
            for participant in participant_list:
                if participant['participant'] == payee:
                    participant['payee'] = True
        else:
            participant_list.append({'participant': payee, 'payer': False, 'payee': True})
    '''
    i = 0
    for entry in participant_list:
        participant = entry['participant']
        payer_dict = {
            'user_id': participant['id'],
            'email': participant['email'],
            'paid_share': amount_paid if entry['payer'] else 0,
            'owed_share': amount_split if entry['payee'] else 0,
        }
        for param in ('user_id', 'email', 'paid_share', 'owed_share'):
            k = 'users__%d__%s' % (i, param)
            params_dict[k] = payer_dict[param]
        i += 1

    response = post_splitwise_request(access_token, access_token_secret, protected_uri, params_dict)
    return response.json()


def get_expenses(access_token, access_token_secret):
    protected_uri = 'https://secure.splitwise.com/api/v3.0/get_expenses'
    response = get_splitwise_response(access_token, access_token_secret, protected_uri)
    return response.json()


def get_friends(access_token, access_token_secret):
    protected_uri = 'https://secure.splitwise.com/api/v3.0/get_friends'
    response = get_splitwise_response(access_token, access_token_secret, protected_uri)
    return response.json()
