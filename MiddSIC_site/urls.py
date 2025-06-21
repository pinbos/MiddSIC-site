from django.urls import path, include
from django.contrib.auth import views as auth_views
from web import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('investment/', views.investment, name='investment'),
    path('recruitment/', views.recruitment, name='recruitment'),
    path('contact/', views.contact, name='contact'),
    
    # New public URLs
    path('leadership/', views.leadership, name='leadership'),
    path('performance/', views.performance, name='performance'),
    
    # Admin URLs
    path('admin-dashboard/manage-portfolio/delete-holding/<str:ticker>/', views.delete_holding, name='delete_holding'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/team/', views.manage_team, name='manage_team'),
    path('admin-dashboard/team/add/', views.add_team_member, name='add_team_member'),
    path('admin-dashboard/team/delete/<int:member_id>/', views.delete_team_member, name='delete_team_member'),
    path('admin-dashboard/portfolio/', views.manage_portfolio, name='manage_portfolio'),
    path('admin-dashboard/portfolio/add/', views.add_transaction, name='add_transaction'),
    path('admin-dashboard/get-stock-info/<str:ticker>/', views.get_stock_info, name='get_stock_info'),
    
    # Microsoft auth
    path('microsoft/', include('microsoft_auth.urls', namespace='microsoft_auth')),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    # Add the new API endpoint
    path('api/upload_portfolio/', views.api_upload_portfolio, name='api_upload_portfolio'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)