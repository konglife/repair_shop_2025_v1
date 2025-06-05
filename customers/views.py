# customers/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Customer
from .forms import CustomerForm
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

# ฟังก์ชันเข้าสู่ระบบ
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "message": "Login successful"})
        else:
            return JsonResponse({"success": False, "message": "Invalid username or password"}, status=400)
    return JsonResponse({"message": "Please use POST method for login"}, status=405)

# ฟังก์ชันออกจากระบบ
def user_logout(request):
    logout(request)
    return JsonResponse({"success": True, "message": "Logout successful"})

# ฟังก์ชันแสดงรายชื่อลูกค้าทั้งหมด
@login_required
def customer_list(request):
    query = request.GET.get('q')
    customers = Customer.objects.all().order_by('id')  # เรียงลำดับตาม ID

    if query:
        customers = customers.filter(name__icontains=query)  # กรองตามชื่อ (ไม่สนใจตัวพิมพ์)

    paginator = Paginator(customers, 10)  # แบ่งหน้า แสดง 10 รายการต่อหน้า
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    customer_list = []
    for customer in page_obj:
        customer_list.append({
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'address': customer.address
        })
    
    return JsonResponse({
        'customers': customer_list,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number
    })

# ฟังก์ชันแสดงรายละเอียดลูกค้าแต่ละคน
@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return JsonResponse({
        'id': customer.id,
        'name': customer.name,
        'phone': customer.phone,
        'email': customer.email,
        'address': customer.address
    })

# ฟังก์ชันเพิ่มลูกค้าใหม่
@login_required
@csrf_exempt
def add_customer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = CustomerForm(data)
        if form.is_valid():
            customer = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Customer added successfully',
                'customer_id': customer.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    return JsonResponse({"message": "Please use POST method"}, status=405)

# ฟังก์ชันแก้ไขข้อมูลลูกค้า
@login_required
@csrf_exempt
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        data = json.loads(request.body)
        form = CustomerForm(data, instance=customer)
        if form.is_valid():
            customer = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Customer updated successfully',
                'customer_id': customer.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    return JsonResponse({"message": "Please use POST method"}, status=405)

# ฟังก์ชันลบลูกค้า
@login_required
@csrf_exempt
def delete_customer(request, pk):
    if request.method != 'POST':
        return JsonResponse({'message': 'Please use POST method'}, status=405)
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return JsonResponse({
        'success': True,
        'message': 'Customer deleted successfully'
    })
