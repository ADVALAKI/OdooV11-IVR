# -*- coding: utf-8 -*-
{
    'name': "Knowlarity’s IVR System",

    'summary': """Multi-level IVR System for your business""",

    'description': """
        Power your business communication by greeting them with a professional IVR when they call your business, and routing them to the right team based on their input.
    """,

    'author': "Jothimani R / Prabakaran R",
    'website': "https://www.linkedin.com/in/rjothimani/",
    'category': 'Discuss',
    'version': '0.1',
    'depends': ['base', 'web', 'audio_field'],
    'data': [
        'wizard/wizard_views.xml',
        'security/security.xml',
        'views/templates.xml',
        'views/views.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/nav_bar.xml',
    ],
}
