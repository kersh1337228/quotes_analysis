"""quotes_analysis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from quotes_analysis import settings


urlpatterns = [
    # Default urls
    path('admin/', admin.site.urls),
    # Frameworks urls
    path('api/', include('rest_framework.urls')),
    # Applications urls
    path('analysis/', include('analysis.urls')),
    path('quotes/', include('quotes.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('strategy/', include('strategy.urls')),
    path('log/', include('log.urls')),
]


if settings.DEBUG:  # Appending urls on local machine
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
