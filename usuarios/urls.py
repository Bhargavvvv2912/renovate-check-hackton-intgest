from django.urls import path

from usuarios.views import (
    conta_bloqueada_view,
    login_view,
    logout_view,
    perfil_view,
    registro_view,
    admin_dashboard_view,
    admin_toggle_usuario_view,
)

app_name = 'usuarios'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro_view, name='registro'),
    path('perfil/', perfil_view, name='perfil'),
    path('conta-bloqueada/', conta_bloqueada_view, name='conta_bloqueada'),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path(
        'admin-toggle-usuario/<int:usuario_id>/',
        admin_toggle_usuario_view,
        name='admin_toggle_usuario',
    ),
]
