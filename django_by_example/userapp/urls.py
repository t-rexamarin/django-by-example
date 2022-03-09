from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


app_name = 'user'

urlpatterns = [
    path('login/', views.LoginUserView.as_view(), name='login'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
