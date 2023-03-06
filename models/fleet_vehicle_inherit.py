from odoo import models, fields


class VehicleRentalInherit(models.Model):
    _inherit = 'fleet.vehicle'

    registration_date = fields.Date(copy=False)