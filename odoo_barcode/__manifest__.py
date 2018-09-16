# -*- coding: utf-8 -*-
{
    'name': "odoo_barcode",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product'],

    'qweb' : [],

    'data': [
        # 'security/ir.model.access.csv',
        'views/config_views.xml',
        'static/src/xml/report_template.xml',
        'views/report.xml',
        'wizards/barcode_report_wizard.xml',
        'security/security_group.xml',
        'security/ir.model.access.csv'
    ],

}