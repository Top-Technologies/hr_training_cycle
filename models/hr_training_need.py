# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrTrainingNeed(models.Model):
    _name = 'hr.training.need'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Training Need Assessment (HR-OF-009)'
    _order = 'id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        tracking=True
    )
    department_head_id = fields.Many2one(
        'hr.employee',
        string='Department Head',
        default=lambda self: self._default_department_head(),
        tracking=True
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    line_ids = fields.One2many(
        'hr.training.need.line',
        'need_id',
        string='Training Needs'
    )
    total_budget = fields.Monetary(
        string='Total Budget',
        compute='_compute_total_budget',
        store=True,
        currency_field='currency_id',
        tracking=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved by HR'),
        ('refused', 'Refused'),
    ], string='Status', default='draft', tracking=True)

    session_ids = fields.One2many(
        'hr.training.session',
        'assessment_id',
        string='Training Sessions',
    )
    session_count = fields.Integer(
        string='Sessions Count',
        compute='_compute_session_count',
    )

    @api.depends('session_ids')
    def _compute_session_count(self):
        for need in self:
            need.session_count = len(need.session_ids)

    def action_view_sessions(self):
        self.ensure_one()
        return {
            'name': _('Training Sessions'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.training.session',
            'view_mode': 'list,form',
            'domain': [('assessment_id', '=', self.id)],
            'context': {'default_assessment_id': self.id},
        }

    @api.model
    def _default_department_head(self):
        return self.env.user.employee_id

    @api.model
    def _get_next_sequence(self):
        """Fetch next sequence safely with sudo, company fallback, and auto-recovery."""
        seq = self.env['ir.sequence'].sudo().next_by_code('hr.training.need')
        if not seq or seq in ('New', '/'):
            # Fallback 1: Search sequence regardless of company
            sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'hr.training.need')], limit=1)
            if sequence:
                seq = sequence._next()
            else:
                # Fallback 2: Auto-create sequence if missing from database
                sequence = self.env['ir.sequence'].sudo().create({
                    'name': 'Training Need Assessment Reference',
                    'code': 'hr.training.need',
                    'prefix': 'TNA/%(year)s/',
                    'padding': 4,
                    'number_increment': 1,
                    'number_next': 1,
                    'company_id': False,
                })
                seq = sequence._next()
        return seq or 'TNA/%s/0001' % fields.Date.today().year

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') in ('New', '/'):
                vals['name'] = self._get_next_sequence()
        return super().create(vals_list)

    @api.depends('line_ids.budget')
    def _compute_total_budget(self):
        for need in self:
            need.total_budget = sum(need.line_ids.mapped('budget'))

    def action_submit(self):
        for need in self:
            if not need.line_ids:
                raise UserError(_("Please add at least one training need line before submitting."))
            vals = {'state': 'submitted'}
            if not need.name or need.name in ('New', '/'):
                vals['name'] = self._get_next_sequence()
            need.write(vals)
            need.message_post(body=_("Training Need Assessment submitted for HR approval."))

    def action_approve(self):
        if not self.env.user.has_group('hr_training_cycle.group_training_manager'):
            raise UserError(_("Only HR Training Managers can approve training needs."))
        for need in self:
            vals = {'state': 'approved'}
            if not need.name or need.name in ('New', '/'):
                vals['name'] = self._get_next_sequence()
            need.write(vals)
            need.message_post(body=_("Training Need Assessment has been approved by HR."))

    def action_assign_missing_reference(self):
        """Utility to assign reference numbers to existing records showing 'New' or '/'."""
        for need in self:
            if not need.name or need.name in ('New', '/'):
                need.name = self._get_next_sequence()
        return True

    def action_refuse(self):
        if not self.env.user.has_group('hr_training_cycle.group_training_manager'):
            raise UserError(_("Only HR Training Managers can refuse training needs."))
        for need in self:
            need.write({'state': 'refused'})
            need.message_post(body=_("Training Need Assessment has been refused by HR."))

    def action_reset_to_draft(self):
        for need in self:
            need.write({'state': 'draft'})


class HrTrainingNeedLine(models.Model):
    _name = 'hr.training.need.line'
    _description = 'Training Need Line'

    need_id = fields.Many2one(
        'hr.training.need',
        string='Training Need Sheet',
        ondelete='cascade',
        required=True
    )
    name = fields.Char(string='Training Title', required=True)
    trainee_ids = fields.Many2many(
        'hr.employee',
        'hr_training_need_line_employee_rel',
        'line_id',
        'employee_id',
        string='Trainees',
        required=True,
    )
    reason = fields.Selection([
        ('low_performance', 'Low performance'),
        ('better_productivity', 'Better productivity'),
        ('new_technology', 'New technology'),
    ], string='Reason for the training', required=True, default='better_productivity')
    expected_result = fields.Text(string='Expected Result after Training')
    duration = fields.Float(string='Duration (days)', default=1.0)
    budget = fields.Monetary(string='Budget Required', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='need_id.currency_id',
        store=True,
        readonly=True
    )
    session_ids = fields.Many2many(
        'hr.training.session',
        'hr_training_session_need_line_rel',
        'need_line_id',
        'session_id',
        string='Training Sessions'
    )
    is_planned = fields.Boolean(
        string='Planned',
        compute='_compute_session_status',
    )
    is_completed = fields.Boolean(
        string='Completed',
        compute='_compute_session_status',
    )
    session_state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Session Status', compute='_compute_session_status')

    @api.depends('session_ids.state', 'need_id.session_ids.state', 'need_id.session_ids.training_title_id')
    def _compute_session_status(self):
        for line in self:
            all_sessions = line.session_ids | line.need_id.session_ids.filtered(lambda s: s.training_title_id == line)
            states = all_sessions.mapped('state')
            line.is_planned = bool(all_sessions)
            if 'done' in states:
                line.session_state = 'done'
                line.is_completed = True
            elif 'planned' in states:
                line.session_state = 'planned'
                line.is_completed = False
            elif 'draft' in states:
                line.session_state = 'draft'
                line.is_completed = False
            else:
                line.session_state = False
                line.is_completed = False
