from odoo import models, fields, api
from odoo.exceptions import UserError


class HotelBooking(models.Model):
    _name = 'hotel.booking'
    _description = 'Hotel Booking'

    customer_id = fields.Many2one('hotel.customer', string='Customer', required=True)
    room_id = fields.Many2one('hotel.room', string='Room', required=True)
    check_in_date = fields.Date(string='Check-in Date', required=True)
    check_out_date = fields.Date(string='Check-out Date', required=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)

    @api.depends('room_id', 'check_in_date', 'check_out_date')
    def _compute_total_amount(self):
        for booking in self:
            if booking.check_in_date and booking.check_out_date:
                num_nights = (booking.check_out_date - booking.check_in_date).days
                booking.total_amount = booking.room_id.price_per_night * num_nights
    
    @api.onchange('check_in_date', 'check_out_date')
    def _onchange_dates(self):
        if self.check_in_date and self.check_out_date:
            if self.check_in_date >= self.check_out_date:
                raise UserError('Check-in date must be less than Check-out date')
            
    

    def unlink(self):
        for booking in self:
            room = booking.room_id
            if room.status == 'booked':
                room.status = 'available'
        return super(HotelBooking, self).unlink()