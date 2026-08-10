import datetime
from odoo import models, fields, api


class LicenciaContpaqi(models.Model):
    _name = 'licencia.contpaqi'
    _description = 'Gestión de Licencias'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Número de Serie', required=True, tracking=True)
    
    # Nuevo: Selector para otros tipos de software
    software_type = fields.Selection([
        ('contpaqi', 'CONTPAQi'),
        ('office', 'Microsoft Office'),
        ('antivirus', 'Antivirus'),
        ('otro', 'Otro')
    ], string='Tipo de Software', default='contpaqi', required=True, tracking=True)

    # NUEVOS CAMPOS PARA EVITAR REDUNDANCIA
    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta Relacionada', 
                                      tracking=True, help='La venta de donde viene esta licencia')
    product_id = fields.Many2one('product.product', string='Producto', tracking=True, 
                                  help='Detectado automáticamente desde la venta')
    
    partner_id = fields.Many2one('res.partner', string='Cliente', required=False, index=True, 
                                 default=lambda self: self.env.context.get('default_partner_id'),
                                 help='Se pre-carga desde la venta si existe')
    fecha_vencimiento = fields.Date(string='Fecha de Vencimiento', tracking=True)
    vendedor_id = fields.Many2one('res.users', string='Vendedor', default=lambda self: self.env.user)
    linea_ids = fields.One2many('licencia.linea', 'licencia_id', string='Equipos')
    
    state = fields.Selection([
        ('activa', 'Activa'),
        ('renovada', 'Renovada'),
        ('cancelada', 'Cancelada')
    ], string='Estado', default='activa', tracking=True)

    # ONCHANGE: Cuando se selecciona una venta, pre-carga cliente y producto
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        """Auto-carga el cliente y producto desde la venta seleccionada"""
        if self.sale_order_id:
            # Pre-cargar el cliente de la venta
            self.partner_id = self.sale_order_id.partner_id
            
            # Buscar producto licenciable en las líneas de la venta
            for line in self.sale_order_id.order_line:
                if line.product_id and line.product_id.type in ['service', 'product']:
                    self.product_id = line.product_id
                    break
        else:
            # Si se quita la venta, limpiar producto
            self.product_id = False

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
        """Filter and validate data from website form submissions"""
        if 'name' in values:
            # Ensure software_type is set
            values.setdefault('software_type', 'contpaqi')
            # Assign partner_id if user is logged in
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