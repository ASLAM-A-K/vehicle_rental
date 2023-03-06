from odoo import models, fields, api


class RentCharges(models.Model):
    _name = "rent.charges"
    _rec_name = 'rental_time'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    rental_time = fields.Selection(selection=[('Hour', 'Hour'), ('Day', 'Day'), ('Week', 'Week'), ('Month', 'Month')],
                                   string='Time')
    rental_charge_amount = fields.Monetary(currency_field='currency_id', tracking=True, string='Amount')
    rental_id = fields.Many2one("vehicle.table")
