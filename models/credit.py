# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class product_category_commission(models.Model):
    _inherit = 'product.category'

    interests = fields.Float(string='Interes', help="Usar numeros enteros, por ejemplo: 10 porciento de interes.")

