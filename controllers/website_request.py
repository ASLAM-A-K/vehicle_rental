# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from datetime import datetime

from odoo import http, api
from odoo.http import request


class WebsitePage(http.Controller):
    @http.route('/request2', type='http', auth='public', website=True)
    def rental_page(self):
        partner = request.env['res.partner'].sudo().search([])
        vehicle = request.env['vehicle.table'].sudo().search([('state', '=',
                                                               'Available')])
        values = {}
        values.update({
            'vehicles': vehicle,
            'partners': partner
        })
        return http.request.render('vehicle_rental.website_rent_request',
                                   values)

    @http.route('/submit', type='http', auth='public', website=True)
    def page_submit(self, **post):
        period = post.get('period_type')
        rent = request.env['rent.charges'].sudo().search([('id', '=',
                                                           int(period))])
        from_date = datetime.strptime(post.get('from_date'), '%Y-%m-%d')
        if rent.rental_time == 'Month':
            to_date = from_date + relativedelta(months=1)
        elif rent.rental_time == 'Week':
            to_date = from_date + relativedelta(weeks=1)
        elif rent.rental_time == 'Day':
            to_date = from_date + relativedelta(days=1)
        elif rent.rental_time == 'Hour':
            to_date = from_date + relativedelta(hours=1)

        request.env['rent.request'].sudo().create({
            'customer_id': post.get('partner_name'),
            'available_vehicle_id': post.get('available_vehicle_id'),
            'period_type_id': post.get('period_type'),
            'from_date': post.get('from_date'),
            'to_date': to_date
        })
        return http.request.render('vehicle_rental.website_rent_success')

    @http.route('/get_period', type='json', auth='public', website=False)
    @api.model
    def get_rent_time(self, vehicle_id):
        period_type = request.env['rent.charges'].sudo().search([
            ('rental_id', '=', int(vehicle_id))])
        rent_list = {}
        for rec in period_type:
            rent_list[rec.id] = [rec.rental_time]
        return rent_list
