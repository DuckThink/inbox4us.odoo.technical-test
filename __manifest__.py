{
    'name': 'Inbox4us Hotel Booking Management',
    'author': 'Nguyen Duc Thinh',
    'version': '1.0',
    'category': 'Hotel Management',
    'summary': 'Manage hotel room bookings and customers',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/user_view.xml',
        'views/hotel_booking_view.xml',
        'views/hotel_customer_view.xml',
        'views/hotel_room_view.xml',
        'views/menu_view.xml',
    ],
    'installable': True,
    'application': True,
}