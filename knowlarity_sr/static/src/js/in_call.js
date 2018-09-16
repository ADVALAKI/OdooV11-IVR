odoo.define('knowlarity_sr.in_call', function(require) {
    "use strict";
    var socket = io.connect('https://api.knowlarity.com:8089/');
    var rpc = require('web.rpc');
    var session = require('web.session');

    socket.emit('feedapp', '98e27342-b121-4a18-a4dc-afee3e63ad5b');
    socket.on('message', function(msg) {
        msg = msg.replace(/\'/g, '\"');
        var json_msg = JSON.parse(msg);
        create_log(json_msg)
    });

    function create_log(data) {
        rpc.query({
            model: 'knowlarity.number',
            method: 'search',
            args: [
                [
                    ['name', '=', data['dispnumber']]
                ]
            ]
        }).then(function(result) {
            console.log(result)
            result.length ? rpc.query({
                model: 'call.log',
                method: 'create',
                args: [{
                    knowlarity_number: result[0],
                    agent_number: data['destination'],
                    customer_number: data['caller_id'],
                    uuid: data['callid'],
                    business_call_type: data['action'],
                    call_type: '0'
                }],
                kwargs: {
                    context: session.user_context
                }
            }) : alert('Configurations not configured correctly.');
        });
    }

    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');

    var ClickCallMenu = Widget.extend({
        template: 'ClickCallMenu',

        events: {
            "click.object": "ClickCallMenu",
        },

        ClickCallMenu: function() {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'click.call',
                view_mode: 'form',
                view_type: 'form',
                views: [
                    [false, 'form']
                ],
                target: 'new',
            });
        }

    });

    SystrayMenu.Items.push(ClickCallMenu);

});