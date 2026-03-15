from django.urls import path
from . import views

urlpatterns = [
    # Shopper dashboard
    path('dashboard/', views.ShopperDashboardView.as_view(), name='shopper-dashboard'),
    
    # Available lists to bid on
    path('available-lists/', views.AvailableListsView.as_view(), name='available-lists'),
    path('lists/<int:pk>/', views.ListDetailForShopperView.as_view(), name='list-detail-shopper'),
    
    # Bid management
    path('', views.PlaceBidView.as_view(), name='place-bid'),
    path('my-bids/', views.MyBidsView.as_view(), name='my-bids'),
    path('lists/<int:pk>/bids/', views.ListBidsView.as_view(), name='list-bids'),
    path('won/', views.MyWonBidsView.as_view(), name='my-won-bids'),
    path('<int:pk>/', views.BidDetailView.as_view(), name='bid-detail'),
    path('<int:pk>/update/', views.UpdateBidView.as_view(), name='update-bid'),
    path('<int:pk>/withdraw/', views.WithdrawBidView.as_view(), name='withdraw-bid'),
    path('<int:pk>/history/', views.BidHistoryView.as_view(), name='bid-history'),
]