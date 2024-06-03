from simplejson import dumps
import datetime
import traceback
import functools
import jwt
from odoo import http
from odoo.http import request, Response
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)

class JwtRequest:

    def __init__(self):
        self.odoo_req = request


    def is_rpc(self):
        return 'application/json' in request.httprequest.headers.get('Content-Type','')


    def is_ok_response(self, status=200):
        return status >= 200 and status < 300

    def rpc_response(self, data={}, status=200):
        '''
        Response json rpc request (with controller type='json')
        '''
        r = {
            'success': True if self.is_ok_response(status) else False,
            'code': status,
        }
        if not self.is_ok_response(status):
            return { **r, **data }
        return { **r, 'data': data }


    def response(self, data={}, status=200):
        if self.is_rpc():
            return self.rpc_response(data, status)
        return {'message': 'Invalid Content-Type', 'code': 400, 'data': data }

    def response_500(self, data={}):
        return self.response(data, 500)

    def response_404(self, data={}):
        return self.response(data, 404)
    
    def decode_token(self, token, secret_key):
        '''
        Decode a jwt token
        '''
        return jwt.decode(
                    token, 
                    secret_key, 
                    algorithms='HS256'
                )
    
    def sign_token(self, payload, secret_key):
        '''
        Generally sign a jwt token
        '''
        token = jwt.encode(
            payload,
            secret_key,
            algorithm='HS256'
        )

        return token

    def create_token(self, user, secret_key):
        '''
        Create a token
        '''
        try:
            exp = datetime.datetime.now() + datetime.timedelta(days=30)
            payload = {
                'exp': exp,
                'iat': datetime.datetime.now(),
                'user': user.id,
                'login': user.login,
            }
            token = self.sign_token(payload, secret_key)
            self.save_token(token, user.id, exp)
            return token
        except Exception as ex:
            _logger.error(traceback.format_exc())
            raise


    def save_token(self, token, uid, exp):
        '''Save token to database
        '''
        request.env['jwt_access_token'].sudo().create({
            'user_id': uid,
            'expires': exp.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'token': token,
        })


    def get_state(self):
        '''
        get database state
        '''
        return {
            'd': request.session.db
        }


    def login(self, login, password, secret_key, with_token=True):
        '''
        Try logging user in use their login & password.
        '''
        state = self.get_state()
        uid = request.session.authenticate(state['d'], login, password)
        if not uid:
            return False
        if with_token:
            return self.create_token(request.env.user, secret_key)
        return True

jwt_request = JwtRequest()
