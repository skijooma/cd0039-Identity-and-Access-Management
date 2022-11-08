from functools import wraps

from flask import abort, request

AUTH0_DOMAIN = 'dev-4ezltnbcex7uvmp5.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'ffsnd'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''


def get_token_auth_header():
    """
    Retrieves the Access Token from the Authorization Header.
    """

    # Checking if authorization header is not present in the request.
    if 'Authorization' not in request.headers:
        raise AuthError("Authorization missing", 401)

    auth_header = request.headers['Authorization']

    parts = auth_header.split()

    # Checking if bearer part is missing.
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'Malformed header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    # Checking if header is missing a part.
    elif len(parts) == 1:
        raise AuthError({
            'code': 'Invalid header',
            'description': 'Header incomplete.'
        }, 401)

    # Checking if header has excess parts.
    elif len(parts) > 2:
        raise AuthError({
            'code': 'Invalid header',
            'description': 'Authorization header has excess parts.'
        }, 401)

    token = parts[1]

    return token


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    raise Exception('Not Implemented')


'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
    raise Exception('Not Implemented')


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
