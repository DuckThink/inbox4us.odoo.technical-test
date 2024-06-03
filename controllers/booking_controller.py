from odoo import http
from odoo.http import request
from datetime import datetime
from functools import wraps
from ..jwt_request import jwt_request
from ..util import is_valid_date
from ..controllers.auth_controller import SECRET_KEY

import logging
_logger = logging.getLogger(__name__)


class BookingController(http.Controller):

    def validate_request(f):
        """Decorators to ensure correct data is provided in the API requests."""
        @wraps(f)
        def decorated(*args, **kwargs):
            params = set(kwargs.keys())
            required_params = {'room_id', 'customer_id', 'checkin_date', 'checkout_date'}
            if not required_params.issubset(params):
                missing_params = required_params - params
                return jwt_request.response({'message': 'Missing Parameters (%s)' % (', '.join(missing_params))}, status=400)
            for key in required_params:
                if not kwargs[key]:
                    return jwt_request.response({'message': 'Parameter %s cannot be empty' % key}, status=400)
            room_id, customer_id, checkin_date, checkout_date = kwargs['room_id'], kwargs['customer_id'] \
                                                                    ,kwargs['checkin_date'], kwargs['checkout_date']
            if not request.env['hotel.room'].sudo().search([('id', '=', room_id)]):
                return jwt_request.response({'message': 'Invalid room id'}, status=400)
            if not request.env['hotel.customer'].sudo().search([('id', '=', customer_id)]):
                return jwt_request.response({'message': 'Invalid customer id'}, status=400)
            if is_valid_date(checkin_date) and is_valid_date(checkout_date):
                if checkin_date > checkout_date:
                    return jwt_request.response({'message': 'Checkin date must be less than checkout date'}, status=400)
            else:
                return jwt_request.response({'message': 'Invalid date format Y-m-d'}, status=400)
            return f(*args, **kwargs)
        return decorated
    
    def jwt_required(f):
        """Decorators to ensure jwt token is provided in the API requests."""
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header:
                return jwt_request.response({'message': 'Authorization header missing'}, status=401)
            return f(*args, **kwargs)
        return decorated

    @http.route('/api/bookings', type='json', auth='public', methods=['POST'])
    @validate_request
    @jwt_required
    def create_booking(self, **kwargs):
        try:
            # Extract and validate JWT token
            auth_header = request.httprequest.headers.get('Authorization')
            token = auth_header.split(" ")[1]
            if request.env['jwt_access_token'].sudo().search([('token', '=', token)]):
                access_token = request.env['jwt_access_token'].sudo().search([('token', '=', token)])
                if access_token.is_expired:
                    return jwt_request.response({'message': 'Token expired'}, status=401)
            else:
                return jwt_request.response({'message': 'Invalid token'}, status=401)
            uid = jwt_request.decode_token(token, SECRET_KEY)['user']
            user = request.env['res.users'].sudo().search([('id', '=', uid)])
            if not user:
                return jwt_request.response({'message': 'Invalid token'}, status=401)

            # Extract booking parameters
            room_id = kwargs['room_id']
            if request.env['hotel.room'].sudo().search([('id', '=', room_id)]).status != 'available':
                return jwt_request.response({'message': 'Room not available'}, status=400)
            customer_id = kwargs['customer_id']
            checkin_date = kwargs['checkin_date']
            checkout_date = kwargs['checkout_date']

            # Create booking record
            booking = request.env['hotel.booking'].sudo().create({
                'room_id': room_id,
                'customer_id': customer_id,
                'check_in_date': checkin_date,
                'check_out_date': checkout_date,
            })
            request.env['hotel.room'].sudo().search([('id', '=', room_id)]).status = 'booked'

            return jwt_request.response({
                'booking': booking.read()[0]
            }, status=201)
        except Exception as e:
            _logger.error(str(e))
            return jwt_request.response_500({
                'message': 'Server error'
            })
