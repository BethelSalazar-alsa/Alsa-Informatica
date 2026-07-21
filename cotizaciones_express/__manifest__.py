{
    'name': 'Cotizaciones Express',
    'version': '19.0.1.0.21',
    'category': 'Sales',
    'summary': 'Cotizaciones con vista dividida y previsualización de PDF en tiempo real',
    'author': 'Alsa Informática',
    'depends': ['base', 'contacts', 'sale', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/stages.xml',
        'views/seller_signature_views.xml',
        'views/cotizacion_views.xml',
        'report/cotizacion_preview.xml',
        'report/cotizacion_report.xml',
        'data/mail_template.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'cotizaciones_express/static/src/css/cotizacion_form.css',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
