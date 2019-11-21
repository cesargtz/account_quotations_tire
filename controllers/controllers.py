# -*- coding: utf-8 -*-
from odoo import http

# class Addons/accountQuotationTire(http.Controller):
#     @http.route('/addons/account_quotation_tire/addons/account_quotation_tire/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/addons/account_quotation_tire/addons/account_quotation_tire/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('addons/account_quotation_tire.listing', {
#             'root': '/addons/account_quotation_tire/addons/account_quotation_tire',
#             'objects': http.request.env['addons/account_quotation_tire.addons/account_quotation_tire'].search([]),
#         })

#     @http.route('/addons/account_quotation_tire/addons/account_quotation_tire/objects/<model("addons/account_quotation_tire.addons/account_quotation_tire"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('addons/account_quotation_tire.object', {
#             'object': obj
#         })