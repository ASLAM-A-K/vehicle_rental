from odoo import models, fields, api
from odoo.exceptions import ValidationError


class VehicleRental(models.Model):
    _name = "vehicle.table"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    rental_vehicle_id = fields.Many2one('fleet.vehicle', required=True, domain="[('state_id.name', '=', 'Registered')]")
    name = fields.Char(store=True)
    model_year = fields.Char(compute='_compute_nameof', store=True)
    state = fields.Selection(
        selection=[('Available', 'Available'), ('Not Available', 'Not Available'), ('Sold', 'Sold')],
        default='Available')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    rent_amount = fields.Monetary(currency_field='currency_id', tracking=True)
    reg_date = fields.Date(related="rental_vehicle_id.registration_date", string="Registration Date", store=True)
    vehicle_brand = fields.Char(compute="_compute_vehicle_brand", store=True, default=" ")
    vehicle_access_id = fields.Many2one("rent.request")
    confirmed_rental_ids = fields.One2many("rent.request", "available_vehicle_id",
                                           domain=[('rental_state', '=', 'confirm')], string=" ", readonly=True)
    rental_charge_ids = fields.One2many("rent.charges", "rental_id")
    date_warning = fields.Boolean(string='Warning', readonly=True)
    date_late = fields.Boolean(string='Late', readonly=True)
    vehicle_image = fields.Image('Image')

    @api.depends('rental_vehicle_id')
    def _compute_vehicle_brand(self):
        self.vehicle_brand = self.rental_vehicle_id.brand_id.name

    @api.onchange('model_year')
    def _compute_nameof(self):
        if self.model_year:
            self.name = self.rental_vehicle_id.name + "/" + str(self.model_year)

    @api.onchange('reg_date')
    def _onchange_rental_vehicle_id(self):

        if self.reg_date:
            self.model_year = self.reg_date.year

    def vehicle_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicles Request',
            'view_mode': 'tree',
            'res_model': 'rent.request',
            'domain': [('available_vehicle_id', '=', self.name)],
            'context': "{'create': False}"
        }

    @api.onchange('rental_charge_ids')
    def _onchange_rental_charge_ids(self):
        for i in self.rental_charge_ids:
            line = self.rental_charge_ids.filtered(lambda l: l.rental_time == i.rental_time)
            if len(line) > 1:
                raise ValidationError('Already Chosen, Please choose another period.')


