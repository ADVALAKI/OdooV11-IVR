# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from urllib.parse import urlencode

import pytz
import requests
from dateutil.parser import parse
from odoo import models, fields, api

from ..utils import call

_logger = logging.getLogger(__name__)
limit = 10000000000000000000


class KnowlarityNumber(models.Model):
    _name = 'knowlarity.number'

    name = fields.Char(string='Knowlarity Number', required=True)
    api = fields.Many2one('sr.api', string='API', required=True)


class SrApi(models.Model):
    _name = 'sr.api'
    _rec_name = 'x_api_key'

    channel = fields.Char(string='Channel', required=True)
    x_api_key = fields.Char(string='API Key', required=True)
    authorization = fields.Char(string='Authorization Key', required=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    knowlarity_agent = fields.Boolean(string="Is a Super Receptionist Agent")
    knowlarity_numbers = fields.Many2many('knowlarity.number', string="Knowlarity Number")


class CallLog(models.Model):
    _name = 'call.log'
    _order = 'start_time desc'
    _rec_name = 'customer_number'

    @api.one
    @api.depends('agent_number')
    def _compute_agent_id(self):
        agent = self.env['res.partner'].search(
            ['|', ('phone', '=', self.agent_number), ('mobile', '=', self.agent_number)])
        self.agent_id = agent and agent.id

    customer_number = fields.Char(string="Caller", help="Phone number of the agent(Outgoing) or customer (Incoming)")
    uuid = fields.Char(string="UUID", required=True)
    agent_number = fields.Char(string="Agent Number", help="Phone number of the customer(Outgoing) or agent (Incoming)")
    agent_id = fields.Many2one('res.partner', string='Agent', compute=_compute_agent_id, store=True)
    call_duration = fields.Char('Duration (In Seconds)', help="Duration for which the call was active (in seconds)")
    business_call_type = fields.Char("Communication Type")
    call_type = fields.Selection((('0', 'Incoming'), ('1', 'Outgoing')), string="Call Type", )
    knowlarity_number = fields.Many2one('knowlarity.number')
    start_time = fields.Datetime()
    state = fields.Selection((('answered', 'Answered'), ('missed', 'Call Missed')), string='Status')
    call_recording = fields.Char('Call Record')

    def sync(self):
        logs = self.env['call.log'].search([])
        url = "https://kpi.knowlarity.com/Basic/v1/account/calllog"
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
        }
        now_local = fields.Datetime.context_timestamp(self, datetime.now())

        for each in logs:
            query = {
                'end_time': str(now_local),
                'limit': limit,
            }
            headers.update({
                'channel': each.knowlarity_number.api.channel,
                'x-api-key': each.knowlarity_number.api.x_api_key,
                'authorization': each.knowlarity_number.api.authorization
            })
            url_with_query = url + '?%s' % urlencode(query)
            response = requests.request("GET", url_with_query, data={}, headers=headers)
            response_text = eval(response.text)
            objects = response_text.get('objects')

            log = list(filter(lambda x: each.uuid == x.get('uuid'), objects))

            if log:
                state = 'Missed' in log[0].get('agent_number')
                start_time = parse(log[0].get('start_time')).astimezone(pytz.utc)
                each.write({'call_duration': log[0].get('call_duration'),
                            'business_call_type': log[0].get('business_call_type'),
                            'call_recording': log[0].get('call_recording'),
                            'start_time': start_time,
                            'state': 'missed' if state else 'answered',
                            })

    def get_log_all(self):
        existing_logs = self.search([])
        existing_logs_uuid = [x.uuid for x in existing_logs]
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
        }
        url = "https://kpi.knowlarity.com/Basic/v1/account/calllog?%s" % urlencode({'limit': limit})

        for sr in self.env['knowlarity.number'].search([]):
            headers.update({
                'channel': sr.api.channel,
                'x-api-key': sr.api.x_api_key,
                'authorization': sr.api.authorization
            })
            response = requests.request("GET", url, data={}, headers=headers)
            response_text = eval(response.text)
            objects = response_text.get('objects')
            uuids = [x.get('uuid') for x in objects]

            new_uuids = set(uuids) - set(existing_logs_uuid)
            for uuid in new_uuids:
                log = list(filter(lambda x: uuid == x.get('uuid'), objects))

                if log:
                    state = 'Missed' in log[0].get('agent_number')
                    start_time = parse(log[0].get('start_time')).astimezone(pytz.utc)
                    self.create({
                        'customer_number': log[0].get('customer_number'),
                        'agent_number': log[0].get('destination'),
                        'knowlarity_number': sr.id,
                        'uuid': log[0].get('uuid'),
                        'call_type': str(log[0].get('Call_Type')) or '',
                        'call_duration': log[0].get('call_duration'),
                        'business_call_type': log[0].get('business_call_type'),
                        'call_recording': log[0].get('call_recording'),
                        'start_time': start_time,
                        'state': 'missed' if state else 'answered',
                    })


class ScheduleCall(models.Model):
    _name = 'schedule.call'
    _rec_name = 'partner_id'

    @api.multi
    def _default_knowlarity_numbers(self):
        if self.env.user.partner_id.knowlarity_agent:
            if len(self.env.user.partner_id.knowlarity_numbers) == 1:
                return self.env.user.partner_id.knowlarity_numbers

    partner_id = fields.Many2one('res.partner', string="Partner")
    mobile = fields.Char(string="Mobile")
    cron_time = fields.Datetime(string="Date")
    agent_id = fields.Many2one('res.partner', string="Agent")
    knowlarity_number = fields.Many2one('knowlarity.number', string="Knowlarity-Number",
                                        default=_default_knowlarity_numbers)
    state = fields.Selection((('draft', 'Draft'), ('done', 'Done')), string='Status', default='draft')

    @api.multi
    def schedule_call(self):
        for each in self.search([('state', '=', 'draft')]):
            scheduled_time = fields.Datetime.from_string(each.cron_time)

            if scheduled_time < datetime.now():
                res = call(k_number=each.knowlarity_number.name,
                           agent_number=each.agent_id.mobile,
                           customer_number=each.mobile,
                           x_api_key=each.knowlarity_number.api.x_api_key,
                           authorization=each.knowlarity_number.api.authorization)
                success = res.get('success', False)
                error = res.get('error', False)
                invalid = res.get('message', False)

                if success:
                    each.write({'state': 'done'})
                    self.env['call.log'].create({
                        'uuid': success.get('call_id'),
                        'agent_number': each.agent_id.mobile,
                        'customer_number': each.mobile,
                        'knowlarity_number': each.knowlarity_number.id,
                        'call_type': '1',
                    })
                if error:
                    _logger.error(error)

                if invalid:
                    _logger.error(invalid)



    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.mobile = self.partner_id.mobile

    @api.onchange('agent_id')
    def _onchange_agent(self):
        return {'domain': {'knowlarity_number': [('id', 'in', self.agent_id.knowlarity_numbers.ids)]}}
