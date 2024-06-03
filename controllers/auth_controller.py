from odoo import http, _
import werkzeug
from functools import wraps
from odoo.http import request
from ..jwt_request import jwt_request
from ..util import is_valid_email
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError

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
            if not required_params.issubset(params):
                missing_params = required_params - params
                return jwt_request.response({'message': 'Missing Parameters (%s)'%(', '.join(missing_params))}, status=400)
            for key in required_params:
                if not kwargs[key]:
                    return jwt_request.response({'message': 'Parameter %s cannot be empty'%key}, status=400)
            if 'email' in required_params:
                if not is_valid_email(kwargs['email']):
                    return jwt_request.response({'message': 'Invalid email address'}, status=400)
            return f(*args, **kwargs)
        return decorated
    
    @http.route('/api/auth/register', type='json', auth="none", methods=['POST'], cors='*', csrf=False)
    @check_parameter
    def register(self, **kwargs):
        try:
            if request.env['res.users'].sudo().search([('login', '=', kwargs['email'])]):
                return jwt_request.response(status=400, data={'message': 'Email address has been taken'})
            auth_signup = AuthSignupHome()
            qcontext = auth_signup.get_auth_signup_qcontext()

            if not qcontext.get('token') and not qcontext.get('signup_enabled'):
                raise werkzeug.exceptions.NotFound()

            if 'error' not in qcontext and request.httprequest.method == 'POST':
                try:
                    values = {
                        'login': kwargs['email'],
                        'password': kwargs['password'],
                        'name': kwargs['name'],
                        'email': kwargs['email']
                    }
                    if not values:
                        raise UserError(_("Missing required fields."))
                    auth_signup._signup_with_values(qcontext.get('token'), values)
                    User = request.env['res.users']
                    user_sudo = User.sudo().search(
                        User._get_login_domain(values.get('login')), order=User._get_login_order(), limit=1
                    )
                except UserError as e:
                    qcontext['error'] = e.args[0]
                    jwt_request.response({'message': qcontext['error']}, status=400)
                except (SignupError, AssertionError) as e:
                    if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                        qcontext["error"] = _("Another user is already registered using this email address.")
                        jwt_request.response({'message': qcontext['error']}, status=400)
                    else:
                        _logger.error("%s", e)
                        qcontext['error'] = _("Could not create a new account.")
                        jwt_request.response({'message': qcontext['error']}, status=400)
                        
            if user_sudo:
                token = jwt_request.create_token(user_sudo, SECRET_KEY)
                return jwt_request.response({
                    'user': user_sudo.to_dict(),
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

