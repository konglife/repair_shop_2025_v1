# inventory/views.py
from django.shortcuts import get_object_or_404
from .models import Product, Supplier, Stock, Purchase, Category
from .forms import SupplierForm, PurchaseForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def index(request):
    return JsonResponse({"message": "Inventory API endpoint"})

@login_required
def product_list(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    # Prefetch stocks เพื่อดึง current_stock
    products = Product.objects.prefetch_related(
        Prefetch('stocks', queryset=Stock.objects.all(), to_attr='all_stocks')
    )

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    paginator = Paginator(products, 10)  # แบ่งหน้า
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    product_list = []
    for product in page_obj:
        product_list.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price) if product.price else 0,
            'category': product.category.name if product.category else None,
            'current_stock': product.current_stock if hasattr(product, 'current_stock') else 0
        })

    categories = list(Category.objects.values('id', 'name'))
    
    return JsonResponse({
        'products': product_list,
        'categories': categories,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number
    })

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    stock = product.stock if hasattr(product, 'stock') else None
    
    stock_data = None
    if stock:
        stock_data = {
            'quantity': stock.quantity,
            'last_updated': stock.last_updated.isoformat() if stock.last_updated else None
        }
    
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': float(product.price) if product.price else 0,
        'category': product.category.name if product.category else None,
        'stock': stock_data
    })

@login_required
@csrf_exempt
def add_supplier(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = SupplierForm(data)
        if form.is_valid():
            supplier = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Supplier added successfully',
                'supplier_id': supplier.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    return JsonResponse({"message": "Please use POST method"}, status=405)

@login_required
def purchase_list(request):
    purchases = Purchase.objects.all()
    purchase_list = []
    
    for purchase in purchases:
        purchase_list.append({
            'id': purchase.id,
            'product': purchase.product.name,
            'supplier': purchase.supplier.name,
            'quantity': purchase.quantity,
            'price': float(purchase.price) if purchase.price else 0,
            'date': purchase.date.isoformat() if purchase.date else None
        })
    
    return JsonResponse({'purchases': purchase_list})

@login_required
@csrf_exempt
def add_purchase(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = PurchaseForm(data)
        if form.is_valid():
            purchase = form.save(commit=False)

            # TODO: ใช้ average_cost จาก Stock หรือ logic ใหม่ แทน ProductSupplier
            purchase.price = 0

            purchase.save()
            return JsonResponse({
                'success': True,
                'message': 'Purchase added successfully',
                'purchase_id': purchase.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    return JsonResponse({"message": "Please use POST method"}, status=405)