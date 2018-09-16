# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class BarcodeConfig(models.TransientModel):
    _name = "barcode.config"
    _inherit = "res.config.settings"

    currency = fields.Selection([('inr', 'INR'), ('eur', 'EUR')], string="Currency")
    symbol_position = fields.Selection([('before', 'Before Amount'), ('after', 'After Amount')],
                                       string="Symbol Position")
    label_width = fields.Float('Label Width(MM)', required=True)
    label_height = fields.Float('Label Height(MM)', required=True)
    product_name = fields.Boolean('Product Name')
    product_default_code = fields.Boolean('Product Default Code')
    barcode_label = fields.Boolean('Barcode Labels')
    attributes = fields.Boolean('Attributes')
    price = fields.Boolean('Price')
    type = fields.Selection([('codabar', 'Codabar'),
                             ('CODE11', 'Code11'),
                             ('EAN13', 'EAN13'),
                             ('CODE128', 'CODE128'),
                             ('EAN18', 'EAN8'),
                             ('extended39', 'Extended39'),
                             ('usps_4state', 'USPS_4State'),
                             ('i2of5', 'I2of5'),
                             ('upca', 'UPCA'),
                             ('QR', 'QR')
                             ], string="Type", required=True, default="ean13")
    barcode_field = fields.Selection([('barcode', 'Barcode'),
                                      ('cost_method', 'Cost Method'),
                                      ('hs_code', 'HS Code'),
                                      ('manufacturer_pro_number', 'Manufacturer Product Number'),
                                      ('name', 'Name'),
                                      ('valuation', 'Valuation'),
                                      ('reference', 'Internal Reference'),
                                      ], string="Barcode Field", required=True)
    readable = fields.Boolean('Human Readable')
    margin_left = fields.Float('Margin(left)')
    margin_right = fields.Float('Margin(Right)')
    margin_top = fields.Float('Margin(Top)')
    margin_bottom = fields.Float('Margin(Bottom)')
    dpi = fields.Float('DPI')

    @api.model
    def get_values(self):
        res = super(BarcodeConfig, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            label_width=int(float(ICPSudo.get_param('label_width'))),
            label_height=int(float(ICPSudo.get_param('label_height'))),
            product_name=ICPSudo.get_param('product_name'),
            product_default_code=ICPSudo.get_param('product_default_code'),
            currency=ICPSudo.get_param('currency'),
            symbol_position=ICPSudo.get_param('symbol_position'),
            barcode_label=ICPSudo.get_param('barcode_label'),
            attributes=ICPSudo.get_param('attributes'),
            price=ICPSudo.get_param('price'),
            type=ICPSudo.get_param('type'),
            barcode_field=ICPSudo.get_param('barcode_field'),
            readable=ICPSudo.get_param('readable'),
            margin_left=int(float(ICPSudo.get_param('margin_left'))),
            margin_right=int(float(ICPSudo.get_param('margin_right'))),
            margin_top=int(float(ICPSudo.get_param('margin_top'))),
            margin_bottom=int(float(ICPSudo.get_param('margin_bottom'))),
            dpi=int(float(ICPSudo.get_param('dpi'))),
        )
        return res

    @api.multi
    def set_values(self):
        super(BarcodeConfig, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('label_width', self.label_width)
        ICPSudo.set_param('label_height', self.label_height)
        ICPSudo.set_param('product_name', self.product_name)
        ICPSudo.set_param('currency', self.currency)
        ICPSudo.set_param('symbol_position', self.symbol_position)
        ICPSudo.set_param('product_default_code', self.product_default_code)
        ICPSudo.set_param('barcode_label', self.barcode_label)
        ICPSudo.set_param('attributes', self.attributes)
        ICPSudo.set_param('price', self.price)
        ICPSudo.set_param('type', self.type)
        ICPSudo.set_param('barcode_field', self.barcode_field)
        ICPSudo.set_param('readable', self.readable)
        ICPSudo.set_param('margin_left', self.margin_left)
        ICPSudo.set_param('margin_right', self.margin_right)
        ICPSudo.set_param('margin_top', self.margin_top)
        ICPSudo.set_param('margin_bottom', self.margin_bottom)
        ICPSudo.set_param('dpi', self.dpi)
        record = self.env['report.paperformat'].search([('name','=','Custome barcode Report Print')], limit=1)
        record.write({
            'page_height':self.label_height,
            'page_width':self.label_width,
            'margin_top':self.margin_top,
            'margin_bottom':self.margin_bottom,
            'margin_left':self.margin_left,
            'margin_right':self.margin_right,
            'dpi':self.dpi,
        })
