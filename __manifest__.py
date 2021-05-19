#-*- coding: utf-8 -*-

{
	"name": "Qontak webhook",
	"version": "1.0", 
	"depends": [
		'base'
	],
	"author": "Legian Wahyu P",
	"category": "Utility",
	"website": "https://github.com/legianwp18",
	"images": ["static/description/images/main_screenshot.jpg"],
	"price": "10",
	"license": "OPL-1",
	"currency": "USD",
	"summary": "Aplikasi ini mengintegrasikan/menghubungkan antara Odoo dengan Whatsapp Official (Qontak)",
	"description": """

Information
======================================================================

* created menus
* created objects
* created views
* logics

""",
	"data": [
		"security/ir.model.access.csv",
		"view/menu.xml",
		"view/qontak_token.xml",
		"view/qontak_log.xml",
		"view/qontak_bot.xml",
		"report/qontak_token.xml",
	],
	"installable": True,
	"auto_install": False,
	"application": True,
}