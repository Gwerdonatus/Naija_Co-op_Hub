# logistics/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
import requests
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LogisticCompany
from .forms import LogisticCompanyForm

def order_tracking_view(request):
    # Render the order tracking page
    return render(request, 'logistics/order_tracking.html')

def fetch_tracking_data(request, order_id):
    if request.method == 'GET':
        external_api_url = 'https://api.logisticspartner.com/track'  # Replace with actual API endpoint
        headers = {
            'Authorization': f'Bearer {os.environ.get("LOGISTICS_API_KEY")}',
            'Content-Type': 'application/json'
        }
        params = {'order_id': order_id}
        try:
            response = requests.get(external_api_url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return JsonResponse(data)
            else:
                return JsonResponse({'error': 'Failed to fetch tracking data'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return HttpResponseBadRequest('Invalid request method.')


def logistic_company_apply(request):
    if request.method == 'POST':
        form = LogisticCompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('logistic_company_apply')
        else:
            messages.error(request, 'There was an error with your submission. Please check the details and try again.')
    else:
        form = LogisticCompanyForm()
    
    return render(request, 'logistics/company_apply.html', {'form': form})



def list_logistic_companies(request):
    companies = LogisticCompany.objects.filter(status='approved')
    return render(request, 'logistics/companies_list.html', {'companies': companies})

