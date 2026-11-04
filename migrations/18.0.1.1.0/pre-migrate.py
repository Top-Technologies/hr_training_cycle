# -*- coding: utf-8 -*-


def migrate(cr, version):
    """Copy trainee_id Many2one values into the new trainee_ids Many2many table."""
    cr.execute("""
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'hr_training_need_line'
          AND column_name = 'trainee_id'
    """)
    if not cr.fetchone():
        return

    cr.execute("""
        CREATE TABLE IF NOT EXISTS hr_training_need_line_employee_rel (
            line_id INTEGER NOT NULL REFERENCES hr_training_need_line(id) ON DELETE CASCADE,
            employee_id INTEGER NOT NULL REFERENCES hr_employee(id) ON DELETE CASCADE,
            PRIMARY KEY (line_id, employee_id)
        )
    """)
    cr.execute("""
        INSERT INTO hr_training_need_line_employee_rel (line_id, employee_id)
        SELECT id, trainee_id
        FROM hr_training_need_line
        WHERE trainee_id IS NOT NULL
        ON CONFLICT DO NOTHING
    """)
