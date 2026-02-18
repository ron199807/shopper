from django.urls import path
from . import views

urlpatterns = [
    # Client endpoints
    path('', views.ClientShoppingListCreateView.as_view(), name='create-list'),
    path('my-lists/', views.ClientShoppingListView.as_view(), name='my-lists'),
    path('<int:pk>/', views.ClientShoppingListDetailView.as_view(), name='list-detail'),
    path('<int:pk>/bids/', views.ClientShoppingListBidsView.as_view(), name='list-bids'),
    path('<int:pk>/accept-bid/<int:bid_id>/', views.ClientAcceptBidView.as_view(), name='accept-bid'),
    path('<int:pk>/status/', views.ClientUpdateListStatusView.as_view(), name='update-status'),
    
    # Public endpoints
    path('open/', views.OpenShoppingListsView.as_view(), name='open-lists'),
    path('nearby/', views.NearbyShoppingListsView.as_view(), name='nearby-lists'),
]