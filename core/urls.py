"""core URL Configuration

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
# swagger docs
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import TemplateView

# main
from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny

base_url = 'api/v1/'

urlpatterns = [
    path('admin/', admin.site.urls),
	path(base_url+'user/', include('user.urls')),
	# path(base_url, include('user.urls'))
	path(base_url+'auth/', include('authentication.urls'))
	# path(base_url, include('client.urls'))
	# path(base_url, include('business.urls'))

]


schema_view = get_schema_view(
    openapi.Info(
        title="BookMe API",
        default_version='v1',
        description="API for a Service Booking Application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="ainae06@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)
urlpatterns += [
    path(base_url+'docs/', schema_view.with_ui('swagger',
                                         cache_timeout=0), name='schema-swagger-ui'),
    path(base_url+'redoc/', schema_view.with_ui('redoc',
                                       cache_timeout=0), name='schema-redoc'),
   	# path('graphql/', csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True)))
]
