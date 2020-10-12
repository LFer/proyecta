# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2015 Techrifiv Solutions Pte Ltd
# Copyright 2015 Statecraft Systems Pte Ltd
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models



class ProjectTask(models.Model):
    _inherit = 'project.task'


    task_type = fields.Selection(selection=[
        ('draft', 'Undefined'),
        ('help', 'Help'),
        ('improvement', 'Improvement'),
        ('block', 'Blocking'),
        ('bug', 'Bug')
    ], string='Task Type', default='draft')