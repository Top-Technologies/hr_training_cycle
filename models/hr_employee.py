# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    training_evaluation_ids = fields.One2many(
        'hr.training.evaluation',
        'trainee_id',
        string='Training Records'
    )
    training_count = fields.Integer(
        string='Trainings',
        compute='_compute_training_count'
    )

    @api.depends('training_evaluation_ids')
    def _compute_training_count(self):
        for employee in self:
            employee.training_count = len(employee.training_evaluation_ids)

    def action_view_trainings(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('hr_training_cycle.action_hr_training_evaluation')
        action['domain'] = [('trainee_id', '=', self.id)]
        action['context'] = {'default_trainee_id': self.id}
        return action
