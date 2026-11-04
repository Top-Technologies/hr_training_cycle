#!/bin/bash

# Quick upgrade script for hr_training_cycle module
# Run this to apply the Assessment Reference sequence changes

echo "=========================================="
echo "Quick Upgrade: HR Training Cycle"
echo "=========================================="
echo ""

# You need to set these variables:
ODOO_BIN="${HOME}/Documents/odoo18e/server/odoo-bin"
ODOO_CONF="${HOME}/Documents/odoo18e/server/odoo.conf"

# Prompt for database name
read -p "Enter your database name: " DB_NAME

if [ -z "$DB_NAME" ]; then
    echo "Error: Database name is required!"
    exit 1
fi

echo ""
echo "Upgrading module in database: $DB_NAME"
echo ""

# Run upgrade
python3 "$ODOO_BIN" -c "$ODOO_CONF" -d "$DB_NAME" -u hr_training_cycle --stop-after-init

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Module upgraded successfully!"
    echo ""
    echo "Now test by:"
    echo "1. Restart your Odoo server"
    echo "2. Open a training evaluation"
    echo "3. Fill Part A and click 'Submit Self Evaluation'"
    echo "4. Check that Assessment Reference changes from 'New' to 'EVAL/2026/####'"
else
    echo ""
    echo "✗ Upgrade failed - check the error messages above"
fi
