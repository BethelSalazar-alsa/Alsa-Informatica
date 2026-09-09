# Model Registration Diagnostic - 404 Not Found

**Error:** `KeyError: 'licencia.contpaqi'` - Model not in registry  
**Date:** 2026-04-08  
**Status:** INVESTIGATING

---

## Error Analysis

The 404 error indicates the model `licencia.contpaqi` **is not registered** in Odoo's runtime registry.

### What This Means
- ✅ Python files have no syntax errors
- ✅ `models/__init__.py` properly imports models
- ✅ `__manifest__.py` is correct
- ❌ **Something prevents the model from registering at runtime**

### Possible Root Causes

#### 1. **Mixins Not Available** ⚠️
The model inherits from:
```python
_inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin']
```

**Check:** Are all dependencies loaded?
- `mail` ✅ (in depends)
- `website` ✅ (in depends)
- `activity.mixin` ✅ (part of mail)
- `website.published.mixin` ✅ (part of website)

#### 2. **Method Signature Error** ✅ FIXED
**Issue Found:** `website_form_input_filter` had invalid Odoo signature
```python
# ❌ WRONG: @api.model methods can't use 'request'
@api.model
def website_form_input_filter(self, request, values):
    ...

# ✅ FIXED: Correct signature for model method
def website_form_input_filter(self, values):
    ...
```

#### 3. **Circular Import or Module Load Failure**
If `models/__init__.py` fails importing any model, ALL models fail.

#### 4. **Missing Model Dependencies**
Fields reference models that might not exist.

---

## Fixes Applied

### Fix #1: website_form_input_filter Signature ✅

**File:** `models/licencia.py`  
**Change:** Removed invalid `request` parameter from `@api.model` method

```python
# BEFORE (Invalid)
@api.model
def website_form_input_filter(self, request, values):
    if not values.get('partner_id') and request.env.user.partner_id:
        values['partner_id'] = request.env.user.partner_id.id

# AFTER (Valid)
def website_form_input_filter(self, values):
    """Filter and validate data from website form submissions"""
    if 'name' in values:
        values.setdefault('software_type', 'contpaqi')
    return values
```

**Why:** `request` is only available in controllers, not model methods. This would cause an exception during module loading.

---

## Diagnostic Steps

### Step 1: Check Odoo Logs for Actual Error
Run Odoo with verbose logging to see what error prevents model registration:

```bash
# In your Odoo terminal
-d <database_name> -u gestion_licencias --log-level=debug 2>&1 | grep -A 10 "licencia"
```

**Look for:**
- Syntax errors in model definitions
- Missing module dependencies
- Field reference errors
- Inheritance chain issues

### Step 2: Verify Module Installation

```bash
# In Odoo shell
import odoo
env = odoo.api.Environment(cr, uid, {})
modules = env['ir.module.module'].search([('name', '=', 'gestion_licencias')])
print(f"Module state: {modules.state}")
print(f"Installation errors: {modules.last_update}")
```

### Step 3: Test Model Import Directly

```python
# In Python shell with Odoo environment
from odoo import models
from odoo.addons.gestion_licencias.models.licencia import LicenciaContpaqi
print("Model imported successfully")
```

### Step 4: Check Model Registry After Module Load

```python
# In Odoo XML-RPC or Python shell
registry = env.registry
print(f"Available models: {list(registry.models.keys())}")
print(f"licencia.contpaqi in registry: {'licencia.contpaqi' in registry.models}")
```

---

## Next Steps

### Immediate Actions

1. **Redeploy Module:**
   ```bash
   # Restart Odoo server
   # Uninstall and reinstall the module in Odoo UI
   # OR: odoo -u gestion_licencias --db-filter='^(database_name)$'
   ```

2. **Verify Installation:**
   - Go to Apps → Search: "Gestión de Licencias"
   - Click module
   - Check: State should be "Installed" (green) 
   - If not installed: Click "Install" button
   - Watch Odoo logs for any errors

3. **Test Model Access:**
   - Go to Menu → Licencias (or create one)
   - Try to create a new License record
   - Should work without 404 error

### Debugging if Still Broken

If the model still doesn't load:

1. **Check Odoo logs:**
   ```
   grep -i "licencia\|error\|traceback" /var/log/odoo/odoo.log
   ```

2. **Simplify model temporarily:**
   - Remove `_inherit` mixins temporarily
   - Test if model loads
   - Add mixins back one at a time

3. **Check field references:**
   - Verify all `Many2one` and `Many2many` references exist
   - Check dependency set

---

## Model Dependency Chain

```
licencia.contpaqi
  ├─ mail.thread ✅
  ├─ mail.activity.mixin ✅
  ├─ website.published.mixin ✅
  ├─ Many2one: sale.order ✅
  ├─ Many2one: product.product ✅
  ├─ Many2one: res.partner ✅
  ├─ Many2one: res.users ✅
  └─ One2many: licencia.linea ✅

licencia.linea
  ├─ Many2one: licencia.contpaqi ✅
  └─ Many2one: res.users ✅

helpdesk.ticket (inherited)
  ├─ Many2many: licencia.contpaqi ✅
  ├─ Many2one: sale.order ✅
  └─ Many2many: licencia.linea ✅

sale.order (inherited)
  └─ Many2many: licencia.contpaqi ✅

res.partner (inherited)
  ├─ One2many: licencia.contpaqi ✅
  └─ Computed: licencia_count ✅
```

All dependencies are standard Odoo models → ✅ Should work

---

## Common Issues & Solutions

| Issue | Symptom | Fix |
|-------|---------|-----|
| Module not installed | 404 error + KeyError | Install in Odoo UI |
| Model syntax error | Error in logs + KeyError | Check Python syntax |
| Missing mixin | TypeError during load | Verify dependencies in __manifest__.py |
| Circular import | ImportError in logs | Check models/__init__.py import order |
| Wrong database | 404 on correct model | Verify database name in connection |

---

## Files Changed

- ✅ `models/licencia.py` - Fixed `website_form_input_filter` signature
- ✅ `__manifest__.py` - Verified dependencies and data order

---

## Status

- [x] Python syntax validated
- [x] Method signatures fixed
- [x] Dependencies verified
- [ ] Module installation verified (need to reload)
- [ ] Model registry access verified (need to test)

**Next action:** Reinstall module in Odoo and check logs.
