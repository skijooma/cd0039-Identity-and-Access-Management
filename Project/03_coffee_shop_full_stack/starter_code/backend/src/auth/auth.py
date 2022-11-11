import json
from functools import wraps
from urllib.request import urlopen

from flask import abort, request
from jose import jwt

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
            'code': 'Invalid header', 'description': 'Header incomplete.'
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

    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)

    return True


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
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header', 'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'], 'kid': key['kid'], 'use': key['use'],
                'n': key['n'], 'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(token, rsa_key, algorithms=ALGORITHMS,
                                 audience=API_AUDIENCE,
                                 issuer='https://' + AUTH0_DOMAIN + '/')

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired', 'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience '
                               'and issuer. '
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


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
            try:
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except:
                abort(401)

            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator




# https://dev-4ezltnbcex7uvmp5.us.auth0.com/authorize?
# audience=ffsnd&
# response_type=token&
# client_id=V2cmp8AICx4yXN3pfTNnT3prnjhWWx89&
# redirect_uri=https://localhost:8080/callback

# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNyN2hvNVA2Qi13UE85ajZRVEo2TiJ9.eyJpc3MiOiJodHRwczovL2Rldi00ZXpsdG5iY2V4N3V2bXA1LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MzY5ODAxZWNmOTFkMmE3NmU5NDM3ODIiLCJhdWQiOiJmZnNuZCIsImlhdCI6MTY2ODE5MjA3MCwiZXhwIjoxNjY4MTk5MjcwLCJhenAiOiJWMmNtcDhBSUN4NHlYTjNwZlROblQzcHJuamhXV3g4OSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmRyaW5rcyIsImdldDpkcmlua3MiLCJnZXQ6ZHJpbmtzLWRldGFpbCIsInBhdGNoOmRyaW5rcyIsInBvc3Q6ZHJpbmtzIl19.DQN212NOL5yuu6_LnpnhB4lwLk-HwB0dSPU1r3SzVoRjwWAGlWGEo7eWAqfv8Z9FHe4U0GDIFmcpFUBDaQtv4IS7eMgt0BfQ0jJZJqUXTztF0e_KDooUvUXldUe3L0EX31fcU4saCrLkxJ566kxd0KmhMA-nwMkBwwFUQqLsLqrHp0czYkuir68uJWb7AMgZsgLOqj2o90iX_3UDk2YlnLHB34K9PviYvjKxIitnobkcY3Ju6QEJx6Lmu2lhn9PemPqNNx_pHQH2ObDs7U34ROXYU_s5h0D7IFWiF25YcxNAVg9sknyLKYtUaVF_tVz7RS7pclbimIeLrwYNMHdQ5w
