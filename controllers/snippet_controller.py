import itertools
import operator
from odoo import http, api
from odoo.http import request


class TopRental(http.Controller):
    @http.route('/TopFourVehicles', type="json", auth="public", website=False)
    def top_vehicle(self):
        vehicles = request.env['rent.request'].sudo().search([]).mapped(
            'available_vehicle_id')
        vehicle_dict = {}
        image_dict = {}
        for rec in vehicles:
            count = request.env['rent.request'].sudo().search_count(
                [('available_vehicle_id', '=', rec.id)])
            vehicle_dict[rec.id] = count
        sorted_d = dict(sorted(vehicle_dict.items(), key=operator.itemgetter(1)
                               , reverse=True))
        top_four = dict(itertools.islice(sorted_d.items(), 4))
        for i in top_four:
            vehicle = vehicles.filtered((lambda l: l.id == i))
            image_dict[vehicle.name] = vehicle.id
        return image_dict

    @http.route('/top_vehicle_details', type="http", auth="public",
                website=True, csrf=False)
    @api.model
    def top_vehicle_details(self, **post):
        vehicle_id = post.get('vehicle_id')
        print(vehicle_id)
        vehicle = request.env['vehicle.table'].sudo().browse([int(vehicle_id)])
        return http.request.render('vehicle_rental.website_vehicle',
                                   {'vehicle': vehicle})
