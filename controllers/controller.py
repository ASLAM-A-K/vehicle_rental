import io
import xlsxwriter
from odoo import http
from odoo.http import request, content_disposition


class RentalExcelReportController(http.Controller):
    @http.route(['/invoicing/excel_report/<model("rental.pdf"):report_id>',
                 ], type='http', auth="user", csrf=False)
    def get_rental_excel_report(self, report_id=None):
        response = request.make_response(None,
                                         headers=[
                                             ('Content-Type', 'application/vnd.ms-excel'),
                                             ('Content-Disposition',
                                              content_disposition('Vehicle_rental_report' + '.xlsx'))
                                         ]
                                         )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        header_style = workbook.add_format({'bold': True, 'bg_color': 'yellow', 'align': 'center',
                                            'font_size': 12, 'underline': True})
        tb_head = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 10})
        data_head = workbook.add_format({'bold': True, 'font_size': 9})
        sl_left = workbook.add_format({'align': 'left'})
        report_lines = report_id.get_report_lines()
        sql_data = report_lines.get('sql_data')
        sheet = workbook.add_worksheet("rental_report")
        sheet.set_column(1, 6, 25)
        sheet.write(0, 0, 'COMPANY', data_head)
        sheet.write(0, 1, report_lines['company_name'])
        sheet.write(1, 0, 'ADDRESS', data_head)
        sheet.write(1, 1, report_lines['company_address'])
        row = 3
        if report_lines['from_date'] != 'False':
            sheet.write(row, 1, 'FROM DATE:', data_head)
            row += 1
            sheet.write(row, 1, report_lines['from_date'])
            row += 1

        if report_lines['to_date'] != 'False':
            sheet.write(row, 1, 'TO DATE:', data_head)
            row += 1
            sheet.write(row, 1, report_lines['to_date'])
            row += 1

        if report_lines['vehicle_name'] != 0:
            sheet.write(row, 1, 'VEHICLE NAME:', data_head)
            row += 1
            sheet.write(row, 1, report_lines['vehicle_name'])
            row += 2

        col = 0
        sheet.write(row, col, 'SL NO:', tb_head)
        col += 1
        sheet.write(row, col, 'CUSTOMER NAME', tb_head)
        col += 1
        if report_lines['vehicle_name'] == 0:
            sheet.write(row, col, 'VEHICLE NAME', tb_head)
            col += 1
        sheet.write(row, col, 'VEHICLE STATE', tb_head)
        col += 1
        sheet.write(row, col, 'RENTAL PERIOD', tb_head)
        col += 1
        sheet.write(row, col, 'DATE FROM', tb_head)
        col += 1
        sheet.write(row, col, 'DATE TO', tb_head)
        row = row + 1
        number = 1
        head_col = 0
        for line in sql_data:
            col = 0
            sheet.set_row(row, 20)
            sheet.write(row, col, number, sl_left)
            col += 1
            sheet.write(row, col, line['display_name'])
            col += 1
            if report_lines['vehicle_name'] == 0:
                sheet.write(row, col, line['name'])
                col += 1
            sheet.write(row, col, line['state'])
            col += 1
            sheet.write(row, col, line['rental_period'])
            col += 1
            sheet.write(row, col, (line['from_date'].strftime("%d-%m-%Y")))
            col += 1
            sheet.write(row, col, (line['to_date'].strftime("%d-%m-%Y")))
            col += 1
            head_col = col
            row += 1
            number += 1

        if head_col == 7:
            sheet.merge_range('A3:G3', 'Vehicle Rental Report', header_style)
        else:
            sheet.merge_range('A3:F3', 'Vehicle Rental Report', header_style)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
