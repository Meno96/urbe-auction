from django.urls import path
from . import views

app_name = "auction"

urlpatterns = [
    path('', views.homePageView, name='homepage'),
    path('add-nft', views.addNft, name='add-nft'),
    path('end-auction', views.endAuction, name='end-auction'),
]