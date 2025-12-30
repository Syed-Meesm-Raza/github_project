import os
import django

# 1. Setup Django so we can connect to the database
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# 2. Connect to the database
from django.db import connection

print("Attempting to remove the 'total_amount' column...")

try:
    # 3. Execute the SQL command
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE core_order DROP COLUMN total_amount;")
        
    print("✅ SUCCESS! The 'total_amount' column has been removed.")
    print("You can now try to create an order again.")

except Exception as e:
    error_message = str(e)
    if "no such column" in error_message:
        print("ℹ️  The column 'total_amount' is already gone. No action needed.")
    else:
        print(f"❌ ERROR: {e}")

print("\nPress Enter to close...")
input()