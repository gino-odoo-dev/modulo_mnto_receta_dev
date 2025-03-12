from odoo import models, fields

class Temporadas(models.Model):
    _name = 'cl.product.temporada'
    _description = 'Temporadas'
    _order = 'id'
    _rec_name = 'name'

    name = fields.Char(string="Nombre", required=True)
    