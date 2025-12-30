from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Client, Invoice, Order
from .forms import ClientForm, OrderForm
from  django.http import JsonResponse
from .models import Client, Order, Material
from django.urls import reverse
from django.db.models import Q, Count, Sum , F
from core.models import Material
import json
from datetime import datetime
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from django.http import HttpResponse
import random
from django.template.loader import render_to_string
import os
import tempfile
import subprocess
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from .models import Invoice
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.template.loader import render_to_string
from django.db import models

BANKS = [
    "Global Trust Bank",
    "Penta Financial Services",
    "Horizon Capital Bank",
    "Summit National Bank",
    "Vertex Banking, Ltd."
]

IBANS = [
    "DE89370400440532013000",
    "FR1420041010050500013M02606",
    "GB29NWBK60161331926819",
    "IT60X0542811101000000123456",
    "ES9121000418450200051332"
]

def get_bank_details(invoice_id):
    """Return consistent bank name and IBAN for a given invoice ID."""
    index = invoice_id % len(BANKS)  # Always same index for same ID
    return BANKS[index], IBANS[index]

def main_dashboard(request):
    clients = Client.objects.all()
    orders = Order.objects.all()
    materials = Material.objects.all()
    return render(request, 'main.html', {
        'clients': clients,
        'orders': orders,
        'materials': materials
    })

def client_detail(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    orders = Order.objects.filter(client=client)
    return render(request, 'client.html', {
        'client': client,
        'orders': orders
    })

def order_list(request):
    orders = Order.objects.all()
    completed_orders = [o for o in orders if o.status == 'completed']
    pending_orders = [o for o in orders if o.status != 'completed']
    return render(request, 'orders.html', {
        'orders': orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders
    })

def inventory_view(request):
    materials = Material.objects.all()
    low_stock = [m for m in materials if m.current_stock < m.threshold_amount]
    return render(request, 'inventory.html', {
        'materials': materials,
        'low_stock': low_stock
    })

def finance_view(request):
    # For now, use mock data (replace with real models later)
    client_invoices = [
        {'client': 'Ali Khan', 'amount': 5000, 'due_date': '2025-12-31', 'status': 'paid'},
        {'client': 'Sara Ahmed', 'amount': 3000, 'due_date': '2025-12-15', 'status': 'unpaid'}
    ]
    vendor_bills = [
        {'vendor': 'Polymer Co', 'amount': 2000, 'due_date': '2025-12-20', 'status': 'unpaid'},
        {'vendor': 'Chemical Ltd', 'amount': 1500, 'due_date': '2025-12-10', 'status': 'paid'}
    ]
    return render(request, 'finance.html', {
        'client_invoices': client_invoices,
        'vendor_bills': vendor_bills
    })

def home(request):
    return render(request, 'main.html')  # or whatever template you want
def client_dashboard(request):
    # === CALCULATE STATS ===
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(is_active=True).count()
    inactive_clients = Client.objects.filter(is_active=False).count()

    # Clients created this month
    now = datetime.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month_clients = Client.objects.filter(created_at__gte=start_of_month).count()
    
    # return render(request, 'client.html', {
    #     'clients': clients,
    #     'form': form,
    #     'all_clients_json': all_clients_json,
    #     'total_clients': total_clients,
    #     'active_clients': active_clients,
    #     'inactive_clients': inactive_clients,
    #     'this_month_clients': this_month_clients,
    # })
    
    # Handle DELETE
    if request.method == "POST" and "delete_client" in request.POST:
        client_id = request.POST.get("client_id")
        client = get_object_or_404(Client, id=client_id)
        client_name = client.name
        client.delete()
        messages.success(request, f"Client '{client_name}' deleted successfully.")
        return redirect('client_dashboard')

    # Handle CREATE/UPDATE (POST)
    if request.method == "POST":
        client_id = request.POST.get("client_id")
        if client_id:
            client = get_object_or_404(Client, id=client_id)
            form = ClientForm(request.POST, request.FILES, instance=client)
        else:
            form = ClientForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            action = "updated" if client_id else "added"
            messages.success(request, f"Client {action} successfully.")
            return redirect('client_dashboard')
    else:
        form = ClientForm()

        # === FILTER & SEARCH LOGIC ===
    clients = Client.objects.all()
    search = request.GET.get('search')
    status = request.GET.get('status')

    # === FILTER & SEARCH LOGIC ===
    clients = Client.objects.all()
    search = request.GET.get('search')
    status = request.GET.get('status')

    # === SEARCH LOGIC ===
    if search:
        # Logic:
        # 1. Name starts with 'search' (e.g., "a" finds "Ahmed")
        # 2. Name contains " search" (e.g., " Baig" finds "Saad Baig")
        # 3. Company starts with 'search' (e.g., "Ham" finds "Hamdard")
        query_filter = (
            Q(name__istartswith=search) | 
            Q(name__icontains=" " + search) | 
            Q(company__istartswith=search)
        )
        
        # If search is a number (e.g., "31"), also check Client ID
        if search.isdigit():
            query_filter |= Q(id=int(search))
            
        clients = clients.filter(query_filter)

    # === STATUS FILTER LOGIC ===
    if status == 'active':
        clients = clients.filter(is_active=True)
    elif status == 'inactive':
        clients = clients.filter(is_active=False)
        
    return render(request, 'client.html', {
        'clients': clients,
        'form': form,
        'total_clients': total_clients,
        'active_clients': active_clients,
        'inactive_clients': inactive_clients,
        'this_month_clients': this_month_clients,
    })
    
    

def order_dashboard(request):
    orders = Order.objects.select_related('client').all()  # Efficient query

    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    # ====================================
    # === SEARCH LOGIC ===
    search_query = request.GET.get('search', '')
    if search_query:
        # Search ONLY in Order ID and Fabric Type (Quantity handled below)
        query_filter = (
            Q(order_id__icontains=search_query) |
            Q(fabric_type__istartswith=search_query) 
            # REMOVED: Q(client__name__icontains=search_query) to prevent false matches
        )
        
        # If the user types numbers, also check Quantity AND Client ID
        if search_query.isdigit():
            query_filter |= Q(quantity=int(search_query)) | Q(client__id=int(search_query))
            
        orders = orders.filter(query_filter)
    
    #Handles delete
    if request.method == "POST" and "delete_order" in request.POST:
        order_id = request.POST.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        order_id_str = order.order_id
        order.delete()
        messages.success(request, f"Order {order_id_str} deleted successfully.")
        return redirect('order_dashboard')
    
    # Handle EDIT (Update)
    if request.method == "POST" and "edit_order" in request.POST:
        order_id = request.POST.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        # Bind the form to the existing order instance
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order {order.order_id} updated successfully.")
            return redirect('order_dashboard')
    
    else:
        form = OrderForm() # Empty form for the modal
    
       # === REAL-TIME STATS ===
    
    # 1. Total Orders: Count everything
    total_orders = Order.objects.all().count()
    
    # 2. Pending: Count ALL orders EXCEPT 'completed'
    # This includes: Sample Preparing, Production Starts, Quality Checking, Ready for Shipment, and Shipped
    pending = Order.objects.exclude(status='completed').count()
    
    # 3. Shipped: Count orders with specific status 'shipped'
    shipped = Order.objects.filter(status='shipped').count()
    
    # 4. Completed: Count orders with specific status 'completed'
    completed = Order.objects.filter(status='completed').count()

    return render(request, 'orders.html', {
        'orders': orders,
        'form': form,
        'total_orders': total_orders,
        'pending': pending,
        'shipped': shipped,
        'completed': completed,
    })
    
def add_order_for_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            print("Form errors:", form.errors)  # 👈 Add this
            order = form.save(commit=False)
            order.client = client  # Link to client
            order.save()
            print("✅ Order saved:", order.order_id)
            messages.success(request, f"Order {order.order_id} added successfully for {client.name}!")
            return redirect('order_dashboard')
    else:
        form = OrderForm()

    return render(request, 'add_order.html', {
        'form': form,
        'client': client
    })
from django.shortcuts import render

def inventory_dashboard(request):
    if request.method == 'POST':
        # --- DELETE ---
        if 'delete_material' in request.POST:
            material_id = request.POST.get('material_id')
            try:
                Material.objects.filter(id=material_id).delete()
                messages.success(request, "Material deleted successfully.")
            except Exception as e:
                messages.error(request, "Failed to delete material.")

        # --- EDIT ---
        elif 'edit_material' in request.POST:
            material_id = request.POST.get('material_id')
            try:
                material = Material.objects.get(id=material_id)
                material.name = request.POST['name'].strip()
                material.quantity = Decimal(request.POST['quantity'])
                material.unit = request.POST['unit']
                material.max_quantity = Decimal(request.POST['max_quantity'])
                material.threshold = Decimal(request.POST['threshold'])
                material.save()
                messages.success(request, "Material updated successfully.")
            except Material.DoesNotExist:
                messages.error(request, "Material not found.")
            except (InvalidOperation, ValueError):
                messages.error(request, "Invalid number format in quantity fields.")
            except Exception as e:
                messages.error(request, f"Error updating material: {str(e)}")

        # --- ADD (only if NOT edit/delete) ---
        elif 'name' in request.POST and 'quantity' in request.POST:
            try:
                material = Material(
                    name=request.POST['name'].strip(),
                    quantity=Decimal(request.POST['quantity']),
                    unit=request.POST['unit'],
                    max_quantity=Decimal(request.POST['max_quantity']),
                    threshold=Decimal(request.POST['threshold'])
                )
                material.save()
                messages.success(request, f"Material '{material.name}' added successfully.")
            except (InvalidOperation, ValueError):
                messages.error(request, "Invalid number format in quantity fields.")
            except Exception as e:
                messages.error(request, f"Failed to add material: {str(e)}")

        return redirect('inventory_dashboard')
    
    # ... GET logic ...

        # === HANDLE GET: FILTERING & SEARCH ===
    materials = Material.objects.all()
    search_query = request.GET.get('search')
    status_filter = request.GET.get('status')

    # Apply search
    if search_query:
        materials = materials.filter(name__icontains=search_query)

    # Apply status filter
    if status_filter == 'out_of_stock':
        materials = materials.filter(quantity=0)
    elif status_filter == 'low_stock':
        materials = materials.filter(quantity__gt=0, quantity__lt=F('threshold'))
    elif status_filter == 'in_stock':
        materials = materials.filter(quantity__gt=0)

    # Compute stats based on **filtered** materials (optional)
    # Or keep stats for ALL materials — your choice
    all_materials = Material.objects.all()
    total_materials = all_materials.count()
    out_of_stock = all_materials.filter(quantity=0).count()
    # In Stock = everything with quantity > 0
    in_stock = all_materials.filter(quantity__gt=0).count()
    # Low Stock = subset of in_stock
    low_stock = all_materials.filter(quantity__gt=0, quantity__lt=F('threshold')).count()

    # Add computed fields for each material (for cards)
    for mat in materials:
        q = mat.quantity
        t = mat.threshold
        if q <= 0:
            mat.status = 'danger'
        elif q <= t:
            mat.status = 'danger'  # or 'warning' if you prefer
        elif q < t * Decimal('1.5'):
            mat.status = 'warning'
        else:
            mat.status = 'fill'

        max_q = max(mat.max_quantity, Decimal('1'))
        mat.bar_width = min(100, int((q / max_q) * 100))
        mat.bar_class = mat.status
        mat.show_warning = q < t

    context = {
        'materials': materials,
        'total_materials': total_materials,
        'in_stock': in_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    }
    return render(request, 'inventory.html', context)


def finance_dashboard(request):
    if request.method == 'POST':
        
         # ✅ Handle Edit Invoice
        if 'edit_invoice' in request.POST:
            try:
                invoice_id = request.POST.get('invoice_id')
                amount = Decimal(request.POST.get('amount'))
                payment_method = request.POST.get('payment_method', '').strip()
                if payment_method not in ['cash', 'bank_transfer', 'credit_card', 'upi', 'other']:
                    payment_method = 'cash'

                invoice = Invoice.objects.get(id=invoice_id)
                invoice.amount = amount
                invoice.payment_method = payment_method
                invoice.save()
                messages.success(request, "Invoice updated successfully.")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
            return redirect('finance_dashboard')

        # ✅ Handle Delete Invoice
        elif 'delete_invoice' in request.POST:
            try:
                invoice_id = request.POST.get('invoice_id')
                invoice = Invoice.objects.get(id=invoice_id)
                invoice.delete()
                messages.success(request, "Invoice deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
            return redirect('finance_dashboard')

        # ✅ Handle Record Payment (your existing logic)
        
        elif 'record_payment' in request.POST:
            try:
                order_id = request.POST.get('order_id')
                new_total_paid = Decimal(request.POST.get('paid_amount', '0'))

                order = Order.objects.get(id=order_id)

                if new_total_paid < 0:
                    messages.error(request, "Paid amount cannot be negative.")
                elif new_total_paid > order.payment:
                    messages.error(request, f"Paid amount cannot exceed total invoice amount (${order.payment}).")
                else:
                    # ✅ DELETE all existing invoices
                    Invoice.objects.filter(order=order).delete()

                    # ✅ ALWAYS create a new invoice — even if $0
                    Invoice.objects.create(
                        order=order,
                        amount=new_total_paid,
                        payment_method='cash'  # or omit if you remove payment_method
                    )

                    messages.success(request, "Payment updated successfully.")
            except (Order.DoesNotExist, ValueError, Exception) as e:
                messages.error(request, f"Error: {str(e)}")
    
            return redirect('finance_dashboard')
    
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
        
    
    client_invoices = Order.objects.select_related('client').prefetch_related('invoices').annotate(
        total_paid=Coalesce(Sum('invoices__amount'), 0, output_field=DecimalField()),
        db_remaining=F('payment') - Coalesce(Sum('invoices__amount'), 0, output_field=DecimalField())
    )
    
    # Apply search filter
    if search_query:
        client_invoices = client_invoices.filter(
            Q(client__name__icontains=search_query) |
            Q(client__id__icontains=search_query) |
            Q(order_id__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter:
        if status_filter == 'paid':
            client_invoices = client_invoices.filter(db_remaining__lte=0)
        elif status_filter == 'partial':
            client_invoices = client_invoices.filter(db_remaining__gt=0, total_paid__gt=0)
        elif status_filter == 'pending':
            client_invoices = client_invoices.filter(total_paid=0)

    # ✅ Calculate stats AFTER client_invoices is defined
    # Calculate stats
    total_invoices = client_invoices.count()
    paid_invoices = client_invoices.filter(db_remaining__lte=0).count()
    unpaid_invoices = total_invoices - paid_invoices

    context = {
    'client_invoices': client_invoices,
    'vendor_bills': [],
    'total_invoices': total_invoices,
    'paid_invoices': paid_invoices,
    'unpaid_invoices': unpaid_invoices,
}
    return render(request, 'finance.html', context)
        
            # try:
            #     order_id = request.POST.get('order_id') 
            #     amount = Decimal(request.POST.get('paid_amount'))
            #     # ✅ Fixed: clean and validate
            #     payment_method = request.POST.get('payment_method', '').strip()
            #     if payment_method not in ['cash', 'bank_transfer', 'credit_card', 'upi', 'other']:
            #         payment_method = 'cash'  # fallback
                
            #     print(">>> SAVING PAYMENT METHOD:", repr(payment_method))

            #     order = Order.objects.get(id=order_id)
            #     total_paid = order.invoices.aggregate(total=Sum('amount'))['total'] or 0
            #     remaining = order.payment - total_paid

            #     if amount <= 0:
            #         messages.error(request, "Amount must be greater than zero.")
            #     elif amount > remaining:
            #         messages.error(request, f"Amount exceeds remaining balance (₹{remaining}).")
            #     else:
            #         Invoice.objects.create(
            #             order=order,
            #             amount=amount,
            #             payment_method=payment_method
            #         )
            #         messages.success(request, "Payment recorded and invoice created.")
            # except Exception as e:
            #     messages.error(request, f"Error: {str(e)}")
            
            # # ✅ ALWAYS return after POST
            # return redirect('finance_dashboard')

       

    # ✅ Use a DIFFERENT name for the annotation
    client_invoices = Order.objects.select_related('client').prefetch_related('invoices').annotate(
        total_paid=Coalesce(Sum('invoices__amount'), 0, output_field=DecimalField()),
        db_remaining=F('payment') - Coalesce(Sum('invoices__amount'), 0, output_field=DecimalField())
    )
    context = {
        'client_invoices': client_invoices,
        'vendor_bills': [],
    }
    return render(request, 'finance.html', context)

    

def client_search_api(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    clients = Client.objects.filter(
        Q(name__icontains=query) | Q(email__icontains=query)
    )[:10]  # Limit to 10 results

    results = [
        {
            'id': client.id,
            'display': f"CL-{client.id} – {client.name}",
            'name': client.name,
            'email': client.email,
        }
        for client in clients
    ]
    return JsonResponse(results, safe=False)

# views.py
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    order = invoice.order  # ✅ Get related order

    # ✅ Calculate total paid and remaining
    total_paid = order.invoices.aggregate(total=models.Sum('amount'))['total'] or 0
    remaining = order.payment - total_paid
    
    bank_name , iban = get_bank_details(invoice_id)

    # ✅ Generate random bank + IBAN
    # banks = [
    #     "Global Trust Bank",
    #     "Penta Financial Services",
    #     "Horizon Capital Bank",
    #     "Summit National Bank",
    #     "Vertex Banking Group"
    # ]
    # ibans = [
    #     "DE89370400440532013000",
    #     "FR1420041010050500013M02606",
    #     "GB29NWBK60161331926819",
    #     "IT60X0542811101000000123456",
    #     "ES9121000418450200051332"
    # ]
    # bank_name = random.choice(banks)
    # iban = random.choice(ibans)

    # ✅ PASS ALL REQUIRED VARIABLES TO TEMPLATE
    context = {
        'invoice': invoice,
        'order': order,  # ✅ Needed for client/order info
        'paid_amount': total_paid,  # ✅ For Payment Summary
        'remaining_amount': remaining,  # ✅ For Remaining & Due Amount
        'bank_name': bank_name,  # ✅ For Bank Details
        'iban': iban,  # ✅ For Bank Details
    }

    return render(request, 'invoice_detail.html', context)


def download_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    order = invoice.order

    # ✅ Calculate paid & remaining (same as view_invoice)
    total_paid = order.invoices.aggregate(total=models.Sum('amount'))['total'] or 0
    remaining = order.payment - total_paid
    
    bank_name , iban = get_bank_details(invoice_id)
    
    # # ✅ Generate bank + IBAN (same as view_invoice)
    # banks = [
    #     "Global Trust Bank",
    #     "Penta Financial Services",
    #     "Horizon Capital Bank",
    #     "Summit National Bank",
    #     "Vertex Banking, Ltd."
    # ]
    # ibans = [
    #     "DE89370400440532013000",
    #     "FR1420041010050500013M02606",
    #     "GB29NWBK60161331926819",
    #     "IT60X0542811101000000123456",
    #     "ES9121000418450200051332"
    # ]
    # bank_name = random.choice(banks)
    # iban = random.choice(ibans)

    # ✅ PASS FULL CONTEXT (critical!)
    context = {
        'invoice': invoice,
        'order': order,
        'paid_amount': total_paid,
        'remaining_amount': remaining,
        'bank_name': bank_name,
        'iban': iban,
    }

    # 🔸 Use the SAME template as your web view!
    # If your web uses 'invoice_detail.html', use that — NOT 'invoice_pdf.html'
    html_content = render_to_string('invoice_detail.html', context)

    # Rest of your WeasyPrint logic (unchanged)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as html_file:
        html_file.write(html_content)
        html_path = html_file.name

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
        pdf_path = pdf_file.name

    try:
        WEASYPRINT_PATH = r"D:\project1\weasyprint-windows\dist\weasyprint.exe"
        result = subprocess.run(
            [WEASYPRINT_PATH, html_path, pdf_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print("WeasyPrint Error:", result.stderr)
            messages.error(request, "Failed to generate PDF.")
            return redirect('finance_dashboard')

        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Invoice_INV-{invoice.id}.pdf"'
        return response

    except subprocess.TimeoutExpired:
        messages.error(request, "PDF generation timed out.")
        return redirect('finance_dashboard')
    except FileNotFoundError:
        messages.error(request, "WeasyPrint executable not found.")
        return redirect('finance_dashboard')
    finally:
        for path in [html_path, pdf_path]:
            if os.path.exists(path):
                os.remove(path)