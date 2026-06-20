"""
URL configuration for backendapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from property.views import UserListCreateApiviews,UserUpdateDelateApiview,UserLogin,UserLogout,UserNewpasswordCreate,UserNewpasswordSendlink,UserPropertyFeature,UserPropertyFeatureUpdateDelete,UserFeautureValue,UserFeatureValueUpdateDelete,UserReviewUpdateDelete,UserReview,UserContactMessage,UserPropertyInquery,UserPropertyInqueryUpdate
from property.views import PropertyTypeView,PropertyStatusView,PropertyTypeUpdateDelete,PropertyStatusUpdateDelete,UserBusinessDetail,UserBusinessDetailUpdateDelete,UserBusinessLocationGetPost,UserBusinessLocation,UserPropertyImage,UserPropertyImageUpdateDelete,UserFavorite,UserFavoriteUpdateDelete,UserContactRequestUpdate,CreateAgentProfile,CreateAgentProfileUpdate
from property.views import LoginIntApi,CatcheLoginApi,CaptchaImageView
from property.services import property_search
from property.services import city_list
from property.paymentgetway.payment import create_order,verify_payment
from property.servicepage.ai_assistance import chat_bot

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/signup/",UserListCreateApiviews.as_view(),name='user-get-post'),
    path("api/signup/<int:pk>/",UserUpdateDelateApiview.as_view(),name='update'),
    path("api/login/",UserLogin.as_view(),name='login'),
    path("api/logout/",UserLogout.as_view(),name='logout'),
    path("api/upsl/",UserNewpasswordSendlink.as_view(),name='sendlinkpassword'),
    path("api/upu/",UserNewpasswordCreate.as_view(),name='newpassword'),
    path("api/type/",PropertyTypeView.as_view(),name='property-type'),
    path('api/type/<int:pk>/',PropertyTypeUpdateDelete.as_view(),name='property-ud'),
    path('api/status/',PropertyStatusView.as_view(),name='status'),
    path('api/status/<int:pk>/',PropertyStatusUpdateDelete.as_view(),name='status-ud'),
    path('api/business/',UserBusinessDetail.as_view(),name='buseness'),
    path('api/business/<int:pk>/',UserBusinessDetailUpdateDelete.as_view(),name='buseness-ud'),
    path('api/location/',UserBusinessLocationGetPost.as_view(),name='location'),
    path('api/locationid/<int:pk>/',UserBusinessLocation.as_view(),name='location-ud'),
    path('api/images/',UserPropertyImage.as_view(),name='image'),
    path('api/images/<int:pk>/',UserPropertyImageUpdateDelete.as_view(),name='image-ud'),
    path('api/feature',UserPropertyFeature.as_view(),name='feature'),
    path('api/feature/<int:pk>/',UserPropertyFeatureUpdateDelete.as_view(),name='feature-ud'),
    path('api/featurevalue/',UserFeautureValue.as_view(),name='featurevalue'),
    path('api/featurevalue/<int:pk>/',UserFeatureValueUpdateDelete.as_view(),name='featurevalue-ud'),
    path('api/review/',UserReview.as_view(),name='review'),
    path('api/review/<int:pk>/',UserReviewUpdateDelete.as_view(),name='review-ud'),
    path('api/favorite/',UserFavorite.as_view(),name='favorite'),
    path('api/favorite/<int:pk>/',UserFavoriteUpdateDelete.as_view(),name='favorite-ud'),
    path('api/contact/',UserContactMessage.as_view(),name='contact'),
    path('api/contact/<int:pk>/',UserContactRequestUpdate.as_view(),name='contact-ud'),
    path('api/inquery/',UserPropertyInquery.as_view(),name='inquery'),
    path('api/inquery/<int:pk>/',UserPropertyInqueryUpdate.as_view(),name='inquery-ud'), 
    path('api/agent/',CreateAgentProfile.as_view(),name='agent'),  
    path('api/agent/<int:pk>/',CreateAgentProfileUpdate.as_view(),name='agent-ud'), 
    path('api/lgi/',LoginIntApi.as_view(),name='lgi'),
    path('api/lgi/<str:captcha_key>/', CaptchaImageView.as_view(), name="captcha-image"),
    path('api/cla/',CatcheLoginApi.as_view(),name='cla'),
    path('api/search/', property_search,name='search'),
    path('api/search/city/', city_list,name='city'),
    path('api/payment/', create_order,name='order'),
    path('api/verify_payment/',verify_payment,name='verify_payment'),
    path('api/aibot/',chat_bot,name='aibot'),
]

if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)