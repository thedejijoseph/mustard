
from django.http import JsonResponse

def index(request):
    data = {
        "message": "Mustard API",
        "status": "success"
    }
    return JsonResponse(data)
