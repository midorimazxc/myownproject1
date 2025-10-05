from django.urls import path, include
from . import views

app_name = 'store'
urlpatterns = [
    path('', views.guitar_list, name = 'guitar_list'),
    path('guitar/<int:pk>/', views.guitar_detail, name='guitar_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:guitar_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:guitar_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:guitar_id>/<str:action>/', views.update_quantity, name='update_quantity'),
    path('check/', views.check, name='check'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

