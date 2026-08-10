{
    'name': 'Gestión de Licencias Contpaqi',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Administración de series y vencimientos de software',
    'author': 'Alsa',
    'depends': ['base', 'contacts', 'sale', 'mail', 'helpdesk', 'hr_timesheet'], 
    'data': [
        # Security must be loaded first
        'security/ir.model.access.csv',
        # Views for base model (licencia.contpaqi) must be loaded before inherited views
        'views/licencia_views.xml',
        # Inherited views for other models
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/helpdesk_ticket_views.xml',
        # Cron jobs last
        'data/ir_cron.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
