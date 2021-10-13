# -*- coding: utf-8 -*-
import ipdb
from odoo import models, fields, api
import uuid

class ProjectTask(models.Model):
    _inherit = "project.task"

    def _default_access_token(self):
        return uuid.uuid4().hex

    access_token = fields.Char('Invitation Token', default=_default_access_token)

    def get_email_to(self):
        users_to_notify = self.project_id.members
        users_to_send = ''
        if len(users_to_notify) > 1:
            lastindex = len(users_to_notify)
            _iter = 0
            for user in users_to_notify:
                _iter += 1
                if lastindex != _iter:
                    users_to_send += user.login + ';'
                if lastindex == _iter:
                    users_to_send += user.login
        return users_to_send

    def get_response_name(self):
        users_to_nofity = self.project_id.members
        users_to_send = ''
        if len(users_to_nofity) > 1:
            lastindex = len(users_to_nofity)
            _iter = 0
            for user in users_to_nofity:
                _iter += 1
                if lastindex != _iter:
                    users_to_send += user.name + ','
                if lastindex == _iter:
                    users_to_send += user.name

        else:
            users_to_send = users_to_nofity.name
        return users_to_send
