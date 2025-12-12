from django.urls import path, include

urlpatterns = [
    path('login/', include(('login.urls', 'login'), namespace='login')),
    path('secretary/', include(('secretary.urls', 'secretary'), namespace='secretary')),

    
]