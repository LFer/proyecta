# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug

from odoo.api import Environment
import odoo.http as http

from odoo.http import request
from odoo import SUPERUSER_ID
from odoo import registry as registry_get
import ipdb

class ProjectTaskController(http.Controller):


    @http.route('/versolicitud', type='http', auth="public")
    def versolicitud(self, db, token, action, id):
        return self.view(db, token, action, id, view='form')



    @http.route('/view', type='http', auth="public")
    def view(self, db, token, action, id, view='calendar'):
        registry = registry_get(db)
        with registry.cursor() as cr:
            # Since we are in auth=none, create an env with SUPERUSER_ID
            env = Environment(cr, SUPERUSER_ID, {})
            attendee = env['project.task'].search([('access_token', '=', token), ('id', '=', int(id))])
            if not attendee:
                return request.not_found()
            return werkzeug.utils.redirect('/web?db=%s#id=%s&view_type=form&model=project.task' % (db, id))


