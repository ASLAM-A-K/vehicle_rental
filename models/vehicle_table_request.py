from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from datetime import datetime

from odoo.exceptions import ValidationError


class VehicleRentalRequest(models.Model):
    _name = "rent.request"
    _rec_name = 'rental_sequence'

    rental_sequence = fields.Char(string='Rental Reference', required=True,
                                  readonly=True, default='New')
    customer_id = fields.Many2one('res.partner')
    request_date = fields.Date(default=datetime.today())
    vehicle_access_id = fields.Many2one("vehicle.table")
    available_vehicle_id = fields.Many2one('vehicle.table', domain=[
        ('state', '=', 'Available')], string='Vehicle')
    from_date = fields.Datetime(default=datetime.today())
    to_date = fields.Datetime()
    rental_period = fields.Char()
    rental_state = fields.Selection(
        selection=[('draft', 'Draft'), ('confirm', 'Confirm'),
                   ('invoiced', 'Invoiced'),
                   ('returned', 'Returned')], default='draft')
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id')
    confirmed_request_id = fields.Many2one('vehicle.table')
    period_type = fields.Selection(
        selection=[('Hour', 'Hour'), ('Day', 'Day'), ('Week', 'Week'),
                   ('Month', 'Month')])
    period_type_id = fields.Many2one("rent.charges", string='Period Type')
    request_charge_ids = fields.One2many("rent.charges", "rental_id")
    rental_time = fields.Many2one('rent.charges')
    amount_id = fields.Monetary(compute='_compute_amount')
    invoice_id = fields.Many2one('account.move')
    invoice_count = fields.Integer(compute='compute_count')

    @api.model
    def create(self, vals):
        if vals.get('rental_sequence', 'New') == 'New':
            vals['rental_sequence'] = self.env['ir.sequence'].next_by_code(
                'rental.request') or 'New'
        res = super(VehicleRentalRequest, self).create(vals)
        return res

    @api.onchange('to_date')
    def _onchange_from_date(self):
        if self.to_date:
            if str(self.from_date) > str(self.to_date):
                raise ValidationError(
                    "To date cannot be earlier than from date.")
            two_days = self.to_date - relativedelta(days=2)
            two_day = two_days.strftime("%Y-%m-%d")
            today_date = str(fields.date.today())
            if two_day <= today_date:
                self.available_vehicle_id.date_warning = True
                if str(self.to_date) < today_date:
                    self.available_vehicle_id.date_warning = False
                    self.available_vehicle_id.date_late = True
            else:
                self.available_vehicle_id.date_warning = False

    @api.constrains('to_date')
    def _compute_rental_period(self):
        text = str(self.to_date.date() - self.from_date.date())
        period = text.strip(', 00:00:00')
        self.rental_period = period

    def action_confirm(self):
        self.rental_state = 'confirm'
        self.available_vehicle_id.state = 'Not Available'

    def action_return(self):
        self.rental_state = 'returned'
        self.available_vehicle_id.state = 'Available'
        self.available_vehicle_id.date_warning = False
        self.available_vehicle_id.date_late = False

    def action_create_invoice(self):
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_confirm': self.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Rent Service',
                'quantity': 1,
                'price_unit': self.amount_id
            })],
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rent Invoice',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': self.env.ref('account.view_move_form').id,
            'target': 'current',
            'res_id': invoice.id
        }

    @api.onchange('period_type_id', 'from_date', 'to_date')
    def _onchange_period_type(self):
        for i in self:
            if i.period_type_id.rental_time == 'Month':
                i.to_date = i.from_date + relativedelta(months=1)
            elif i.period_type_id.rental_time == 'Week':
                i.to_date = i.from_date + relativedelta(weeks=1)
            elif i.period_type_id.rental_time == 'Day':
                i.to_date = i.from_date + relativedelta(days=1)
            elif i.period_type_id.rental_time == 'Hour':
                i.to_date = i.from_date + relativedelta(hours=1)

    @api.onchange('to_date')
    def _compute_amount(self):
        if not self.period_type_id:
            for i in self:
                self.amount_id = i.available_vehicle_id.rent_amount
        else:
            for i in self:
                self.amount_id = i.period_type_id.rental_charge_amount

    @api.onchange('available_vehicle_id')
    def _onchange_vehicle(self):
        return {'domain': {'period_type_id': [
            ('id', 'in', self.available_vehicle_id.rental_charge_ids.ids)]}}

    def request_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice Request',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('invoice_confirm', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_count(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count(
                [('invoice_confirm', '=', self.id)])

    @api.model
    def get_rent_time(self, vehicle_id):
        period_type = self.env['rent.charges'].sudo().search([
            ('rental_id', '=', int(vehicle_id))])
        rent_list = {}
        for rec in period_type:
            rent_list[rec.id] = [rec.rental_time]
        return rent_list
