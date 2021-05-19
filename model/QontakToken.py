#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import requests, json
import logging

_logger = logging.getLogger(__name__)
	
class QontakLog(models.Model):

	_name = "qontak.log"
	_description = "qontak_log"
	_order = "date desc"

	date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)
	data = fields.Text(string='Data')

class QontakBot(models.Model):

	_name = "qontak.bot"
	_description = "qontak_bot"

	date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)
	sequence = fields.Integer('Sequence', default=20)
	key = fields.Char(string='Key')
	message = fields.Text(string='Message')

class QontakToken(models.Model):

	_name = "qontak.token"
	_description = "qontak_token"

	access_token = fields.Char( string="Access token")
	token_type = fields.Char( string="Token type")
	refresh_token = fields.Char( string="Refresh token")
	created_at = fields.Datetime( string="Created at")
	expires_in = fields.Datetime( string="Expires in")
	username = fields.Char( string="Username")
	password = fields.Char( string="Password")
	grant_type = fields.Char( string="Grant type")
	client_id = fields.Char( string="Client")
	client_secret = fields.Char( string="Client secret")
	account_type = fields.Selection([('bot', 'Bot'),('admin', 'Admin'),('supervisor', 'Supervisor'),('agent', 'Agent')])

	@api.multi
	def get_token(self):
		headers = {'Content-Type': "application/json"}
		data = {
			"username": self.username,
			"password": self.password,
			"grant_type": self.grant_type,
			"client_id": self.client_id,
			"client_secret": self.client_secret
		}
		response = requests.post("https://chat-service.qontak.com/oauth/token",data=json.dumps(data),headers=headers)
		created_at_timestamp = datetime.datetime.fromtimestamp(response.json()['created_at'])
		expires_in_timestamp = datetime.datetime.fromtimestamp(response.json()['expires_in'])
		created_at = created_at_timestamp.strftime('%Y-%m-%d %H:%M:%S')
		expires_in = expires_in_timestamp.strftime('%Y-%m-%d %H:%M:%S')
		self.write({
			'access_token' :  response.json()['access_token'],
			'token_type' :  response.json()['token_type'],
			'expires_in' : expires_in,
			'refresh_token' :  response.json()['refresh_token'],
			'created_at' :  created_at,
		})

	@api.multi
	def get_template(self):
		token = self.env['qontak.token'].search([('account_type','=','admin')], limit=1)
		headers = {
				"Content-Type" : "application/json",
				"Authorization" : "Bearer "+token.access_token
			}
		data = {}
		response = requests.get("https://chat-service.qontak.com/api/open/v1/templates/whatsapp",data=json.dumps(data),headers=headers)
		template = response.json()
		_logger.info("[GET TEMPLATE] "+json.dumps(template))

		template_old = self.env['qontak.template'].search([])
		template_old.unlink()

		if template['status'] == "success" :
			template_all = template['data']
			_logger.info("[TEMPLATE ALL QONTAK] "+json.dumps(template))
			for temp in template_all:
				create = {}
				create['template_id'] = temp['id']
				create['organization_id'] = temp['organization_id']
				create['name'] = temp['name']
				create['language'] = temp['language']
				if temp['header']:
					header = temp['header']
					create['format'] = header['format']
				create['body'] = temp['body']
				create['footer'] = temp['footer']
				create['status'] = temp['status']
				create['category'] = temp['category']
				template_old.create(create)

	@api.multi
	def get_channel(self):
		token = self.env['qontak.token'].search([('account_type','=','admin')], limit=1)
		headers = {
				"Content-Type" : "application/x-www-form-urlencoded",
				"Authorization" : "Bearer "+token.access_token
			}
		data = "target_channel=wa"
		response = requests.get("https://chat-service.qontak.com/api/open/v1/integrations",data=data,headers=headers)
		channel = response.json()
		_logger.info("[GET CHANNEL] "+json.dumps(channel))

		channel_old = self.env['qontak.channel'].search([])
		channel_old.unlink()

		if channel['status'] == "success" :
			channel_all = channel['data']
			_logger.info("[CHANNEL ALL QONTAK] "+json.dumps(channel_all))
			for chan in channel_all:
				create = {}
				create['template_id'] = chan['id']
				create['target_channel'] = chan['target_channel']
				create['organization_id'] = chan['organization_id']
				create['webhook'] = chan['webhook']
				create['created_at'] = chan['created_at']
				if chan['settings'] :
					setting = chan['settings']
					create['domain_server'] = setting['domain_server']
					create['authorization'] = setting['authorization']
					create['account_name'] = setting['account_name']
					create['server_wa_id'] = setting['server_wa_id']
				channel_old.create(create)
				
				
class QontakTemplate(models.Model):
	_name = "qontak.template"
	_description = "qontak_template"

	template_id = fields.Char(string='ID')
	organization_id = fields.Char(string='Organization ID')
	name = fields.Char(string='Name')
	language = fields.Char(string='Language')
	format = fields.Char(string='Format')
	body = fields.Text(string='Body')
	footer = fields.Char(string='Footer')
	status = fields.Char(string='Status')
	category = fields.Char(string='Category')

class QontakChannel(models.Model):
	_name = "qontak.channel"
	_description = "qontak_channel"

	channel_id = fields.Char(string='ID')
	target_channel = fields.Char(string='Target Channel')
	webhook = fields.Char(string='Webhook')
	domain_server = fields.Char(string='Domain Server')
	authorization = fields.Char(string='Authorization')
	account_name = fields.Char(string='Account_Name')
	server_wa_id = fields.Char(string='Server WA id')
	organization_id = fields.Char(string='Organization ID')
	created_at = fields.Char(string='Created at')
	
