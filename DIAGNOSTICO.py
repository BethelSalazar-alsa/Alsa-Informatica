#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la integridad del módulo gestion_licencias
"""

import os
import sys
import xml.etree.ElementTree as ET

# Colores para consola
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_file(path, name):
    """Verifica que un archivo exista"""
    if os.path.exists(path):
        print(f"{Colors.GREEN}✓{Colors.END} {name}: {path}")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {name} FALTANTE: {path}")
        return False

def check_xml(path, name):
    """Verifica que un XML esté bien formado"""
    if not os.path.exists(path):
        print(f"{Colors.RED}✗{Colors.END} {name} NO EXISTE: {path}")
        return False
    
    try:
        tree = ET.parse(path)
        print(f"{Colors.GREEN}✓{Colors.END} {name}: XML válido")
        return True
    except ET.ParseError as e:
        print(f"{Colors.RED}✗{Colors.END} {name}: ERROR XML - {e}")
        return False

def check_python(path, name):
    """Verifica que un archivo Python esté bien formado"""
    if not os.path.exists(path):
        print(f"{Colors.RED}✗{Colors.END} {name} NO EXISTE: {path}")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        compile(content, path, 'exec')
        print(f"{Colors.GREEN}✓{Colors.END} {name}: Sintaxis válida")
        return True
    except SyntaxError as e:
        print(f"{Colors.RED}✗{Colors.END} {name}: ERROR SYNTAX - Línea {e.lineno}: {e.msg}")
        return False

print(f"{Colors.BLUE}=== DIAGNÓSTICO DEL MÓDULO GESTION_LICENCIAS ==={Colors.END}\n")

base_path = os.path.dirname(__file__)

# Verificar archivos Python
print(f"{Colors.BLUE}Verificando archivos Python:{Colors.END}")
py_files = [
    ('gestion_licencias/__init__.py', '__init__.py'),
    ('gestion_licencias/models/__init__.py', 'models/__init__.py'),
    ('gestion_licencias/models/licencia.py', 'models/licencia.py'),
    ('gestion_licencias/models/res_partner.py', 'models/res_partner.py'),
    ('gestion_licencias/models/sale_order.py', 'models/sale_order.py'),
    ('gestion_licencias/models/helpdesk_ticket.py', 'models/helpdesk_ticket.py'),
]

py_ok = True
for rel_path, name in py_files:
    full_path = os.path.join(base_path, rel_path)
    if not check_python(full_path, name):
        py_ok = False

print()

# Verificar archivos XML
print(f"{Colors.BLUE}Verificando archivos XML:{Colors.END}")
xml_files = [
    ('gestion_licencias/security/ir.model.access.csv', 'security/ir.model.access.csv (no es XML pero lo verificamos)'),
    ('gestion_licencias/data/ir_cron.xml', 'data/ir_cron.xml'),
    ('gestion_licencias/views/licencia_views.xml', 'views/licencia_views.xml'),
    ('gestion_licencias/views/res_partner_views.xml', 'views/res_partner_views.xml'),
    ('gestion_licencias/views/sale_order_views.xml', 'views/sale_order_views.xml'),
    ('gestion_licencias/views/helpdesk_ticket_views.xml', 'views/helpdesk_ticket_views.xml'),
    ('gestion_licencias/views/website_form_licencia.xml', 'views/website_form_licencia.xml'),
    ('gestion_licencias/views/website_snippets.xml', 'views/website_snippets.xml'),
]

xml_ok = True
for rel_path, name in xml_files:
    full_path = os.path.join(base_path, rel_path)
    if '.csv' in rel_path:
        if not check_file(full_path, name):
            xml_ok = False
    else:
        if not check_xml(full_path, name):
            xml_ok = False

print()

# Verificar __manifest__.py
print(f"{Colors.BLUE}Verificando __manifest__.py:{Colors.END}")
manifest_path = os.path.join(base_path, 'gestion_licencias/__manifest__.py')
if not check_python(manifest_path, '__manifest__.py'):
    py_ok = False
else:
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
            if "'installable': True" in manifest_content:
                print(f"{Colors.GREEN}✓{Colors.END} Módulo marcado como instalable")
            else:
                print(f"{Colors.RED}✗{Colors.END} Módulo NO está marcado como instalable")
    except:
        pass

print()

# Resumen
print(f"{Colors.BLUE}=== RESUMEN ==={Colors.END}")
if py_ok and xml_ok:
    print(f"{Colors.GREEN}✓ Todos los archivos están correctos{Colors.END}")
else:
    if not py_ok:
        print(f"{Colors.RED}✗ Hay errores en archivos Python{Colors.END}")
    if not xml_ok:
        print(f"{Colors.RED}✗ Hay errores en archivos XML{Colors.END}")

print()
print(f"{Colors.YELLOW}Próximos pasos en Odoo:{Colors.END}")
print("1. Ve a Aplicaciones (Apps)")
print("2. Busca 'Gestión de Licencias Contpaqi'")
print("3. Si existe, haz clic en 'Desinstalar' (Uninstall)")
print("4. Luego haz clic en 'Instalar' (Install)")
print("5. Si hay error, revisa los logs del servidor Odoo")
