# -*- coding: utf-8 -*-

import json
import logging, requests
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class ApiWebhook(http.Controller):

	def send_message(self,room_id,text):
		token = request.env['qontak.token'].sudo().search([('account_type','=','bot')], limit=1)
		if token : 
			headers = {
				"Content-Type" : "application/json",
				"Authorization" : "Bearer "+token.access_token
			}
			data = {
				"room_id": room_id,
				"type": "text",
				"text": text
			}
			response = requests.post("https://chat-service.qontak.com/api/open/v1/messages/whatsapp/bot",data=json.dumps(data),headers=headers)
			status = response.json()
			if status['status'] == "error":
				code = status['error']['code']
				message = status['error']['messages']
				_logger.info("[ERORR QONTAK] {0} | {1}".format(code,message))
				return False
			else:
				return True
		else:
			_logger.info("[ERORR QONTAK] TOKEN NOT FOUND")
			return False

	def get_message(self,data):
		if data['participant_type'] == "customer":
			_logger.info('GET MESSAGE SUCCESSFUL!!')
			room_id = data['room']['id']
			name = data['room']['name']
			account_uniq_id = data['room']['account_uniq_id']
			text = data['text']
			chat = request.env['qontak.bot'].sudo().search([('key','=',text)], limit=1)
			if chat:
				status = self.send_message(room_id,chat.message)
				_logger.info('SSTATUS : ' + str(status))

	@http.route(['/api/whatsapp'], type="json", auth="public", method=['POST'], csrf=False)
	def qontak_webhook(self, **post):
		_logger.info('CONNECTION SUCCESSFUL!!')
		json_req = request.jsonrequest
		# _logger.info('SPOST : ' + json.dumps(json_req))
		values={}
		if json_req :
			create = {}
			create['data'] = json.dumps(json_req)
			# _logger.info('SRL : ' + str(create))
			data = request.env['qontak.log'].sudo().create(create)
			self.get_message(json_req)

			if data :
				values['id'] = str(data.id)
				values['success'] = True
			else:
				values['success'] = False
				values['error_code'] = 202
				values['error_data'] = 'Create Error'
		else:
			values['success'] = True
			values['error_code'] = 404
			values['error_data'] = 'No params found!'
		return json.dumps(values)