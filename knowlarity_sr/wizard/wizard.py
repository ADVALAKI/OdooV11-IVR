from odoo import models, fields, api, _
from odoo.exceptions import UserError

from ..utils import call


class ClickCall(models.TransientModel):
    _name = 'click.call'

    @api.multi
    def _current_user(self):
        if self.env.user.partner_id.knowlarity_agent:
            return self.env.user.partner_id
    # @api.multi
    # def _get_mobile(self):
    #     print('\n---',self._context,'--self_contetxt--\n')
    #     model = self._context.get('active_model')
    #     print('\n---',model,'--model--\n')
    #     active_id = self._context.get('active_id')
    #     print('\n---',active_id,'--active_id--\n')

    #     if model == 'call.log':
    #         log = self.env[model].browse(active_id)
    #         print('\n---',log.customer_number,'--log--\n')
    #         return log.customer_number

    @api.multi
    def _knowlarity_num(self):
        if self.env.user.partner_id.knowlarity_agent:
            if len(self.env.user.partner_id.knowlarity_numbers) == 1:
                return self.env.user.partner_id.knowlarity_numbers

    partner_id = fields.Many2one('res.partner', string="Partner")
    mobile = fields.Char('Mobile', required=True)
    agent = fields.Many2one('res.partner', string="Agent", default=_current_user,
                            domain=[('knowlarity_agent', '=', True)])
    knowlarity_number = fields.Many2one('knowlarity.number', default=_knowlarity_num, string="SR Number")


    @api.multi
    def click_call(self):
        res = call(k_number=self.knowlarity_number.name, agent_number=self.agent.mobile, customer_number=self.mobile,
                   x_api_key=self.knowlarity_number.api.x_api_key,
                   authorization=self.knowlarity_number.api.authorization)
        success = res.get('success', False)
        error = res.get('error', False)
        invalid = res.get('message', False)
        if success:
            self.env['call.log'].create({
                'uuid': success.get('call_id'),
                'agent_number': self.agent.mobile,
                'customer_number': self.mobile,
                'knowlarity_number': self.knowlarity_number.id,
                'call_type': '1',
            })
            return {
                'name': 'Success',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.pop.message',
                'target': 'new',
                'context': {'default_name': success.get('message')}
            }
        elif error:
            raise UserError(_(error.get('message')))
        else:
            raise UserError(_(res.get('message') + ' Check agent mobile number'))

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        print('\n---',self._context,'--context\n')
        field_name = self._context.get('field_name', False)
        print('\n---',field_name,'--context\n')

        if field_name == 'mobile' and self.partner_id:
            self.mobile = self.partner_id.mobile
        elif field_name == 'phone' and self.partner_id:
            self.mobile = self.partner_id.phone
        elif self.partner_id and not field_name:
            self.mobile = self.partner_id.mobile or self.partner_id.phone

    @api.onchange('agent')
    def _onchange_agent(self):
        return {'domain': {'knowlarity_number': [('id', 'in', self.agent.knowlarity_numbers.ids)]}}


class CustomPopMessage(models.TransientModel):
    _name = "custom.pop.message"

    name = fields.Char('Message', readonly=True)
