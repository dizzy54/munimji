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


def get_user_by_auth(access_token, access_token_secret):
    """ returns splitwise response json for user with input ouath access token
    """
    protected_uri = ' https://secure.splitwise.com/api/v3.0/get_current_user'
    response = get_splitwise_response(access_token, access_token_secret, protected_uri)
    return response.json()


def get_expenses(access_token, access_token_secret):
    protected_uri = 'https://secure.splitwise.com/api/v3.0/get_expenses'
    response = get_splitwise_response(access_token, access_token_secret, protected_uri)
    return response.json()
