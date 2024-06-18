from django.urls import path
from . import views
from .views import get_time_record, start_publish  # 导入视图函数
from .views import view_users, get_table_data2  # 确保导入 get_table_data 视图
urlpatterns = [
    path('', views.index, name='index'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('get_table_data/', views.get_table_data, name='get_table_data'),#获取表的URL配置
    path('update_table_data/', views.update_table_data, name='update_table_data'),  # 新增的路径 lgq
    path('register/', views.register_view, name='register'),

    path('view_users/', views.view_users, name='view_users'),
    path('get_table_data/<str:table_name>/', get_table_data2, name='get_table_data2'),
    path('manage/', views.manage, name='manage'),
    path('collect_form/', views.collect_form, name='collect_form'),
    path('start_publish/', start_publish, name='start_publish'),

    path('get_time_record/<str:table_name>/', get_time_record, name='get_time_record'),
    # 新增的路径用于检查时间范围是否允许更新数据
    path('check_time_range/<str:table_name>/', views.check_time_range, name='check_time_range'),
]
