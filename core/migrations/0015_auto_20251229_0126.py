# core/migrations/0015_load_initial_inventory.py
from django.db import migrations
from decimal import Decimal

MATERIALS = [
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
    # Clear existing data (only in dev!)
    Material.objects.all().delete()
    for mat in MATERIALS:
        Material.objects.create(**mat)

def reverse_data(apps, schema_editor):
    Material = apps.get_model('core', 'Material')
    names = [m["name"] for m in MATERIALS]
    Material.objects.filter(name__in=names).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0014_auto_20251229_0111'),  # ✅ Depends on last migration
    ]

    operations = [
        migrations.RunPython(load_data, reverse_data),
    ]