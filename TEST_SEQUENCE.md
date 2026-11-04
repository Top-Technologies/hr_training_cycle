# Testing Assessment Reference Sequence

## ⚠️ BEFORE TESTING - YOU MUST UPGRADE THE MODULE!

The code changes will NOT work until you upgrade the module in Odoo.

## How to Upgrade:

### Option A: Via Odoo Interface
1. Open Odoo in browser
2. Go to **Apps** menu
3. Remove the "Apps" filter (click X in search bar)
4. Search: **HR Training Cycle**
5. Click the module
6. Click **"Upgrade"** button
7. Wait for completion
8. Hard refresh browser (Ctrl+Shift+R)

### Option B: Via Command Line
```bash
cd /home/toptec/Documents/odoo18e/server/custom_addons/hr_training_cycle
./quick_upgrade.sh
```

Then restart your Odoo server.

---

## Testing Steps:

### Test 1: Check if Sequence Exists

1. In Odoo, enable **Developer Mode**:
   - Settings → Activate Developer Mode

2. Go to **Settings → Technical → Sequences**

3. Search for: **"Training Evaluation"**

4. You should see:
   - **Name**: Training Evaluation Reference
   - **Code**: hr.training.evaluation
   - **Prefix**: EVAL/%(year)s/
   - **Padding**: 4

**If sequence doesn't exist**: Run the check_sequence.py script in Odoo shell to create it

---

### Test 2: Create New Evaluation

1. Go to **Training → Sessions**

2. Open a **planned** training session (or create one)

3. Click **"Close Session"** button

4. This creates evaluations for all attendees

5. Go to **Training → Evaluations**

6. Open one of the new evaluations

7. **Check**: Assessment Reference should show **"New"** ✓

---

### Test 3: Submit Part A (This generates the sequence!)

1. In the evaluation form (showing "New"):

2. Fill out **Part A** fields:
   - Is the training related to your current job? → Select Yes/No
   - What additional knowledge did you gain? → Enter text
   - How are you prepared to apply what you learned? → Enter text

3. Click **"Submit Self Evaluation"** button

4. **EXPECTED RESULT**: 
   - Assessment Reference changes from "New" to **"EVAL/2026/0001"** ✓
   - Status changes to "Awaiting 6-month follow-up"
   - Message in chatter: "Self Evaluation (Trainee Self-Evaluation) has been completed and submitted. Reference: EVAL/2026/0001"

---

## Troubleshooting:

### Still showing "New" after submit?

**Check 1: Did you upgrade the module?**
```bash
# Verify module version in Apps
# Should show version: 18.0.1.1.1
```

**Check 2: Check Odoo logs for errors**
```bash
# Look for Python errors when clicking Submit
# Check: /var/log/odoo/odoo.log or console output
```

**Check 3: Test sequence manually in Odoo Shell**
```bash
cd /home/toptec/Documents/odoo18e/server
./odoo-bin shell -d your_database_name
```

Then run:
```python
# Test sequence
seq_code = 'hr.training.evaluation'
next_num = env['ir.sequence'].next_by_code(seq_code)
print(f"Next sequence number: {next_num}")

# If None, sequence doesn't exist - create it:
if not next_num:
    env['ir.sequence'].create({
        'name': 'Training Evaluation Reference',
        'code': 'hr.training.evaluation',
        'prefix': 'EVAL/%(year)s/',
        'padding': 4,
        'number_increment': 1,
        'number_next': 1,
    })
    env.cr.commit()
    print("Sequence created!")
```

**Check 4: Verify the code is loaded**
```python
# In Odoo shell:
eval_obj = env['hr.training.evaluation']
import inspect
source = inspect.getsource(eval_obj.action_submit_part_a)
print(source)

# Look for: vals['name'] = self.env['ir.sequence'].next_by_code
```

**Check 5: Browser cache**
- Clear browser cache
- Hard refresh: Ctrl+Shift+R or Ctrl+F5
- Try incognito/private window

---

## Expected Sequence Numbers:

| Evaluation | Reference | After Submit |
|-----------|-----------|--------------|
| First | New | EVAL/2026/0001 |
| Second | New | EVAL/2026/0002 |
| Third | New | EVAL/2026/0003 |
| etc... | New | EVAL/2026/#### |

---

## Still Not Working?

Share:
1. Odoo version
2. Module version from Apps (should be 18.0.1.1.1)
3. Error messages from Odoo logs
4. Screenshot of the evaluation form after clicking Submit
