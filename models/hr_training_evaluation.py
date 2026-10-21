# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

RATING_SELECTION = [
    ('4', 'Excellent (4)'),
    ('3', 'Very good (3)'),
    ('2', 'Good (2)'),
    ('1', 'No change / none (1)'),
]

RATING_FIELDS = [
    ('rating_motivation', '1. Motivation to apply the knowledge gained'),
    ('rating_cost_waste', '2. Effort in reducing cost and waste'),
    ('rating_retention', '3. Willingness to stay with the organisation'),
    ('rating_discipline', '4. Discipline and cooperation'),
    ('rating_attendance', '5. Willingness to be present at work'),
    ('rating_work_quality', '6. Attention to work quality, quantity and productivity'),
    ('rating_morale', '7. Work morale and satisfaction'),
    ('rating_customer_focus', '8. Initiative to meet customer needs (internal or external)'),
    ('rating_teamwork', '9. Initiative to influence colleagues in teamwork'),
    ('rating_knowledge_gain', '10. Initiative to gain more knowledge and experience'),
]


class HrTrainingEvaluation(models.Model):
    _name = 'hr.training.evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Post Training Evaluation (HR-OF-011)'
    _order = 'id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default='/'
    )
    session_id = fields.Many2one(
        'hr.training.session',
        string='Training Session',
        required=True,
        tracking=True,
        ondelete='cascade'
    )
    trainee_id = fields.Many2one(
        'hr.employee',
        string='Trainee',
        required=True,
        tracking=True
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='trainee_id.department_id',
        store=True,
        readonly=True
    )
    job_id = fields.Many2one(
        'hr.job',
        string='Position',
        related='trainee_id.job_id',
        store=True,
        readonly=True
    )
    evaluator_id = fields.Many2one(
        'hr.employee',
        string='Evaluator (Direct Manager)',
        required=True,
        tracking=True
    )
    part_b_due_date = fields.Date(
        string='Part B Due Date',
        tracking=True
    )
    part_b_notified = fields.Boolean(
        string='Part B Notified',
        default=False,
        copy=False
    )
    state = fields.Selection([
        ('awaiting_trainee', 'Awaiting trainee (Self Evaluation )'),
        ('awaiting_followup', 'Awaiting 6-month follow-up (Manager Evaluation )'),
        ('completed', 'Completed'),
    ], string='Status', default='awaiting_trainee', tracking=True)

    # ==========================
    # Part A (Trainee)
    # ==========================
    is_related_to_job = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Is the training related to your current job?', tracking=True)
    additional_knowledge = fields.Text(string='What additional knowledge did you gain?')
    need_manager_support = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Do you need support from your manager?', default='no')
    manager_support_detail = fields.Text(string='Support Details')
    how_to_apply = fields.Text(string='How are you prepared to apply what you learned?')
    future_training_points = fields.Text(string='Points to add to future training')

    # ==========================
    # Part B (Direct Manager)
    # ==========================
    rating_motivation = fields.Selection(RATING_SELECTION, string='1. Motivation to apply knowledge')
    rating_cost_waste = fields.Selection(RATING_SELECTION, string='2. Effort in reducing cost and waste')
    rating_retention = fields.Selection(RATING_SELECTION, string='3. Willingness to stay with organisation')
    rating_discipline = fields.Selection(RATING_SELECTION, string='4. Discipline and cooperation')
    rating_attendance = fields.Selection(RATING_SELECTION, string='5. Willingness to be present at work')
    rating_work_quality = fields.Selection(RATING_SELECTION, string='6. Attention to work quality/quantity')
    rating_morale = fields.Selection(RATING_SELECTION, string='7. Work morale and satisfaction')
    rating_customer_focus = fields.Selection(RATING_SELECTION, string='8. Initiative to meet customer needs')
    rating_teamwork = fields.Selection(RATING_SELECTION, string='9. Initiative in teamwork')
    rating_knowledge_gain = fields.Selection(RATING_SELECTION, string='10. Initiative to gain knowledge')

    trainee_results = fields.Text(string='Results the trainee achieved')
    met_goal = fields.Selection([
        ('yes', 'Yes'),
        ('partially', 'Partially'),
        ('no', 'No'),
    ], string='Did the training meet its goal?', tracking=True)
    not_met_reason = fields.Text(string='Reason if not met')
    manager_comments = fields.Text(string='Additional Comments')
    average_score = fields.Float(
        string='Average Score (1 to 4)',
        compute='_compute_average_score',
        store=True,
        digits=(3, 2),
        tracking=True
    )

    @api.depends(
        'rating_motivation', 'rating_cost_waste', 'rating_retention',
        'rating_discipline', 'rating_attendance', 'rating_work_quality',
        'rating_morale', 'rating_customer_focus', 'rating_teamwork',
        'rating_knowledge_gain'
    )
    def _compute_average_score(self):
        fnames = [f[0] for f in RATING_FIELDS]
        for rec in self:
            rated_vals = [int(rec[fname]) for fname in fnames if rec[fname]]
            if rated_vals:
                rec.average_score = round(sum(rated_vals) / len(fnames), 2)
            else:
                rec.average_score = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.training.evaluation') or '/'
        return super().create(vals_list)

    def action_submit_part_a(self):
        for rec in self:
            is_trainee = (rec.trainee_id.user_id == self.env.user)
            is_hr = self.env.user.has_group('hr_training_cycle.group_training_manager')
            if not (is_trainee or is_hr):
                raise UserError(_("Only the trainee (%s) or an HR Training Manager can submit Self Evaluation.") % rec.trainee_id.name)

            if not rec.is_related_to_job:
                raise UserError(_("Please answer: 'Is the training related to your current job?'"))
            if not rec.additional_knowledge:
                raise UserError(_("Please answer: 'What additional knowledge did you gain?'"))
            if not rec.how_to_apply:
                raise UserError(_("Please answer: 'How are you prepared to apply what you learned?'"))

            # Clear open activities on this record
            activities = self.env['mail.activity'].search([
                ('res_model', '=', 'hr.training.evaluation'),
                ('res_id', '=', rec.id),
            ])
            if activities:
                activities.action_feedback(feedback=_("Self Evalation  submitted by trainee."))

            rec.write({'state': 'awaiting_followup'})
            rec.message_post(body=_("Self Evuation  (Trainee Self-Evaluation) has been completed and submitted."))

    def action_submit_part_b(self):
        for rec in self:
            is_evaluator = (rec.evaluator_id.user_id == self.env.user)
            is_hr = self.env.user.has_group('hr_training_cycle.group_training_manager')
            if not (is_evaluator or is_hr):
                raise UserError(_("Only the evaluator (%s) or an HR Training Manager can submit Part B.") % rec.evaluator_id.name)

            # Check all 10 ratings
            missing_ratings = [label for fname, label in RATING_FIELDS if not rec[fname]]
            if missing_ratings:
                raise UserError(_("All 10 rating criteria are required. Missing ratings:\n- %s") % "\n- ".join(missing_ratings))

            if not rec.met_goal:
                raise UserError(_("Please specify whether the training met its goal."))
            if rec.met_goal in ('partially', 'no') and not rec.not_met_reason:
                raise UserError(_("Please explain the reason why the training goal was not fully met."))

            # Clear open activities
            activities = self.env['mail.activity'].search([
                ('res_model', '=', 'hr.training.evaluation'),
                ('res_id', '=', rec.id),
            ])
            if activities:
                activities.action_feedback(feedback=_("Part B completed by manager."))

            rec.write({'state': 'completed'})
            rec.message_post(body=_(
                "Part B (6-Month Follow-Up Evaluation) submitted. "
                "Goal Result: %s. Average Score: %0.2f / 4.00"
            ) % (dict(rec._fields['met_goal'].selection).get(rec.met_goal), rec.average_score))

    @api.model
    def _cron_check_six_month_followup(self):
        today = fields.Date.today()
        evaluations = self.search([
            ('state', '=', 'awaiting_followup'),
            ('part_b_due_date', '<=', today),
            ('part_b_notified', '=', False),
        ])
        for eval_rec in evaluations:
            eval_rec.write({'part_b_notified': True})
            if eval_rec.evaluator_id.user_id:
                eval_rec.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Part B 6-Month Training Follow-Up Due: %s') % eval_rec.trainee_id.name,
                    user_id=eval_rec.evaluator_id.user_id.id,
                    date_deadline=today + relativedelta(days=14),
                    note=_('The 6-month evaluation period for trainee %s (%s) is due. Please review results and submit Part B.') % (
                        eval_rec.trainee_id.name, eval_rec.session_id.title
                    )
                )
            eval_rec.message_post(body=_("6-month follow-up reached. Part B evaluation request dispatched to manager %s.") % eval_rec.evaluator_id.name)
