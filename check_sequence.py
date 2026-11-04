#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check if the hr.training.evaluation sequence exists in Odoo
Run this in Odoo shell: odoo-bin shell -d your_database_name
"""

# Run this in Odoo shell:
sequence = env['ir.sequence'].search([('code', '=', 'hr.training.evaluation')])

if sequence:
    print("\n✓ Sequence EXISTS")
    print(f"  ID: {sequence.id}")
    print(f"  Name: {sequence.name}")
    print(f"  Code: {sequence.code}")
    print(f"  Prefix: {sequence.prefix}")
    print(f"  Padding: {sequence.padding}")
    print(f"  Next Number: {sequence.number_next}")
    print(f"\n  Test next sequence: {env['ir.sequence'].next_by_code('hr.training.evaluation')}")
else:
    print("\n✗ Sequence DOES NOT EXIST!")
    print("\nCreating sequence manually...")
    
    new_seq = env['ir.sequence'].create({
        'name': 'Training Evaluation Reference',
        'code': 'hr.training.evaluation',
        'prefix': 'EVAL/%(year)s/',
        'padding': 4,
        'number_increment': 1,
        'number_next': 1,
    })
    
    print(f"✓ Sequence created with ID: {new_seq.id}")
    print(f"  Test: {env['ir.sequence'].next_by_code('hr.training.evaluation')}")

# Check evaluations with 'New' reference
print("\n" + "="*50)
evals = env['hr.training.evaluation'].search([('name', 'in', ['New', '/', False])])
print(f"Found {len(evals)} evaluations with 'New' or '/' reference:")
for e in evals:
    print(f"  - ID {e.id}: {e.trainee_id.name} - State: {e.state}")
