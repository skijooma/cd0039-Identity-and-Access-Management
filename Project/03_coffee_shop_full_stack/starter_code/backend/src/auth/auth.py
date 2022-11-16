import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen

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
    print("TOKEN ***** ", token)

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
            'code': 'unauthorized', 'description': 'Permission not found.'
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
    # print("JSONURL ***** ", jsonurl)
    jwks = json.loads(jsonurl.read())
    # print("JWKS ***** ", jwks)
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    # print("UNVERIFIED_HEADER ***** ", unverified_header)

    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header', 'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        # print("***** key['kid'] ***** ", key['kid'])
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'], 'kid': key['kid'], 'use': key['use'],
                'n': key['n'], 'e': key['e']
            }

    if rsa_key:
        # print("***** IN ***** ", rsa_key)
        try:
            payload = jwt.decode(token, rsa_key, algorithms=ALGORITHMS,
                                 audience=API_AUDIENCE,
                                 issuer='https://' + AUTH0_DOMAIN + '/')

            # print("PAYLOAD ***** ", payload)

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
    print("INSIDE ^^^^^^^^")
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
                print("PAYLOAD >>>>> ", payload)
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

# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNyN2hvNVA2Qi13UE85ajZRVEo2TiJ9.eyJpc3MiOiJodHRwczovL2Rldi00ZXpsdG5iY2V4N3V2bXA1LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MzY5ODAxZWNmOTFkMmE3NmU5NDM3ODIiLCJhdWQiOiJmZnNuZCIsImlhdCI6MTY2ODU0NDA0MiwiZXhwIjoxNjY4NjMwNDQyLCJhenAiOiJWMmNtcDhBSUN4NHlYTjNwZlROblQzcHJuamhXV3g4OSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmRyaW5rcyIsImdldDpkcmlua3MiLCJnZXQ6ZHJpbmtzLWRldGFpbCIsInBhdGNoOmRyaW5rcyIsInBvc3Q6ZHJpbmtzIl19.M4iqujlRYLmCsgoJXN6Hs7V60a6R4OOT-PU_R6ysrzCNq_2uz1GaYkQzpxgKOGN0XR7O9botvUmKV4DpUTHjLtGH39zaHWVvvHa3ssouJCy0-kkgdlY73RexEYs0DHeu-AOOUcB30ZKUy_yzKuaxQyehvqzg2_IYC5001p5sl1dAGCTpC_eUarnhx0GeELovi5Yvilau_F1m2TnS90QI5_NVxgdXxjDNodH8qJdx-Trf6qOhhuXIlToEFHO-8_kOV_iGv27La-iSzOlXrXiHBGDZkGmhkX-R4F6dNsrvx0Gr6Uf_3KKBLlTPvO7QxycAotFsaADADiuCJS0tReDzfA
