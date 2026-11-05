# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrTrainingSession(models.Model):
    _name = 'hr.training.session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Training Attendance & Session (HR-OF-010)'
    _order = 'id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    title = fields.Char(
        string='Title of the Training',
        required=True,
        tracking=True
    )
    assessment_id = fields.Many2one(
        'hr.training.need',
        string='Assessment Reference',
        tracking=True,
        domain="[('state', '=', 'approved')]",
        ondelete='restrict',
    )
    training_title_id = fields.Many2one(
        'hr.training.need.line',
        string='Training Title',
        tracking=True,
        domain="[('need_id.state', '=', 'approved')]",
        ondelete='restrict',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='assessment_id.department_id',
        readonly=True,
    )
    department_head_id = fields.Many2one(
        'hr.employee',
        string='Department Head',
        related='assessment_id.department_head_id',
        readonly=True,
    )
    assessment_date = fields.Date(
        string='Assessment Date',
        related='assessment_id.date',
        readonly=True,
    )
    expected_result = fields.Text(
        string='Expected Result',
        related='training_title_id.expected_result',
        readonly=True,
    )
    training_duration = fields.Float(
        string='Planned Duration (Days)',
        related='training_title_id.duration',
        readonly=True,
    )
    proposed_budget = fields.Monetary(
        string='Proposed Budget',
        related='training_title_id.budget',
        currency_field='currency_id',
        readonly=True,
    )
    total_attendees = fields.Integer(
        string='Total Enrolled',
        compute='_compute_attendance_metrics',
    )
    present_attendees = fields.Integer(
        string='Attended',
        compute='_compute_attendance_metrics',
    )
    attendance_rate = fields.Float(
        string='Attendance Rate (%)',
        compute='_compute_attendance_metrics',
    )
    target_group = fields.Char(string='Target Group')
    venue = fields.Char(string='Venue')
    training_type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
    ], string='Training Type', default='internal', required=True, tracking=True)
    trainer_employee_id = fields.Many2one(
        'hr.employee',
        string='Trainer (Internal)',
        tracking=True,
    )
    provider_id = fields.Many2one(
        'res.partner',
        string='Training Provider',
        tracking=True,
        help='External company, institution, or provider conducting the training.'
    )
    external_trainer = fields.Char(
        string='External Trainer / Instructor',
        tracking=True,
        help='Name of the external instructor or facilitator.'
    )
    trainer = fields.Char(
        string='Training Provided By',
        compute='_compute_trainer',
        store=True,
        readonly=False,
        precompute=True,
        tracking=True,
    )
    notice = fields.Text(string='Notice')

    day_ids = fields.One2many(
        'hr.training.session.day',
        'session_id',
        string='Training Days'
    )
    start_date = fields.Date(
        string='Start Date',
        compute='_compute_dates',
        store=True,
        tracking=True
    )
    end_date = fields.Date(
        string='End Date',
        compute='_compute_dates',
        store=True,
        tracking=True
    )

    need_line_ids = fields.Many2many(
        'hr.training.need.line',
        'hr_training_session_need_line_rel',
        'session_id',
        'need_line_id',
        string='Need Lines Covered',
        domain="[('need_id.state', '=', 'approved')]"
    )
    attendee_ids = fields.One2many(
        'hr.training.attendee',
        'session_id',
        string='Attendees'
    )
    actual_cost = fields.Monetary(string='Actual Cost', currency_field='currency_id', tracking=True)
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

    evaluation_ids = fields.One2many(
        'hr.training.evaluation',
        'session_id',
        string='Evaluations'
    )
    evaluation_count = fields.Integer(
        string='Evaluations Count',
        compute='_compute_evaluation_count'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    @api.depends('training_type', 'trainer_employee_id', 'provider_id', 'external_trainer')
    def _compute_trainer(self):
        for session in self:
            if session.training_type == 'internal':
                if session.trainer_employee_id:
                    session.trainer = session.trainer_employee_id.name
                elif not session.trainer:
                    session.trainer = ''
            elif session.training_type == 'external':
                parts = []
                if session.provider_id:
                    parts.append(session.provider_id.name)
                if session.external_trainer:
                    parts.append(session.external_trainer)
                if parts:
                    session.trainer = " - ".join(parts)
                elif not session.trainer:
                    session.trainer = ''
            elif not session.trainer:
                session.trainer = ''

    @api.depends('attendee_ids', 'attendee_ids.days_attended_count', 'day_ids')
    def _compute_attendance_metrics(self):
        for session in self:
            total = len(session.attendee_ids)
            present = len(session.attendee_ids.filtered(lambda a: a.days_attended_count > 0 or not session.day_ids)) if total else 0
            session.total_attendees = total
            session.present_attendees = present
            session.attendance_rate = round((present / total * 100.0), 1) if total else 0.0

    @api.onchange('training_type')
    def _onchange_training_type(self):
        if self.training_type == 'internal':
            self.provider_id = False
            self.external_trainer = False
        elif self.training_type == 'external':
            self.trainer_employee_id = False

    @api.depends('day_ids.date')
    def _compute_dates(self):
        for session in self:
            dates = session.day_ids.mapped('date')
            session.start_date = min(dates) if dates else False
            session.end_date = max(dates) if dates else False

    @api.depends('evaluation_ids')
    def _compute_evaluation_count(self):
        for session in self:
            session.evaluation_count = len(session.evaluation_ids)

    @api.onchange('assessment_id')
    def _onchange_assessment_id(self):
        for session in self:
            domain = [('need_id.state', '=', 'approved')]
            if session.assessment_id:
                domain = [('need_id', '=', session.assessment_id.id)]
                if session.assessment_id.department_id and not session.target_group:
                    session.target_group = session.assessment_id.department_id.name

                lines = session.assessment_id.line_ids
                if len(lines) == 1:
                    line = lines[0]
                    session.training_title_id = line
                    session.title = line.name or False
                    session.need_line_ids = [(6, 0, [line.id])]
                    if line.trainee_ids:
                        session.attendee_ids = session._prepare_attendee_commands(line.trainee_ids)
                    if not session.actual_cost and line.budget:
                        session.actual_cost = line.budget
                elif lines:
                    if session.training_title_id and session.training_title_id.need_id == session.assessment_id:
                        pass
                    else:
                        line = lines[0]
                        session.training_title_id = line
                        session.title = line.name or False
                        session.need_line_ids = [(6, 0, [line.id])]
                        if line.trainee_ids:
                            session.attendee_ids = session._prepare_attendee_commands(line.trainee_ids)
                        if not session.actual_cost and line.budget:
                            session.actual_cost = line.budget
                else:
                    session.training_title_id = False
                    session.title = False
                    session.attendee_ids = [(5, 0, 0)]
                    session.need_line_ids = [(5, 0, 0)]
            else:
                session.training_title_id = False
                session.title = False
                session.attendee_ids = [(5, 0, 0)]
                session.need_line_ids = [(5, 0, 0)]
            return {'domain': {'training_title_id': domain}}

    def _prepare_attendee_commands(self, trainees):
        """Build One2many commands to replace attendees with the given trainees."""
        return [(5, 0, 0)] + [(0, 0, {'employee_id': emp.id}) for emp in trainees]

    def _sync_attendees_from_training_title(self, title_line):
        """Replace attendees from the training title need line trainees."""
        self.ensure_one()
        trainees = title_line.trainee_ids if title_line else self.env['hr.employee']
        self.attendee_ids = self._prepare_attendee_commands(trainees)
        if title_line:
            self.need_line_ids = [(6, 0, [title_line.id])]
        else:
            self.need_line_ids = [(5, 0, 0)]

    @api.onchange('training_title_id')
    def _onchange_training_title_id(self):
        for session in self:
            if session.training_title_id:
                line = session.training_title_id
                session.title = line.name or False
                if not session.assessment_id and line.need_id:
                    session.assessment_id = line.need_id
                if line.trainee_ids:
                    session.attendee_ids = session._prepare_attendee_commands(line.trainee_ids)
                session.need_line_ids = [(6, 0, [line.id])]
                if not session.actual_cost and line.budget:
                    session.actual_cost = line.budget
                if line.need_id.department_id and not session.target_group:
                    session.target_group = line.need_id.department_id.name
            else:
                session.title = False
                session.attendee_ids = [(5, 0, 0)]
                session.need_line_ids = [(5, 0, 0)]

    @api.constrains('assessment_id', 'training_title_id')
    def _check_training_title_assessment(self):
        for session in self:
            if session.training_title_id and session.assessment_id:
                if session.training_title_id.need_id != session.assessment_id:
                    raise ValidationError(_(
                        "The selected Training Title '%(title)s' does not belong to Assessment Reference '%(assessment)s'.",
                        title=session.training_title_id.name,
                        assessment=session.assessment_id.name,
                    ))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('training_title_id'):
                title_line = self.env['hr.training.need.line'].browse(vals['training_title_id'])
                if not vals.get('title'):
                    vals['title'] = title_line.name or False
                if not vals.get('assessment_id') and title_line.need_id:
                    vals['assessment_id'] = title_line.need_id.id
                if not vals.get('actual_cost') and title_line.budget:
                    vals['actual_cost'] = title_line.budget
                if not vals.get('target_group') and title_line.need_id.department_id:
                    vals['target_group'] = title_line.need_id.department_id.name
            elif vals.get('assessment_id'):
                assessment = self.env['hr.training.need'].browse(vals['assessment_id'])
                if not vals.get('target_group') and assessment.department_id:
                    vals['target_group'] = assessment.department_id.name
                if assessment.line_ids:
                    first_line = assessment.line_ids[0]
                    if not vals.get('training_title_id'):
                        vals['training_title_id'] = first_line.id
                    if not vals.get('title'):
                        vals['title'] = first_line.name or False
                    if not vals.get('actual_cost') and first_line.budget:
                        vals['actual_cost'] = first_line.budget
        sessions = super().create(vals_list)
        for session in sessions:
            if session.training_title_id and not session.attendee_ids:
                session._sync_attendees_from_training_title(session.training_title_id)
            elif session.assessment_id and not session.attendee_ids:
                all_trainees = session.assessment_id.line_ids.mapped('trainee_ids')
                if all_trainees:
                    session.attendee_ids = session._prepare_attendee_commands(all_trainees)
        return sessions

    def write(self, vals):
        title_changed = False
        assessment_changed = False
        if 'training_title_id' in vals:
            new_title_id = vals['training_title_id'] or False
            title_changed = any((s.training_title_id.id or False) != new_title_id for s in self)
            if vals['training_title_id']:
                title_line = self.env['hr.training.need.line'].browse(vals['training_title_id'])
                if 'title' not in vals:
                    vals['title'] = title_line.name or False
                if 'assessment_id' not in vals and title_line.need_id:
                    vals['assessment_id'] = title_line.need_id.id
            elif 'title' not in vals:
                vals['title'] = False
        elif 'assessment_id' in vals:
            new_assessment_id = vals['assessment_id'] or False
            assessment_changed = any((s.assessment_id.id or False) != new_assessment_id for s in self)

        res = super().write(vals)
        if title_changed:
            for session in self:
                if session.training_title_id:
                    session._sync_attendees_from_training_title(session.training_title_id)
        elif assessment_changed:
            for session in self:
                if session.assessment_id and not session.training_title_id:
                    lines = session.assessment_id.line_ids
                    if len(lines) == 1:
                        session.training_title_id = lines[0]
                        session.title = lines[0].name
                        session._sync_attendees_from_training_title(lines[0])
        return res

    def action_confirm(self):
        for session in self:
            if not session.day_ids:
                raise UserError(_("Please add at least one training day before confirming the session."))
            vals = {'state': 'planned'}
            if not session.name or session.name in ('New', '/', False):
                seq = self.env['ir.sequence'].sudo().next_by_code('hr.training.session')
                if not seq or seq in ('New', '/'):
                    sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'hr.training.session')], limit=1)
                    seq = sequence._next() if sequence else False
                vals['name'] = seq or _('New')
            session.write(vals)
            session.message_post(body=_("Training session has been planned."))

    def action_close(self):
        Evaluation = self.env['hr.training.evaluation']
        for session in self:
            if not session.attendee_ids:
                raise UserError(_("No attendees found in this training session."))

            # Find attendees who were present
            present_attendees = session.attendee_ids.filtered(
                lambda a: a.days_attended_count > 0 or not session.day_ids
            )
            if not present_attendees:
                raise UserError(_("No attendees have marked attendance for this session. Please tick days attended for participants."))

            end_date = session.end_date or fields.Date.today()
            part_b_due_date = end_date + relativedelta(months=6)

            for attendee in present_attendees:
                # Avoid duplicate evaluations
                existing_eval = Evaluation.search([
                    ('session_id', '=', session.id),
                    ('trainee_id', '=', attendee.employee_id.id),
                ], limit=1)

                evaluator = attendee.employee_id.parent_id or self.env.user.employee_id
                if not evaluator:
                    raise UserError(_("Cannot close training: Trainee %s has no direct manager assigned.") % attendee.employee_id.name)

                if not existing_eval:
                    evaluation = Evaluation.create({
                        'session_id': session.id,
                        'trainee_id': attendee.employee_id.id,
                        'evaluator_id': evaluator.id,
                        'part_b_due_date': part_b_due_date,
                        'state': 'awaiting_trainee',
                    })
                else:
                    evaluation = existing_eval

                # Trainee gets a to-do for Part A, due in 7 days
                if evaluation.trainee_id.user_id:
                    # check if activity already scheduled
                    existing_act = self.env['mail.activity'].search([
                        ('res_model', '=', 'hr.training.evaluation'),
                        ('res_id', '=', evaluation.id),
                        ('user_id', '=', evaluation.trainee_id.user_id.id),
                    ], limit=1)
                    if not existing_act:
                        evaluation.activity_schedule(
                            'mail.mail_activity_data_todo',
                            summary=_('Complete Part A Training Evaluation'),
                            user_id=evaluation.trainee_id.user_id.id,
                            date_deadline=fields.Date.today() + relativedelta(days=7),
                            note=_('Please fill out Part A of your post-training evaluation for %s.') % session.title
                        )

            session.write({'state': 'done'})
            session.message_post(body=_("Training session closed. Post-training evaluations have been generated."))

    def action_cancel(self):
        for session in self:
            session.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        for session in self:
            session.write({'state': 'draft'})

    def action_view_evaluations(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('hr_training_cycle.action_hr_training_evaluation')
        action['domain'] = [('session_id', '=', self.id)]
        action['context'] = {'default_session_id': self.id}
        return action


class HrTrainingSessionDay(models.Model):
    _name = 'hr.training.session.day'
    _description = 'Training Session Day'
    _order = 'date asc, id asc'

    session_id = fields.Many2one(
        'hr.training.session',
        string='Session',
        ondelete='cascade',
        required=True
    )
    date = fields.Date(string='Date', required=True)
    name = fields.Char(string='Day Name', compute='_compute_name', store=True)

    @api.depends('date')
    def _compute_name(self):
        for day in self:
            if day.date:
                day.name = f"{day.date.strftime('%Y-%m-%d')} ({day.date.strftime('%a')})"
            else:
                day.name = _("Training Day")


class HrTrainingAttendee(models.Model):
    _name = 'hr.training.attendee'
    _description = 'Training Attendee'
    _rec_name = 'employee_id'

    session_id = fields.Many2one(
        'hr.training.session',
        string='Session',
        ondelete='cascade',
        required=True
    )
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    job_id = fields.Many2one(
        'hr.job',
        string='Position',
        related='employee_id.job_id',
        store=True,
        readonly=True
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        readonly=True
    )
    attended_day_ids = fields.Many2many(
        'hr.training.session.day',
        'hr_training_attendee_day_rel',
        'attendee_id',
        'day_id',
        string='Days Attended'
    )
    days_attended_count = fields.Integer(
        string='Days Attended Count',
        compute='_compute_days_attended_count',
        store=True
    )

    _sql_constraints = [
        ('uniq_employee_session', 'unique(session_id, employee_id)', 'An employee can only be added once per session!')
    ]

    @api.depends('attended_day_ids')
    def _compute_days_attended_count(self):
        for rec in self:
            rec.days_attended_count = len(rec.attended_day_ids)
