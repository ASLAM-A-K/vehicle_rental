# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class CustomerPage(http.Controller):

    @http.route('/customer/create', type='http', auth='public', website=True)
    def page_customer(self):
        return http.request.render('vehicle_rental.website_customer')

    @http.route('/customer/create/submit', type='http', auth='public',
                website=True)
    def create_customer(self, **post):
        request.env['res.partner'].sudo().create({
            'display_name': post.get('name'),
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('phone')
        })
        return http.request.render('vehicle_rental.website_customer_success')
