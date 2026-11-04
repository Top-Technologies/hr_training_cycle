# How to Apply the Assessment Reference Sequence Changes

## What Changed
The Training Evaluation model now automatically assigns a sequence number (like EVAL/2026/0001) to the Assessment Reference field **when the trainee submits Part A (Self Evaluation)**.

This follows the same pattern as the Training Need Assessment, where the sequence is generated on submit rather than on create.

## Why This Approach?
- Draft evaluations don't need a reference number yet
- The sequence represents an "official" submitted evaluation
- Prevents gaps in sequence numbering if records are deleted before submission
- Only submitted evaluations get official reference numbers

## Steps to Apply Changes

### Option 1: Using Odoo UI (Recommended)
1. **Restart Odoo server** (if running)
2. Go to **Apps** menu
3. Click on the search filters and remove the "Apps" filter
4. Search for **"HR Training Cycle"**
5. Click on the module card
6. Click the **"Upgrade"** button

### Option 2: Using Command Line
Run this command from your Odoo installation directory:

```bash
./odoo-bin -c /path/to/your/odoo.conf -u hr_training_cycle -d your_database_name
```

Replace:
- `/path/to/your/odoo.conf` with your actual config file path
- `your_database_name` with your actual database name

## What Will Happen

### For New Records:
- When a training evaluation is created (automatically when a session is closed), the Assessment Reference will immediately show the sequence number like: **EVAL/2026/0001**, **EVAL/2026/0002**, etc.

### For Existing Records:
- Existing records that show "New" or "/" will **keep their current value**
- Only newly created records will get the automatic sequence

### If You Want to Fix Existing Records:
You can manually update existing records by running this Python code in Odoo's debug mode or shell:

```python
# Update existing evaluations without proper reference
evaluations = env['hr.training.evaluation'].search([('name', 'in', ['/', 'New', False])])
for eval in evaluations:
    eval.name = env['ir.sequence'].next_by_code('hr.training.evaluation') or 'EVAL/NEW'
```

## Sequence Format
- **Prefix**: EVAL/
- **Year**: Current year (4 digits)
- **Number**: Sequential number with 4-digit padding
- **Example**: EVAL/2026/0001, EVAL/2026/0002, etc.

## Testing
1. Close a training session to auto-create evaluations
2. Check that the new evaluations have proper sequence numbers in the Assessment Reference field
3. The sequence should be visible immediately in the list view and form view

## Troubleshooting

### If sequences still show as "New":
1. Check that the sequence exists:
   - Go to Settings → Technical → Sequences
   - Search for "Training Evaluation Reference"
   - Verify it exists with code: `hr.training.evaluation`

2. Check the sequence configuration:
   - Prefix should be: `EVAL/%(year)s/`
   - Padding should be: 4
   - Next number should be incremented

3. If sequence is missing, you may need to reinstall the module or manually create the sequence

### Module won't upgrade:
- Check Odoo logs for errors
- Make sure there are no Python syntax errors
- Verify the module is in the correct addons path
