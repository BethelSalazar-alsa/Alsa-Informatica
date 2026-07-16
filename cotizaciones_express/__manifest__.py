{
    'name': 'Cotizaciones Express',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Cotizaciones con vista dividida y previsualización de PDF en tiempo real',
    'author': 'Alsa Informática',
    'depends': ['base', 'contacts', 'sale', 'crm', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/seller_signature_views.xml',
        'views/cotizacion_views.xml',
        'report/cotizacion_preview.xml',
        'data/mail_template.xml',
    ],
    'report': {
        'cotizaciones_express.report_cotizacion_express': {
            'report_type': 'qweb-pdf',
            'model': 'cotizacion.express',
            'name': 'cotizaciones_express.cotizacion_preview_template',
            'file': 'cotizaciones_express.cotizacion_preview_template',
            'print_report_name': "'Cotizacion_' + (object.name or '')",
        },
    },
    'assets': {
        'web.assets_backend': [
            'cotizaciones_express/static/src/js/cotizacion_preview.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
