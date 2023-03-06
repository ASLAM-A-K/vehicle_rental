from odoo import models, fields, api


class ButtonConfirm(models.Model):
    _inherit = 'account.move'

    invoice_confirm = fields.Many2one("rent.request")

    @api.constrains('payment_state')
    def payment_state_check(self):
        for rec in self:
            if rec.payment_state == 'paid':
                self.invoice_confirm.rental_state = 'invoiced'


#
