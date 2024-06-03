import werkzeug
from odoo.exceptions import AccessDenied
from odoo import api, models, fields
from ..jwt_request import jwt_request

class Users(models.Model):
    _inherit = "res.users"
    
    access_token_ids = fields.One2many(
        string='Access Tokens',
        comodel_name='jwt_access_token',
        inverse_name='user_id',
    )

    def to_dict(self, single=True):
        res = []
        for u in self:
            d = u.read(['email', 'name'])[0]
            res.append(d)

        return res[0] if single else res
