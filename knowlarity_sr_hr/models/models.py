# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ClickCall(models.TransientModel):
    _inherit = 'click.call'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    call_to_whom = fields.Selection([('partner', 'Partner'), ('employee', "Employee")], default='employee')

    @api.onchange('call_to_whom')
    def onchenge_call_to_whom(self):
        if self.call_to_whom == 'employee':
            self.mobile = False
            self.partner_id = False
        elif self.call_to_whom == 'partner':
            self.mobile = False
            self.employee_id = False
        elif not self.call_to_whom and self.mobile and self._context.get('active_model', False) == 'crm.lead':
            self.partner_id = False
            self.employee_id = False
        else:
            self.mobile = False
            self.partner_id = False
            self.employee_id = False

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        field_name = self._context.get('field_name', False)

        if field_name == 'mobile_phone' and self.employee_id:
            self.mobile = self.employee_id.mobile_phone
        elif field_name == 'work_phone' and self.employee_id:
            self.mobile = self.employee_id.work_phone
        elif self.partner_id and not field_name:
            self.mobile = self.employee_id.mobile_phone or self.employee_id.work_phone
