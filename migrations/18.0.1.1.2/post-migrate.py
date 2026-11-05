# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """Automatically fix all training needs and evaluations with 'New' or '/' references."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    # 1. Ensure global sequence for hr.training.need exists with company_id=False
    seq_need = env['ir.sequence'].search([('code', '=', 'hr.training.need')], limit=1)
    if not seq_need:
        seq_need = env['ir.sequence'].create({
            'name': 'Training Need Assessment Reference',
            'code': 'hr.training.need',
            'prefix': 'TNA/%(year)s/',
            'padding': 4,
            'number_increment': 1,
            'number_next': 1,
            'company_id': False,
        })
    elif seq_need.company_id:
        seq_need.write({'company_id': False})

    # 2. Assign reference to all training needs stuck with 'New', '/', or NULL
    needs = env['hr.training.need'].search(
        [('name', 'in', ['New', '/', False])],
        order='id asc'
    )
    for need in needs:
        need.name = env['ir.sequence'].next_by_code('hr.training.need')

    # 3. Ensure global sequence for hr.training.evaluation exists with company_id=False
    seq_eval = env['ir.sequence'].search([('code', '=', 'hr.training.evaluation')], limit=1)
    if not seq_eval:
        seq_eval = env['ir.sequence'].create({
            'name': 'Training Evaluation Reference',
            'code': 'hr.training.evaluation',
            'prefix': 'EVAL/%(year)s/',
            'padding': 4,
            'number_increment': 1,
            'number_next': 1,
            'company_id': False,
        })
    elif seq_eval.company_id:
        seq_eval.write({'company_id': False})

    # 4. Fix evaluations with 'New', '/', or False that have been submitted
    evals = env['hr.training.evaluation'].search(
        [('name', 'in', ['New', '/', False]), ('state', '!=', 'awaiting_trainee')],
        order='id asc'
    )
    for ev in evals:
        ev.name = env['ir.sequence'].next_by_code('hr.training.evaluation')
