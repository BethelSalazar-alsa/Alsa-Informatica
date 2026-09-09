# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Licencias por Empresa',
    'version': '1.0',
    'summary': 'Gestión de licencias de software Contpaqi y equipos relacionados',
    'description': """
        Módulo para el control de licencias Contpaqi por cliente, 
        así como los equipos vinculados a cada licencia (servidores o terminales).
        Se integra con Contactos, Ventas y Mesa de Ayuda (Helpdesk).
    """,
    'category': 'Sales/Helpdesk',
    'author': 'Alsa Informática',
    'website': 'https://bethel-alsa-desarrollos.github.io',
    'depends': [
        'base',
        'contacts',
        'sale',
        'helpdesk',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/licencia_views.xml',
        'views/equipo_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
