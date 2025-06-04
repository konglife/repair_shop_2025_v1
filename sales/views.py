# sales/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return JsonResponse({"message": "Sales API endpoint"})
