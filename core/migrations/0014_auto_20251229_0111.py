# core/migrations/0014_load_initial_inventory.py
from django.db import migrations
from decimal import Decimal

# ✅ Define materials at the top level so both functions can use it
MATERIALS_LIST = [
    {
        "name": "Sulfuric Acid",
        "unit": "liters",
        "quantity": Decimal("120.50"),
        "max_quantity": Decimal("300.00"),
        "threshold": Decimal("80.00"),
    },
    {
        "name": "Sodium Chloride",
        "unit": "kg",
        "quantity": Decimal("0.00"),
        "max_quantity": Decimal("500.00"),
        "threshold": Decimal("50.00"),
    },
    {
        "name": "Ethanol",
        "unit": "liters",
        "quantity": Decimal("200.00"),
        "max_quantity": Decimal("400.00"),
        "threshold": Decimal("100.00"),
    },
    {
        "name": "Calcium Carbonate",
        "unit": "kg",
        "quantity": Decimal("75.25"),
        "max_quantity": Decimal("200.00"),
        "threshold": Decimal("60.00"),
    },
]

def load_data(apps, schema_editor):
    Material = apps.get_model('core', 'Material')
    Material.objects.all().delete()  # Only for dev!
    
    for mat in MATERIALS_LIST:
        Material.objects.create(**mat)

def reverse_data(apps, schema_editor):
    Material = apps.get_model('core', 'Material')
    # ✅ Now MATERIALS_LIST is accessible here
    names = [m["name"] for m in MATERIALS_LIST]
    Material.objects.filter(name__in=names).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0013_merge_20251229_0106'),  # ← Use your actual last migration name
    ]

    operations = [
        migrations.RunPython(load_data, reverse_data),
    ]