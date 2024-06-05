from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Post

@csrf_exempt
def graphql_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Your GraphQL handling logic here
            return JsonResponse({'data': data})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)