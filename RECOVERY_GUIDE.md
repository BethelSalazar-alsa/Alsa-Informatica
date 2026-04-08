# 🔧 Recovery Guide: licencia.contpaqi Model Registration

**Problem:** 404 Not Found - Model not in Odoo registry  
**Solution:** Complete redeployment with verification

---

## ✅ Fixes Already Applied

1. ✅ **Fixed `website_form_input_filter` method signature**
   - Removed invalid `request` parameter that prevented model loading
   - Changed from: `def website_form_input_filter(self, request, values)`
   - Changed to: `def website_form_input_filter(self, values)`

2. ✅ **Verified `__manifest__.py`**
   - Correct load order
   - All dependencies present
   - Data entries in proper sequence

3. ✅ **Validated Python syntax**
   - No syntax errors in any model file
   - All imports work correctly

---

## 🚀 Recovery Steps (In Order)

### Step 1: Full Module Uninstall
```bash
# In Odoo terminal/UI:
1. Navigate to: Apps → Search "Gestión de Licencias"
2. Click on the module
3. Click "Uninstall" button (bottom left)
4. Confirm when prompted
```

**Or via command line:**
```bash
# Restart Odoo with module uninstall filter
odoo -u gestion_licencias --db-filter='database_name' --stop-after-init
# Wait for it to complete and exit
```

### Step 2: Verify Clean State
```bash
# In Odoo database, check module is gone:
1. Apps → Search "Gestión de Licencias"
2. Should show "Install" button (not "Upgrade")
3. Check database has no `licencia_*` tables
```

### Step 3: Clear Odoo Cache (if using docker/server)
```bash
# If running Docker:
docker exec odoo-container rm -rf /var/lib/odoo/.cache

# If running locally:
rm -rf ~/.local/share/Odoo/addons/*
```

### Step 4: Fresh Module Install
```bash
# In Odoo terminal/UI:
1. Navigate to: Apps → Search "Gestión de Licencias"
2. Click on the module
3. Click "Install" button (now green)
4. Watch Odoo logs for any errors
5. Wait for message: "Modules loaded" or module state changes to "Installed"
```

**Or via command:**
```bash
# Install with verbose logging
odoo -d database_name -i gestion_licencias --log-level=debug --stop-after-init
```

### Step 5: Verify Model Registration
```bash
# In Odoo UI, try accessing the model:
1. Click menu item (or navigate to):
   - Licencias → Dashboard or List
2. Should load without 404 error
3. Check Odoo logs for any error messages
```

**Or test via XML-RPC:**
```python
# Using Python + Odoo client
import odoo
env = odoo.api.Environment(cr, uid, {})

# This should work without KeyError
try:
    Model = env['licencia.contpaqi']
    print(f"✅ Model loaded: {Model}")
    print(f"✅ Model name: {Model._name}")
    print(f"✅ Fields: {list(Model.fields_get().keys())}")
except KeyError as e:
    print(f"❌ ERROR: Model not in registry - {e}")
```

---

## 🔍 Troubleshooting If Still Broken

### Check 1: Verify Module File Integrity
```bash
# All these files must exist:
ls -la gestion_licencias/
  __manifest__.py       ✓
  __init__.py          ✓
  controllers/
    __init__.py        ✓
    main.py            ✓
  models/
    __init__.py        ✓
    licencia.py        ✓
    res_partner.py     ✓
    sale_order.py      ✓
    helpdesk_ticket.py ✓
  views/
    licencia_views.xml ✓
    res_partner_views.xml ✓
    sale_order_views.xml ✓
    helpdesk_ticket_views.xml ✓
    website_form_licencia.xml ✓
    website_snippets.xml ✓
  security/
    ir.model.access.csv ✓
  data/
    ir_cron.xml        ✓
```

### Check 2: Review Odoo Logs
```bash
# Watch for these specific error patterns:
grep -E "(ERROR|TRACEBACK|licencia|ImportError|SyntaxError)" /var/log/odoo/odoo.log

# Look specifically for model loading errors:
grep -i "licencia" /var/log/odoo/odoo.log | grep -E "(error|fail|exception)"
```

### Check 3: Validate XML Files
```bash
# Check each XML file for parse errors:
python3 -c "import xml.etree.ElementTree as ET; ET.parse('gestion_licencias/views/licencia_views.xml'); print('✓ Valid XML')"

# Repeat for all XML files...
```

### Check 4: Database Check
```sql
-- Connect to Odoo database and verify tables exist
SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE 'licencia%';

-- Should show:
-- licencia_contpaqi
-- licencia_linea
-- ir_model_fields (with licencia.contpaqi reference)
```

### Check 5: Module State Check
```python
# In Odoo Python console:
module = env['ir.module.module'].search([('name', '=', 'gestion_licencias')], limit=1)
if module:
    print(f"State: {module.state}")
    print(f"Last update: {module.last_update}")
    print(f"External ID: {module.external_id}")
else:
    print("Module record not found in database")
```

---

## 📋 Pre-Deployment Checklist

Before reinstalling, verify:

- [ ] All Python files have valid syntax (no ✗ symbols)
- [ ] `__manifest__.py` has proper structure
- [ ] `models/__init__.py` imports all models in correct order
- [ ] `models/licencia.py` has fixed `website_form_input_filter` (no `@api.model` decorator)
- [ ] `__manifest__.py` dependencies include: `['base', 'contacts', 'sale', 'mail', 'helpdesk', 'website', 'website_sale', 'hr_timesheet']`
- [ ] Data load order: security → licencia_views → inherited views → website → cron
- [ ] All XML files are well-formed
- [ ] No circular imports in `models/__init__.py`

---

## 🆘 Emergency Debug Mode

If nothing works, temporarily simplify the model:

**File: gestion_licencias/models/licencia.py - Minimal Version**
```python
from odoo import models, fields

class LicenciaContpaqi(models.Model):
    _name = 'licencia.contpaqi'
    _description = 'Gestión de Licencias'
    
    # Only essential fields
    name = fields.Char(string='Número de Serie', required=True)
    software_type = fields.Selection([
        ('contpaqi', 'CONTPAQi'),
        ('office', 'Microsoft Office'),
        ('antivirus', 'Antivirus'),
    ], string='Tipo de Software', default='contpaqi', required=True)


class LicenciaLinea(models.Model):
    _name = 'licencia.linea'
    _description = 'Equipos por Licencia'
    
    licencia_id = fields.Many2one('licencia.contpaqi', string='Licencia')
    nombre_equipo = fields.Char(string='Nombre del Equipo', required=True)
```

**Then gradually add back:**
1. Tracking fields
2. Relational fields
3. Onchange methods
4. Cron methods last

---

## 📞 Support Info

If you get new error messages after following this guide:

1. **Copy full error traceback from Odoo logs**
2. **Note exact line number in error**
3. **Check Odoo version:** `odoo --version` (should be 19.0)
4. **List installed modules:** `odoo -l` 
5. **Check Odoo is using correct database**

---

## ✅ Success Indicators

When the model is properly registered, you'll see:

1. ✅ No 404 errors when accessing the module
2. ✅ "Gestión de Licencias" appears in left menu
3. ✅ Can create new license records
4. ✅ Database has `licencia_contpaqi` and `licencia_linea` tables
5. ✅ Odoo logs show: "16 models loaded" (or similar count including your new models)

---

**Status:** Ready for redeployment
**Last Updated:** 2026-04-08
**Next Step:** Follow Steps 1-5 above in order
