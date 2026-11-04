#!/bin/bash

# Script to upgrade the hr_training_cycle module in Odoo
# This will apply the sequence changes to the Assessment Reference field

echo "======================================"
echo "HR Training Cycle Module Upgrade"
echo "======================================"
echo ""
echo "This script will upgrade the hr_training_cycle module to apply"
echo "the Assessment Reference sequence changes."
echo ""

# Default values (you may need to adjust these)
ODOO_BIN="/home/toptec/Documents/odoo18e/server/odoo-bin"
ODOO_CONF="/home/toptec/Documents/odoo18e/server/odoo.conf"

# Prompt for database name
read -p "Enter your Odoo database name: " DB_NAME

if [ -z "$DB_NAME" ]; then
    echo "Error: Database name is required!"
    exit 1
fi

# Check if odoo-bin exists
if [ ! -f "$ODOO_BIN" ]; then
    echo "Error: Odoo binary not found at $ODOO_BIN"
    echo "Please update the ODOO_BIN variable in this script."
    exit 1
fi

echo ""
echo "Upgrading module with the following settings:"
echo "  Odoo Binary: $ODOO_BIN"
echo "  Database: $DB_NAME"
echo "  Module: hr_training_cycle"
echo ""

# Stop any running Odoo instance (optional)
read -p "Do you want to stop any running Odoo processes first? (y/n): " STOP_ODOO

if [ "$STOP_ODOO" = "y" ] || [ "$STOP_ODOO" = "Y" ]; then
    echo "Stopping Odoo processes..."
    pkill -f odoo-bin || echo "No Odoo processes found."
    sleep 2
fi

# Run the upgrade
echo ""
echo "Running upgrade command..."
echo "Command: python3 $ODOO_BIN -c $ODOO_CONF -d $DB_NAME -u hr_training_cycle --stop-after-init"
echo ""

python3 "$ODOO_BIN" -c "$ODOO_CONF" -d "$DB_NAME" -u hr_training_cycle --stop-after-init

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✓ Module upgrade completed successfully!"
    echo "======================================"
    echo ""
    echo "Changes applied:"
    echo "  • Assessment Reference now auto-generates sequence (EVAL/YYYY/####)"
    echo "  • Existing records with '/' or 'New' have been updated with sequences"
    echo "  • New evaluations will automatically get sequence numbers"
    echo ""
    echo "You can now restart your Odoo server and test the changes."
else
    echo ""
    echo "======================================"
    echo "✗ Module upgrade failed!"
    echo "======================================"
    echo ""
    echo "Please check the error messages above and fix any issues."
    echo "Common issues:"
    echo "  • Database name incorrect"
    echo "  • Odoo binary path incorrect"
    echo "  • Python syntax errors in the code"
    echo "  • Database connection issues"
fi
