from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home,name='home'),
    path('about/', views.about,name="about"),
    path('contact/', views.contact,name="contact"),
    path('category/<slug:val>', views.CategoryView.as_view(), name='category'),
    path('product-detail/<int:pk>', views.ProductDetail.as_view(), name='product-detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('address/', views.ProfileView.as_view(), name='address'),


    #login authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),


    path ('add-to-cart/', views.add_to_cart,name='add-to-cart'),
    path('cart/',views.show_cart, name='showcart'),
    path('checkout/', views.checkout.as_view(), name='checkout'),
    # path('paymentdone/',views.payment_done, name='paymentdone'),
    path('orders/', views.order, name='orders'),

    path('pluscart/', views.plus_cart, name='plus_cart'),
    path('minuscart/', views.minus_cart),
    path('removecart/', views.remove_cart),





    



    















    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)