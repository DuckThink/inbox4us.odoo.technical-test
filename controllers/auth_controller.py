from odoo import http
from functools import wraps
from odoo.http import request
from ..jwt_request import jwt_request
from ..util import is_valid_email

import logging
_logger = logging.getLogger(__name__)

SECRET_KEY = 'your_secret_key_here'

class AuthController(http.Controller):

    def check_parameter(f):
        """Decorators to ensure correct data is provided in the API requests."""
        @wraps(f)
        def decorated(*args, **kwargs):
            params = set(kwargs.keys())
            required_params = set()
            if f.__name__ == 'register':
                required_params = {'name', 'email', 'password'}
            if f.__name__ == 'login':
                required_params = {'email', 'password'}
            if f.__name__ == 'booking':
                required_params = {'room_id', 'customer_id', 'checkin_date', 'checkout_date'}
            if not required_params.issubset(params):
                missing_params = required_params - params
                return jwt_request.response({'message': 'Missing Parameters (%s)'%(', '.join(missing_params))}, status=400)
            for key in required_params:
                if not kwargs[key]:
                    return jwt_request.response({'message': 'Parameter %s cannot be empty'%key}, status=400)
            if 'email' in required_params:
                if not is_valid_email(kwargs['email']):
                    return jwt_request.response({'message': 'Invalid email address'}, status=400)
            if {'checkin_date', 'checkout_date'}.issubset(required_params):
                if kwargs['checkin_date'] > kwargs['checkout_date']:
                    return jwt_request.response({'message': 'Checkin date must be less than checkout date'}, status=400)
            return f(*args, **kwargs)
        return decorated
    
    @http.route('/api/auth/register', type='json', auth="none", methods=['POST'], cors='*', csrf=False)
    @check_parameter
    def register(self, **kwargs):
        try:
            if request.env['res.users'].sudo().search([('login', '=', kwargs['email'])]):
                return jwt_request.response(status=400, data={'message': 'Email address has been taken'})
            user = request.env['res.users'].sudo().create({
                'login': kwargs['email'],
                'password': kwargs['password'],
                'name': kwargs['name'],
                'email': kwargs['email'],
                'company_id': request.env.ref('base.main_company').id,
                'company_ids': [(4, request.env.ref('base.main_company').id)],
            })
            if user:
                token = jwt_request.create_token(user, SECRET_KEY)
                return jwt_request.response({
                    'user': user.to_dict(),
                    'token': token
                })
        except Exception as e:
            _logger.error(str(e))
            return jwt_request.response_500({
                'message': 'Server error'
            })

    @http.route('/api/auth/login', type='json', auth='none', methods=['POST'], cors='*', csrf=False)
    @check_parameter
    def login(self, **kwargs):
        email, password = kwargs['email'], kwargs['password']
        token = jwt_request.login(email, password, SECRET_KEY)
        return jwt_request.response({
            'user': request.env.user.to_dict(),
            'token': token,
        })
    
    @http.route('/api/auth/booking', type='json', auth='none', methods=['POST'], cors='*', csrf=False)
    @check_parameter
    def booking(self, **kwargs):
        try:
            # Extract and validate JWT token
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header:
                return jwt_request.response({'message': 'Authorization header missing'}, status=401)
            token = auth_header.split(" ")[1]
            user = jwt_request.decode_token(token, SECRET_KEY)
            if not user:
                return jwt_request.response({'message': 'Invalid token'}, status=401)

            # Extract booking parameters
            room_id = kwargs['room_id']
            customer_id = kwargs['customer_id']
            checkin_date = kwargs['checkin_date']
            checkout_date = kwargs['checkout_date']

            # Create booking record
            booking = request.env['hotel.booking'].sudo().create({
                'room_id': room_id,
                'customer_id': customer_id,
                'checkin_date': checkin_date,
                'checkout_date': checkout_date,
                'user_id': user.id,
            })

            return jwt_request.response({
                'booking': booking.read()[0]
            }, status=201)
        except Exception as e:
            _logger.error(str(e))
            return jwt_request.response_500({
                'message': 'Server error'
            })
