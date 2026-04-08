{
    'name': 'Gestión de Licencias Contpaqi',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Administración de series y vencimientos de software',
    'author': 'Alsa',
    'depends': ['base', 'contacts', 'sale', 'mail', 'helpdesk', 'website', 'website_sale'], 
    'data': [
        'security/ir.model.access.csv',
        'data/ir.cron.xml',
        'views/licencia_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/helpdesk_ticket_views.xml', 
        'views/website_form_licencia.xml',
        'views/website_snippets.xml',
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
