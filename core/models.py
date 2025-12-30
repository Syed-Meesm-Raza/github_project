# core/models.py
from django.db import models
from django.utils import timezone
from django.db.models import Max
import hashlib

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True,blank=True)
    phone = models.CharField(max_length=15, blank=True)
    company = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='avatars/' , blank=True , null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_initials(self):
        """Get initials for avatar (e.g., 'John Doe' → 'JD')"""
        if not self.name:
            return "?"
        parts = self.name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        else:
            return self.name[:2].upper() if len(self.name) >= 2 else self.name[0].upper()

    def get_avatar_color(self):
        """Generate consistent background color based on client name"""
        if not self.name:
            return "#0891b2"
        
        # Create consistent hash from client name
        hash_obj = hashlib.md5(self.name.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Use hash to generate color (ensure good contrast)
        r = int(hash_hex[0:2], 16)
        g = int(hash_hex[2:4], 16)
        b = int(hash_hex[4:6], 16)
        
        # Darken if too bright for better text visibility
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        if brightness > 180:
            r = max(0, r - 60)
            g = max(0, g - 60)
            b = max(0, b - 60)
            
        return f"#{r:02x}{g:02x}{b:02x}"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('sample_preparing', 'Sample Preparing'),
        ('production_starts', 'Production Starts'),
        ('quality_checking', 'Quality Checking'),
        ('ready_for_shipment', 'Ready for Shipment'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
    ]
    order_id = models.CharField(max_length=20, unique=True, blank=True)
    fabric_type = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    payment = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='sample_preparing')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True) 
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('credit_card', 'Credit Card'),
            ('upi', 'UPI'),
            ('other', 'Other')
        ],
        default='bank_transfer'
    )
    
    @property
    def remaining_amount(self):
        return self.payment - self.paid_amount
    
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate order ID like ORD-1001
            last_order = Order.objects.order_by('-id').first()
            next_id = 1 if not last_order else last_order.id + 1
            self.order_id = f"ORD-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_id} - {self.client.name}"

class VendorBill(models.Model):
    vendor_name = models.CharField(max_length=100)
    amount = models.FloatField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, default='unpaid')

class Material(models.Model):
    name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, default='kg')
    max_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    threshold = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    vendor = models.CharField(max_length=200, blank=True, null=True)
    last_updated = models.DateField(auto_now=True)  # ← Use DateField, not DateTimeField
    created_at = models.DateField(auto_now_add=True)  # ← Use DateField, not DateTimeField

    def __str__(self):
        return self.name

class Invoice(models.Model):
    INVOICE_PREFIX = "INV"

    # Core fields
    invoice_id = models.CharField(max_length=50, unique=True, editable=False)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('upi', 'UPI'),
        ('other', 'Other')
    ])
    created_at = models.DateTimeField(default=timezone.now)

    # Denormalized for reliability (in case client/order changes later)
    client_name = models.CharField(max_length=100)
    client_id = models.IntegerField()
    order_id_display = models.CharField(max_length=50)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    company_name = models.CharField(max_length=100, default="Penta Industries")
    company_address = models.TextField(default="123 Chemical Park, Mumbai, India")

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = self.generate_invoice_id()
        if not self.pk:  # Only on creation
            # Freeze client & order details at time of invoice
            self.client_name = self.order.client.name
            self.client_id = self.order.client.id
            self.order_id_display = self.order.order_id
            self.order_total = self.order.payment
        super().save(*args, **kwargs)

    def generate_invoice_id(self):
        year = timezone.now().year
        last_invoice = Invoice.objects.filter(
            invoice_id__startswith=f"{self.INVOICE_PREFIX}-{year}-"
        ).aggregate(Max('invoice_id'))['invoice_id__max']
        
        if last_invoice:
            last_num = int(last_invoice.split('-')[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        
        return f"{self.INVOICE_PREFIX}-{year}-{next_num:03d}"

    def __str__(self):
        return self.invoice_id

    class Meta:
        ordering = ['-created_at']  