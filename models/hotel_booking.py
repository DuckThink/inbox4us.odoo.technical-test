from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


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
    
    # Check date in backend
    @api.constrains('check_in_date', 'check_out_date')
    def _validate_date(self):
        for record in self:
            if record.check_in_date >= record.check_out_date:
                raise ValidationError(("Check-in date must be less than Check-out date"))

    @api.model
    def cron_update_room_status(self):
        bookings = self.search([])
        for booking in bookings:
            if booking.check_out_date < datetime.now().date():
                booking.room_id.status = 'available'

    # When booking is created, set the room status to 'booked'
    @api.model
    def create(self, vals):
        room = self.env['hotel.room'].browse(vals['room_id'])
        if room.status == 'booked':
            raise UserError('Room is not available')
        room.status = 'booked'
        return super(HotelBooking, self).create(vals)            
    
    # When booking is deleted, set the room status to 'available'
    def unlink(self):
        for booking in self:
            room = booking.room_id
            if room.status == 'booked':
                room.status = 'available'
        return super(HotelBooking, self).unlink()