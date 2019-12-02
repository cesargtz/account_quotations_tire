# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from openerp.exceptions import ValidationError, Warning


class ProductDiscount(models.Model):
    _inherit = 'product.product'

    for_discount = fields.Boolean(default=False, string="Aplica descuento")
    discount_level_1 = fields.Float("Descuento Nivel 1", help="Descuento en porcentaje")
    discount_level_2 = fields.Float("Descuento Nivel 2", help="Descuento en porcentaje")
    qty_enable = fields.Integer(string="Cantidad disponible")

class AccountQuotationesLine(models.Model):
    _name = 'accountquotation.line'

    quotation = fields.Many2one('accountquotation.tire')
    product = fields.Many2one('product.product', string="Producto")
    qty = fields.Integer(string="Cantidad")
    price = fields.Float(string="Precio")

    use = fields.Selection([
        ('service', 'Servicio'),
        ('tires', 'Neumaticos'),
    ], default="service")

    discount_price_level_2 = fields.Float(string="Precio con 2")
    discount_price_level_4 = fields.Float(string="Precio con 4")

    @api.onchange('product')
    def onchange_calculate_discount(self):
        self.use = self.quotation.use
        self.price = self.product.lst_price
        if self.product.for_discount:
            self.discount_price_level_2 = (self.price - (self.price * (self.product.discount_level_1 / 100)))
            self.discount_price_level_4 = (self.price - (self.price * (self.product.discount_level_2 / 100)))

class AccountQuotationTire(models.Model):
    _name = 'accountquotation.tire'

    # name = fields.Char(string="Service Number", readonly=True, required=True, copy=False, default='New')
    name = fields.Char('Set Quotation Secuence', required=True, select=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('reg_code_account_quotation'), help="Unique number of account quotation")

    use = fields.Selection([
        ('service', 'Servicio'),
        ('tires', 'Neumaticos'),
    ], default='tires')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
        ('invoiced','Facturado'),
        ('cancel', 'Cancelada'),
    ], default='draft')

    partner = fields.Many2one('res.partner', string="Cliente")
    date = fields.Date(string="Fecha",default=fields.Date.today, required=True)
    quotation_line = fields.One2many('accountquotation.line','quotation', required=True, string="Lina de cotizacion")
    products = fields.Many2many('product.product')
    invoice_create_id = fields.Many2one('account.invoice', readonly=True)


    @api.model
    def create(self,vals):
        res = super(AccountQuotationTire, self).create(vals)
        if not vals['partner']:
            raise exceptions.ValidationError("Favor de elegir un cliente")
        return res

    @api.onchange('products')
    def onchage_all_prodcuts(self):
        result = []
        for product in self.products:
            if product.for_discount:
                discont1 = ((product.lst_price) - (product.lst_price) * (product.discount_level_1 / 100))
                discont2 = ((product.lst_price) - (product.lst_price) * (product.discount_level_2 / 100))
                result.append((0, 0, {'use':'tires' ,'product': product.id, 'price': product.lst_price,
                'discount_price_level_2': discont1,'discount_price_level_4': discont2, }))
            else:
                result.append((0, 0, {'product': product.id, 'price': product.lst_price }))
        self.quotation_line = result


    @api.one
    def quotation_confirm(self):
        if len(self.quotation_line) > 0:
            products_to_invoice = False
            for line in self.quotation_line:
                if line.price == 0:
                    raise exceptions.ValidationError("Revisa que todos los productos tengan precio")
                if line.qty > 0 and products_to_invoice == False:
                    products_to_invoice = True
            if not products_to_invoice:
                 raise exceptions.ValidationError("Favor de agregar los productos a facturar.")
            if line.product.type == 'consu':
                if line.product.qty_enable < line.qty:
                    raise exceptions.Warning("Solo cuentas con %d unidaes del producto %s" % (line.product.qty_enable,line.product.name))
            self.state = 'confirm'
        else:
            raise exceptions.ValidationError("Favor de agregar productos")

    @api.one
    def quotation_cancel(self):
        self.state = 'cancel'

    @api.one
    def quotation_change_draft(self):
        self.state = 'draft'

    @api.multi
    def quotation_make_invoice(self):
        invoice_id = self.env['account.invoice'].create({
            'partner_id' : self.partner.id,
            'account_id' : self.partner.property_account_receivable_id.id,
            'journal_id' : self.env['account.journal'].search([('type','=','sale')], order='id', limit=1).id,
            'type':'out_invoice',
            'date_invoice':self.date,
            'state':'draft',
            })
        self.create_move_id(invoice_id)
        self.invoice_create_id = invoice_id.id
        self.state = 'invoiced'

    @api.multi
    def create_move_id(self, invoice_id):
        products = self.quotation_line
        for product in products:
            if product.qty > 0:
                price = product.price
                if product.product.for_discount:
                    if product.qty >= 2 and product.qty < 4:
                        price = product.discount_price_level_2
                    if product.qty >= 4:
                        price = product.discount_price_level_4
                move_id = self.env['account.invoice.line'].create({
                    'invoice_id': invoice_id.id,
                    'price_unit': price,
                    'product_id': product.product.id,
                    'quantity' : product.qty,
                    'name':product.product.name,
                    # 'invoice_line_tax_ids': product.product.taxes_id.ids,
                    'account_id' : self.env['account.journal'].search([('type','=','sale')], order='id', limit=1).default_credit_account_id.id,
                })


class AccountQuotationInvoice(models.Model):
    _inherit = 'account.invoice'
    
    taxes_compute = fields.Selection([
        ('none', 'Sin Impuesto'),
        ('compute', 'Agregar Impuestos'),
    ])

    @api.onchange('taxes_compute')
    def calculate_taxes(self):
        for line in self.invoice_line_ids:
            line.invoice_line_tax_ids = line.product_id.taxes_id.ids

    @api.multi
    def action_invoice_open(self):
        res = super(AccountQuotationInvoice,self).action_invoice_open()
        if self.type in ('out_invoice','in_refund'):
            for line in self.invoice_line_ids:
                if line.product_id.type == 'consu':
                    line.product_id.write({'qty_enable': ( line.product_id.qty_enable - line.quantity)})
        if self.type in ('in_invoice', 'out_refund'):
            for line in self.invoice_line_ids:
                if line.product_id.type == 'consu':
                    line.product_id.write({'qty_enable': ( line.product_id.qty_enable + line.quantity)})
        return res

    @api.multi
    def action_invoice_cancel(self):
        res = super(AccountQuotationInvoice,self). action_invoice_cancel()
        if self.type in ('out_invoice','in_refund'):
            for line in self.invoice_line_ids:
                if line.product_id.type == 'consu':
                    line.product_id.write({'qty_enable': ( line.product_id.qty_enable + line.quantity)})
        if self.type in ('in_invoice', 'out_refund'):
            for line in self.invoice_line_ids:
                if line.product_id.type == 'consu':
                    line.product_id.write({'qty_enable': ( line.product_id.qty_enable - line.quantity)})
        return res

class AccountQuotationWizard(models.TransientModel):
    _name = 'accountquotation.wizard'

    catg_ids = fields.Many2one('product.category', string="Categoría", required=True)


    @api.multi
    def check_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'catg_ids': self.catg_ids.id,
            },
        }
        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
        return self.env.ref('account_quotation_tire.report_quotation').report_action(self, data=data)

class ReportLocationCalculate(models.AbstractModel):
    _name = 'report.account_quotation_tire.report_quo_wiz'

    @api.model
    def _get_report_values(self, docids, data=None):
        categ_id = data['form']['catg_ids']
        print(categ_id)
        products = self.env['product.product'].search([('categ_id','=',categ_id)])
        products_list = []
        for product in products:
           products_list.append(product)
        print(products_list)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': products_list,
        }