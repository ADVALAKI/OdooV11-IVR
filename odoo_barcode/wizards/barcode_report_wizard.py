from odoo import models, fields, api
from odoo.http import request


class ProductPrintWizard(models.Model):
    _name = 'product.print.wizard'

    barcode_id = fields.Many2one('report.barcode.print', string="Products")
    product_id = fields.Many2one('product.product', string="Products")
    qty = fields.Integer(string='Quantity of Labels')


class BarcodeConfig(models.Model):
    _name = 'report.barcode.print'

    @api.model
    def _default_product_line(self):
        active_ids = self._context.get('active_ids', [])
        products = self.env['product.product'].browse(active_ids)
        return [(0, 0, {'product_id': x.id, 'qty': 1}) for x in products]

    product_line = fields.One2many('product.print.wizard', 'barcode_id', string="Products",
                                   default=_default_product_line)

    @api.multi
    def print_report(self):
        ids = [x.product_id.id for x in self.product_line]
        config = self.env['barcode.config'].get_values()
        data = self.read()[0]
        data.update({
            'config': config
        })
        datas = {'docids': ids,
                 'form': data
                 }
        return self.env.ref('odoo_barcode.barcode_report').report_action(self, data=datas)


class ReportBarcode(models.AbstractModel):
    _name = 'report.odoo_barcode.report_barcode_temp'

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        records = self.env['product.product'].browse(data['docids'])
        height = ((data['form']['config'].get('label_height') * data['form']['config'].get('dpi')) / 25.4)
        width = ((data['form']['config'].get('label_width') * data['form']['config'].get('dpi')) / 25.4)
        data.update({'img_height' : height,
                     'img_width': width
                     })
        print('\n---',data,'-data--\n')
        return {
            'doc_ids': data['docids'],
            'doc_model': 'product.product',
            'docs': records,
            'data': data,
        }
