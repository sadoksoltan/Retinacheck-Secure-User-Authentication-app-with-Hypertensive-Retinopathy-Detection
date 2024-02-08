from django.urls import path
from unicodedata import name
from app import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import gettext_lazy as _


urlpatterns = [
    path('',views.home,name='home'),
    path('register.html',views.register,name='register'),
    path('login.html',views.login_view,name='login_view'),
    path('logout_view',views.logout_view,name='logout_view'),
    path('ret.html',views.ret,name='ret'), 
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('predictImage',views.predictImage,name='predictImage'),
    path('forget-password/', views.ForgetPassword , name="forget_password"),
    path('change-password/<token>/' ,views.ChangePassword , name="change_password")
    # path('reset_password/', auth_views.PasswordResetView.as_view(template_name="app/password_reset.html",email_template_name = 'app/password_reset_email.html'), name="password_reset"),
    # path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="app/password_reset_sent.html"), name="password_reset_done"),
    # path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(template_name="app/password_reset_form.html",form_class = CustomSetPasswordForm), name="password_reset_confirm"),
    # path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="app/password_reset_done.html"), name="password_reset_complete")

    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)