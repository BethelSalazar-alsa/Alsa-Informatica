import datetime
from odoo import models, fields, api

class LicenciaContpaqi(models.Model):
    _name = 'licencia.contpaqi'
    _description = 'Gestión de Licencias'
    # Añadimos 'website.published.mixin' para habilitar funciones web
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Número de Serie', required=True, tracking=True)
    
    # Nuevo: Selector para otros tipos de software
    software_type = fields.Selection([
        ('contpaqi', 'CONTPAQi'),
        ('office', 'Microsoft Office'),
        ('antivirus', 'Antivirus'),
        ('otro', 'Otro')
    ], string='Tipo de Software', default='contpaqi', required=True, tracking=True)

    partner_id = fields.Many2one('res.partner', string='Cliente', required=False, index=True, 
                                 default=lambda self: self.env.context.get('default_partner_id'))
    fecha_vencimiento = fields.Date(string='Fecha de Vencimiento', tracking=True)
    vendedor_id = fields.Many2one('res.users', string='Vendedor', default=lambda self: self.env.user)
    linea_ids = fields.One2many('licencia.linea', 'licencia_id', string='Equipos')
    
    state = fields.Selection([
        ('activa', 'Activa'),
        ('renovada', 'Renovada'),
        ('cancelada', 'Cancelada')
    ], string='Estado', default='activa', tracking=True)

    def action_set_renovada(self):
        self.state = 'renovada'

    def action_set_cancelada(self):
        self.state = 'cancelada'

    @api.model
    def _cron_revisar_vencimientos_escalonados(self):
        """ Revisa vencimientos a 30, 15 y 10 días para todos los tipos de software """
        hoy = fields.Date.today()
        alertas = [30, 15, 10]
        
        for dias in alertas:
            fecha_busqueda = hoy + datetime.timedelta(days=dias)
            licencias = self.search([
                ('fecha_vencimiento', '=', fecha_busqueda),
                ('state', '=', 'activa')
            ])
            
            for licencia in licencias:
                # 1. Crear Actividad para el Vendedor (Identificando el tipo de software)
                licencia.activity_schedule(
                    'mail.mail_activity_data_todo',
                    date_deadline=licencia.fecha_vencimiento,
                    summary=f"Vencimiento {licencia.software_type.upper()} en {dias} días",
                    note=f"La serie {licencia.name} vence pronto. Cliente: {licencia.partner_id.name}",
                    user_id=licencia.vendedor_id.id
                )
                
                # 2. Correo al Chatter (Notifica al Cliente y Vendedor)
                body = f"""
                    <div style="font-family: sans-serif;">
                        <p>Estimado/a <b>{licencia.partner_id.name}</b>,</p>
                        <p>Le recordamos que su licencia de <b>{licencia.software_type.upper()}</b> (Serie: {licencia.name}) 
                        está próxima a vencer en <b>{dias} días</b> ({licencia.fecha_vencimiento}).</p>
                        <p>Favor de contactar a su ejecutivo para su renovación.</p>
                    </div>
                """
                licencia.message_post(
                    body=body,
                    partner_ids=[licencia.partner_id.id, licencia.vendedor_id.partner_id.id],
                    subtype_xmlid="mail.mt_comment"
                )

    @api.model
    def website_form_input_filter(self, request, values):
        # Esto le dice a Odoo: "Si alguien envía datos desde la web, acéptalos"
        if 'name' in values:
            # Forzamos el tipo de software si no viene en el form
            values.setdefault('software_type', 'contpaqi')
            # Asignamos el partner_id si el usuario está logueado
            if not values.get('partner_id') and request.env.user.partner_id:
                values['partner_id'] = request.env.user.partner_id.id
        return values



class LicenciaLinea(models.Model):
    _name = 'licencia.linea'
    _description = 'Equipos por Licencia'
    _rec_name = 'nombre_equipo'

    licencia_id = fields.Many2one('licencia.contpaqi', string='Licencia', ondelete='cascade')    
    nombre_equipo = fields.Char(string='Nombre del Equipo', required=True)
    tipo = fields.Selection([('terminal', 'Terminal'), ('servidor', 'Servidor')], default='terminal')
    caracteristicas = fields.Text(string='Características')
    # Campos adicionales para el formulario web
    empleado_id = fields.Many2one('res.users', string='Empleado asignado')
    producto_relacionado = fields.Char(string='Producto/Software') # O Many2one a product.product
    vencimiento_id = fields.Date(string='Fecha Vencimiento')