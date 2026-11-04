# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    training_evaluation_ids = fields.One2many(
        'hr.training.evaluation',
        'trainee_id',
        string='Training Evaluations'
    )
    training_session_ids = fields.Many2many(
        'hr.training.session',
        compute='_compute_training_sessions',
        string='Trainings Taken',
    )
    training_count = fields.Integer(
        string='Trainings',
        compute='_compute_training_sessions'
    )

    def _compute_training_sessions(self):
        Attendee = self.env['hr.training.attendee']
        for employee in self:
            sessions = Attendee.search([
                ('employee_id', '=', employee.id),
            ]).mapped('session_id')
            employee.training_session_ids = sessions
            employee.training_count = len(sessions)

    def action_view_trainings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Trainings Taken'),
            'res_model': 'hr.training.session',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.training_session_ids.ids)],
            'context': {'create': False},
        }
