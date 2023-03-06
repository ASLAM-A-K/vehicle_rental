from odoo import models, fields
from odoo.exceptions import UserError


class RentalPDFWizard(models.TransientModel):
    _name = "rental.pdf"

    date_from = fields.Date()
    date_to = fields.Date()
    vehicle_name_id = fields.Many2one('vehicle.table')
    partner_id = fields.Many2one('res.partner')
    customer_id = fields.Many2one('rent.request')

    def generate_pdf(self):
        cr = self._cr
        query = """select res_partner.display_name,vehicle_table.name,vehicle_table.state,rent_request.from_date,
                       rent_request.to_date, rent_request.rental_period from vehicle_table inner join rent_request 
                       on rent_request.available_vehicle_id=vehicle_table.id inner join res_partner on res_partner.id =
                       rent_request.customer_id """
        if self.vehicle_name_id:
            query += """and vehicle_table.name = '%s'""" % (self.vehicle_name_id.name)
        if self.date_from:
            query += """and rent_request.from_date >= '%s'""" % (self.date_from)
        if self.date_to:
            query += """and rent_request.to_date <= '%s'""" % (self.date_to)
        if self.partner_id:
            query += """and res_partner.id = %s """ % (self.partner_id.id)
        cr.execute(query)
        data = cr.dictfetchall()
        print(data)
        if not data:
            raise UserError("Sorry!! No data available to Print.")
        else:
            data = {
                'model_id': self.id,
                'to_date': self.date_to,
                'from_date': self.date_from,
                'vehicle_name': self.vehicle_name_id.name,
                'sql_data': data
            }
            return self.env.ref('vehicle_rental.vehicle_report_action').report_action(None, data=data)

    def get_report_lines(self):
        cr = self._cr
        query = """select res_partner.display_name,vehicle_table.name,vehicle_table.state,rent_request.from_date,
                       rent_request.to_date, rent_request.rental_period from vehicle_table inner join rent_request 
                       on rent_request.available_vehicle_id=vehicle_table.id inner join res_partner on res_partner.id =
                       rent_request.customer_id where 1=1 """
        if self.vehicle_name_id:
            query += """and vehicle_table.name = '%s'""" % self.vehicle_name_id.name
        if self.date_from:
            query += """and rent_request.from_date >= '%s'""" % self.date_from
        if self.date_to:
            query += """and rent_request.to_date <= '%s'""" % self.date_to
        if self.partner_id:
            query += """and res_partner.id = %s """ % self.partner_id.id
        cr.execute(query)
        data = cr.dictfetchall()

        company_address = ''
        if self.env.user.company_id.street:
            company_address += str(self.env.user.company_id.street) + ', '
        if self.env.user.company_id.street2:
            company_address += str(self.env.user.company_id.street2) + ', '
        if self.env.user.company_id.zip:
            company_address += str(self.env.user.company_id.zip) + ', '
        if self.env.user.company_id.country_id.name:
            company_address += str(self.env.user.company_id.country_id.name)
        data = {
            'model_id': self.id,
            'company_name': self.env.user.company_id.name,
            'to_date': str(self.date_to),
            'from_date': str(self.date_from),
            'vehicle_name': self.vehicle_name_id.name,
            'company_address': company_address,
            'sql_data': data
        }
        return data

    def generate_xls(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/invoicing/excel_report/%s' % self.id,
            'target': 'new',
        }
