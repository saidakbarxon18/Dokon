from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('inventory/', views.inventory, name='inventory'),
    path('pos/', views.pos, name='pos'),
    path('api/sell/', views.sell_api, name='sell_api'),
    path('debts/', views.debts, name='debts'),
    path('my-debts/', views.my_debts, name='my_debts'),
    path('archive/', views.archive, name='archive'),
]
