# academica_tcc/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', include('core.urls')), 
    
    path('', include(('upload.urls', 'upload'), namespace='upload')),
]
