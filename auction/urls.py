from django.urls import path
from . import views

app_name = "auction"

urlpatterns = [
    path('', views.homePageView, name='homepage'),
    path('add-nft', views.addNft, name='add-nft'),
    path('sell-nft', views.sellNft, name='sell-nft'),
    path('account', views.account, name='account'),
    path('end-auction', views.endAuction, name='end-auction'),
    path('api/user-info/', views.userInfo, name='user-info'),
    path('api/fetch-txHash/', views.fetchTxHash, name='fetch-txHash'),
]