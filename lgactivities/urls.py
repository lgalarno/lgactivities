"""lgactivities URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import TemplateView
from .sitemaps import StaticViewSitemap

from .views import home

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),  # TemplateView.as_view(template_name="index.html"), name="main"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),),
    # TODO about page
    path('about/', TemplateView.as_view(template_name="about.html"), name="about"),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('accounts/', include('allauth.urls')),
    path('getactivities/', include('getactivities.urls', namespace="getactivities")),
    path('activities/', include('activities.urls', namespace="activities")),
    path('profile/', include('profiles.urls', namespace="profiles")),
    path('calendar/', include('calendarapp.urls', namespace="calendarapp")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
