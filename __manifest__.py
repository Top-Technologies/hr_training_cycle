# -*- coding: utf-8 -*-
{
    'name': 'HR Training Cycle',
    'version': '18.0.1.1.1',
    'category': 'Human Resources/Training',
    'summary': 'Full HR training cycle from assessment to 6-month evaluation (Forms HR-OF-009, HR-OF-010, HR-OF-011)',
    'description': """
HR Training Cycle Management
============================
Integrates three essential HR paper forms into an automated end-to-end workflow:
- HR-OF-009: Training Need Assessment (hr.training.need and lines)
- HR-OF-010: Training Attendance & Sessions (hr.training.session, days and attendees)
- HR-OF-011: Employee Post Training Evaluation (hr.training.evaluation - Part A & Part B)
    """,
    'author': 'Toptec',
    'depends': ['hr', 'mail'],
    'data': [
        'security/hr_training_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'report/hr_training_attendance_report.xml',
        'views/hr_training_need_views.xml',
        'views/hr_training_session_views.xml',
        'views/hr_training_evaluation_views.xml',
        'views/hr_employee_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
