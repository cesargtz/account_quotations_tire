# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions



class ServiceOrderLine(models.Model):
	_name = 'service.order.line'

	service_order_id = fields.Many2one('service.order')
	description = fields.Char("Descripción")
	product_id = fields.Many2one('product.product')
	qty = fields.Float(string="Cantidad")

	@api.onchange('product_id')
	def _change_product_description(self):
		self.description = self.product_id.name

class ServiceOrder(models.Model):
	_name = 'service.order'

	name = fields.Char('Set service order secuence', required=True, select=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('reg_code_order_service_seq'), help="Unique number of service order")
	brand = fields.Char(required=True, string="Marca")
	model = fields.Char(required=True, string="Modelo")
	year = fields.Char(required=True, string="Año")
	forxfor = fields.Boolean(string="4x4")
	motor = fields.Char(strng="Motor")
	km = fields.Float(string="Km")
	work_to_do = fields.Text(required=True, string="Trabajo a realizar")
	# vehicle = fields.Char(string="vehículo")
	# partner_id = fields.Many2one('res.partner', 'Vendedor', readonly=True, related="contract_id.partner_id")
	owner = fields.Many2one('res.partner', required=True, string="Dueño")
	phone_owner = fields.Char(string=' Numero celular', readonly=True, related="owner.mobile")
	# phone_owner = fields.Char(string="Telefono")
	assigned_to = fields.Char(required=True, string="Asignado a")
	date = fields.Datetime(required=True, string="Fecha", default=fields.Datetime.now)
	state = fields.Selection([
		('draft', 'Borrador'),
		('quoted', 'Cotizado'),
		('in_progress', 'En progreso'),
		('finished', 'Terminado'),
		('cancel', 'Cancelado'),
	], default="draft")
	quotation_id = fields.Many2one('accountquotation.tire')
	service_order_line = fields.One2many('service.order.line','service_order_id', required=True, string="Lineas de Servicio")
	# company =lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('service.order'))


	@api.one
	def quotation_confirm(self):
		quotation_id = self.env['accountquotation.tire'].create({
			'partner': self.owner.id,
			'date': self.date,
			'service_order':self.id
		})
		for line in self.service_order_line:
			quotation_line = self.env['accountquotation.line'].create({
				'quotation': quotation_id.id,
				'product': line.product_id.id,
				'description': line.description,
				'qty': line.qty,
				'price':  line.product_id.lst_price,
			})
		self.quotation_id = quotation_id.id
		self.state = 'quoted'

	@api.one
	def in_progress(self):
		self.state = 'in_progress'

	@api.one
	def cancel(self):
		self.state = 'cancel'

	@api.one
	def finished(self):
		self.state = 'finished'

	@api.one
	def to_draft(self):
		self.state = 'draft'

	@api.one
	def cancel_finished(self):
		self.state = 'cancel'
