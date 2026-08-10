import os
import django
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macom_project.settings')
django.setup()

from dashboard.views import api_metrics
import traceback

request = RequestFactory().get('/api/metrics/')
try:
    response = api_metrics(request)
    print("STATUS:", response.status_code)
    print("CONTENT:", response.content.decode('utf-8'))
except Exception as e:
    print("ERROR:")
    traceback.print_exc()
