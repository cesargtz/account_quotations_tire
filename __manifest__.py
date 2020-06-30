# -*- coding: utf-8 -*-
{
	'name': "account quotation tire",

	'summary': """
		Short (1 phrase/line) summary of the module's purpose, used as
		subtitle on modules listing or apps.openerp.com""",

	'description': """
		Long description of module's purpose
	""",

	'author': "Cesar Gtz",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
	# for the full list
	'category': 'Uncategorized',
	'version': '0.1',

	# any module necessary for this one to work correctly
	'depends': ['base','account','product',],

	# always loaded
	'data': [
		'security/ir.model.access.csv',
		'views/views.xml',
		'views/report_quotation.xml',
		'views/report_service_order.xml',
		'views/wizard_report.xml',
		'views/service_order.xml',
		'views/credit_view.xml',
		# 'views/templates.xml',
	],
	# only loaded in demonstration mode
	'demo': [
		'demo/demo.xml',
	],
}
