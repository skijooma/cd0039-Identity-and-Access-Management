import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen

from flask import abort, request

AUTH0_DOMAIN = 'dev-4ezltnbcex7uvmp5.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'ffsnd'

# AuthError Exception
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
Implementation of get_token_auth_header() method
    it gets the header from the request
        it raises an AuthError if no header is present
    it attempts to split bearer and the token
        it raises an AuthError if the header is malformed
    returns the token part of the header.
'''


def get_token_auth_header():
    """
    Retrieves the Access Token from the Authorization Header.
    """

    # Checking if authorization header is not present in the request.

    if 'Authorization' not in request.headers:
        raise AuthError({
            "code": "authorization_header_missing",
            "description": "Authorization header is expected"
        }, 401)

    auth_header = request.headers.get("Authorization", None)

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

    print("***** TOKEN ***** ")
    print(token)

    return token


'''
Implementation of check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it raises an AuthError if permissions are not included in the payload
    it raises an AuthError if the requested permission string is not in the payload permissions array
    returns true otherwise
'''


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized', 'description': 'Permission not found.'
        }, 403)

    return True


'''
Implementation of verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    function verifies the token using Auth0 /.well-known/jwks.json
    it decodes the payload from the token
    it validates the claims
    returns the decoded payload
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
Implementation of @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    Uses the get_token_auth_header method to get the token
    It uses the verify_decode_jwt method to decode the jwt
    It uses the check_permissions method validate claims and check the requested permission
    returns the decorator which passes the decoded payload to the decorated method
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


''' URL for getting new token '''

# https://dev-4ezltnbcex7uvmp5.us.auth0.com/authorize?
# audience=ffsnd&
# response_type=token&
# client_id=V2cmp8AICx4yXN3pfTNnT3prnjhWWx89&
# redirect_uri=https://localhost:8080/callback

''' Current working token as of Nov. 17th 00:37 (GM+2) '''
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNyN2hvNVA2Qi13UE85ajZRVEo2TiJ9.eyJpc3MiOiJodHRwczovL2Rldi00ZXpsdG5iY2V4N3V2bXA1LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MzY5ODAxZWNmOTFkMmE3NmU5NDM3ODIiLCJhdWQiOiJmZnNuZCIsImlhdCI6MTY2ODYzMjE1MywiZXhwIjoxNjY4NzE4NTUzLCJhenAiOiJWMmNtcDhBSUN4NHlYTjNwZlROblQzcHJuamhXV3g4OSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmRyaW5rcyIsImdldDpkcmlua3MiLCJnZXQ6ZHJpbmtzLWRldGFpbCIsInBhdGNoOmRyaW5rcyIsInBvc3Q6ZHJpbmtzIl19.RXURgAM4fSlHfS1YZ6-wNdl4vOvoXt1PHuyuweG7Bndblgdov38gok02-yQshE5w1lc7ROB1duNtIgzp0NcHEA_sK-m9TW_g39qxNl8duEg9MpcJBZMDg0RUFzCKliikjFj5YjiuawEHNRQJ9TN3yAzz_tgPwjQA1Dhm_ncNYvQZvtXAHpvJ8f7UQxK9u9m4kNUjn7UMZeLU8ueoPQNOWUZ_heuAMGKOtos2s_22EKI_IbILxQFX_sxXL0qOLGer3bqJLiq6gIYju1Fa8h_nJeWNMUlz4BI9xES03bK7UvY8_rz52VdiKTRidEHg19mYRQMTxnpbtqXRLRJZKb56JA
