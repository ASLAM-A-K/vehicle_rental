{
    'name': "Vehicle Rental",
    'version': "16.0.5",
    'category': "Vehicle Rental",
    'sequence': -2,
    'summary': 'Vehicles for rental',

    'depends': [
        'base', 'fleet', 'account', 'website'
     ],
    'data': [
        'security/access_rights.xml',
        'security/ir.model.access.csv',
        'data/website_menu.xml',
        'views/website_customer.xml',
        'views/website_request.xml',
        'views/vehicle_details.xml',
        'views/customer_success.xml',
        'views/rent_success.xml',
        'views/custom_template.xml',
        'views/custom_snippet.xml',
        'views/vehicle_rental_table.xml',
        'wizard/pdf_report.xml',
        'report/rental_template.xml',
        'views/vehicle_rental_request.xml',
        'views/vehicle_rental_menu.xml',
        'views/vehicle_rental_inheritance.xml'
            ],
    'assets': {
        'web.assets_frontend': [
            'vehicle_rental/static/src/xml/vehicle_template.xml',
            'vehicle_rental/static/src/js/rental_request.js',
            'vehicle_rental/static/src/js/vehicle_snippet.js',
            'vehicle_rental/static/src/scss/website_forum.scss'
             ],

            },
    'installable': True,
    'application': True,
}
