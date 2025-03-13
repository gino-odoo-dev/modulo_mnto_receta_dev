from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RecetaFicha(models.Model):
    _name = 'receta.ficha'
    _description = 'Receta ficha tecnica'
    _rec_name = 'nombre_receta'
    _order = 'id asc'

    name = fields.Char(string='Name')
    temporadas_id = fields.Many2one('cl.product.temporada', string='Temporadas')
    temporada_name = fields.Char(string='Nombre de Temporada', compute='_compute_temporada_name', store=True)
    articulos_id = fields.Many2one('cl.product.articulo', string='Articulos')
    articulo_name = fields.Char(string='Nombre de Articulo', compute='_compute_articulo_name', store=True)

    descripcion = fields.Text(string='Descripcion', related='componente_id.descripcion', store=False, readonly=True)
    codigosec_id = fields.Many2one('codigosec.model', string='codigo', readonly=False)
    componente_id = fields.Many2one('componente.model', string='Componente', readonly=False)
    umedida = fields.Char(string='Umedida', related='componente_id.um', store=False, readonly=True)
    depto_id = fields.Many2one('depto.model', string='Departamento', readonly=False)
    codigodepto = fields.Char(string='Codigo Departamento', related='depto_id.codigo', store=False, readonly=True)
    descripciondepto = fields.Text(string='Descripcion Departamento', related='depto_id.descripcion', store=False, readonly=True)
    comp_manu_id = fields.Many2one('compmanu.model', string='CM', readonly=False)
    fact_perdida_id = fields.Float(string='Factor de Perdida (%)', readonly=False)
    cantidad_id = fields.Integer(string='Cantidad', readonly=False)
    c_unitario_id = fields.Float(string='Costo Unitario', readonly=False)
    c_ampliado_id = fields.Float(string='Costo Ampliado', compute='calcular_costo_ampliado', store=True, readonly=True, widget="integer")
    nombre_receta = fields.Char(string='Nombre de la receta', compute='_compute_nombre_receta', store=True, readonly=True)
    copiaficha = fields.Many2one('copia.ficha', string='Copia Ficha', readonly=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('next', 'Next'),
        ('done', 'Done')
    ], string='State', default='draft')

    @api.depends('articulos_id', 'temporadas_id')
    def _compute_nombre_receta(self):
        for record in self:
            articulo_nombre = record.articulos_id.name if record.articulos_id else "Sin Nombre"
            temporada_nombre = record.temporadas_id.name if record.temporadas_id else "Sin Temporada"
            record.nombre_receta = f"\u00A0\u00A0 Articulo: {articulo_nombre} \u00A0\u00A0\u00A0\u00A0\u00A0 Temporada: {temporada_nombre}"
    
    @api.depends('temporadas_id')
    def _compute_temporada_name(self):
        for record in self:
            record.temporada_name = getattr(record.temporadas_id, 'name', "Sin Temporada")

    @api.depends('articulos_id')
    def _compute_articulo_name(self):
        for record in self:
            record.articulo_name = getattr(record.articulos_id, 'name', "Sin Nombre")

    @api.depends('cantidad_id', 'fact_perdida_id', 'c_unitario_id')
    def calcular_costo_ampliado(self):
        for record in self:
            if record.cantidad_id and record.fact_perdida_id and record.c_unitario_id:
                if record.fact_perdida_id > 0:
                    cantidad_perdida = (record.cantidad_id * record.fact_perdida_id) / 100
                    record.c_ampliado_id = int(round(cantidad_perdida * record.c_unitario_id))
                else:
                    record.c_ampliado_id = 0
            else:
                record.c_ampliado_id = 0

    def name_get(self):
        result = []
        for record in self:
            if self.env.context.get('form_view'):
                nombre = record.nombre_receta if record.nombre_receta else "Articulo: Sin Nombre"
                result.append((record.id, nombre))
        return result
    
    def next_button(self):
        self.ensure_one()
        self.write({'state': 'next'})
        
        # Update all fields of receta.ficha
        self._compute_nombre_receta()
        self._compute_temporada_name()
        self._compute_articulo_name()
        self.calcular_costo_ampliado()
        
        # Update fields of copia.ficha
        copia_ficha = self.env['copia.ficha'].search([], limit=1)
        if copia_ficha:
            copia_ficha.write({
                'part_o': self.id,
                'part_d': self.articulos_id.id,
                'temporadas_id': self.temporadas_id.id
            })
            copia_ficha._compute_temporada_name()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'receta.ficha',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {
                'default_articulos_id': self.articulos_id.id,
                'search_default_articulos_id': self.articulos_id.id,
            },
            'domain': [('articulos_id', '=', self.articulos_id.id)],
        }

    @api.onchange('componente_id')
    def _onchange_componente_id(self):
        if self.componente_id:
            self.descripcion = self.componente_id.descripcion or ''
            self.umedida = self.componente_id.um or ''
        else:
            self.descripcion = ''
            self.umedida = ''

#funcion actualiza los registros de maner automatica
    @api.model
    def create(self, vals):
        record = super(RecetaFicha, self).create(vals)
        record._compute_nombre_receta()
        record._compute_temporada_name()
        record._compute_articulo_name()
        record.calcular_costo_ampliado()
        return record
    