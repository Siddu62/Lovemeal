from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('customers/', include('customers.urls')),
    path('chefs/', include('chefs.urls')),
    path('delivery/', include('delivery.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin panel title
admin.site.site_header = "Lovemeal Admin"
admin.site.site_title  = "Lovemeal Admin Panel"
admin.site.index_title = "Welcome to Lovemeal Admin"


