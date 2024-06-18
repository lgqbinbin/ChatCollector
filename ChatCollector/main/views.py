from django.contrib.sites import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import User
import json
from django.db import connection
from django.http import JsonResponse
import pymysql
import requests
from .models import TimeRecord  # 添加导入语句
from datetime import datetime
from django.views.decorators.http import require_POST
from django.utils import timezone


def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            if username == 'admin' and password == '123456':
                return render(request, 'manager.html')


            user = User.objects.get(username=username)
            if user.password == password:
                with connection.cursor() as cursor:
                    # 获取所有表名
                    cursor.execute("SHOW TABLES")
                    all_tables = cursor.fetchall()
                    print(all_tables)

                table_names = []
                for table in all_tables:
                    table_name = table[0]
                    try:
                        with connection.cursor() as cursor:
                            # 获取当前表的所有列名
                            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                            columns = cursor.fetchall()
                            # 检查每个列名是否以 "id" 结尾
                            for column in columns:
                                column_name = column[0]
                                if column_name.endswith('id'):
                                    # 检查表中是否包含特定 id
                                    cursor.execute(f"SELECT 1 FROM {table_name} WHERE {column_name} = %s LIMIT 1",
                                                   [user.id])
                                    if cursor.fetchone():
                                        table_names.append(table_name)
                                        break  # 如果在当前表中找到匹配的列名，不再继续检查其他列
                    except Exception as e:
                        # 忽略没有 id 列的表
                        pass

                context = {
                    'user_id': user.id,
                    'username': username,
                    'password': password,
                    'profile': user.profile,
                    'table_names': table_names
                }
                return render(request, 'user.html', context)

            else:
                return HttpResponse("Invalid login details.")
        except User.DoesNotExist:
            return HttpResponse("Invalid login details.")
    return render(request, 'login.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')


#返回所选表中具有特定用户 ID 的所有条目的数据。
def get_table_data(request):
    table_name = request.GET.get('table')
    user_id = request.GET.get('user_id')  # 获取前端传递的 user_id 值
    print("Received user_id:", user_id)  # 打印接收到的 user_id 值

    if not table_name:
        return JsonResponse({'error': 'No table name provided'}, status=400)


    with connection.cursor() as cursor:
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = cursor.fetchall()

        # binbin
        column_names = [column[0] for column in columns]

        first_column = column_names[0] if columns else None

        if first_column and first_column.endswith('id'):
            # 构建查询条件，只针对第一列进行比较
            query = f"SELECT * FROM {table_name} WHERE {first_column} = %s"

            # 执行查询
            cursor.execute(query, [user_id])
            table_data = cursor.fetchall()
        else:
            table_data = []

    print("#################################")
    print(table_name)
    print(user_id)
    print(table_data)

    data = {
        'columns': column_names,
        'data': table_data
    }

    return JsonResponse(data, safe=False)

@csrf_exempt
def update_table_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table_name = data.get('table')
            rows = data.get('data')

            if not table_name or not rows:
                return JsonResponse({'error': 'Invalid data'}, status=400)

            with connection.cursor() as cursor:
                for row in rows:
                    columns = ', '.join([f"{key} = %s" for key in row.keys() if key != 'id'])
                    values = [row[key] for key in row.keys() if key != 'id']
                    query = f"UPDATE {table_name} SET {columns} WHERE id = %s"
                    cursor.execute(query, values + [row['id']])  # Assuming 'id' is the primary key
            print(query)
            print("更新成功")
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_time_record(request, table_name):
    try:
        time_record = TimeRecord.objects.get(table_name=table_name)
        start_time = time_record.start_time
        end_time = time_record.end_time

        return JsonResponse({
            'table_name': table_name,
            'start_time': start_time,
            'end_time': end_time,
        })
    except TimeRecord.DoesNotExist:
        return JsonResponse({
            'error': 'Time record not found for the selected table.'
        })
#时间查询
def check_time_range(request, table_name):
    current_time = timezone.now()

    print("Table Name:", table_name)
    print("Current Time:", current_time)
    try:
        time_record = TimeRecord.objects.get(table_name=table_name)
        start_time = time_record.start_time
        end_time = time_record.end_time
        print("Start Time:", start_time)
        print("End Time:", end_time)
        if start_time <= current_time <= end_time:
            return JsonResponse({'allowed': True})
        else:
            return JsonResponse({'allowed': False, 'message': 'You are not allowed to update data at this time.'})
    except TimeRecord.DoesNotExist:
        return JsonResponse({'allowed': False, 'message': 'Time record not found for the selected table.'})





def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        profile = request.POST['profile']

        if password1 == password2:
            if not User.objects.filter(username=username).exists():
                user = User(username=username, password=password1, profile=profile)
                user.save()
                return HttpResponse(f"User {username} registered successfully!")
            else:
                return HttpResponse("Username already exists.")
        else:
            return HttpResponse("Passwords do not match.")
    return render(request, 'register.html')

def view_users(request):
    users = User.objects.all()

    # 查询所有表名，排除 main_user
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall() if row[0] != 'main_user']

    context = {
        'users': users,
        'tables': tables,
    }
    return render(request, 'view_users.html', context)

def get_table_data2(request, table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    data = {
        'columns': columns,
        'rows': rows,
    }
    return JsonResponse(data)
#建表逻辑函数
def manage(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sql = data.get('sql')



        if sql:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(sql)
                    return JsonResponse({'success': True})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method or missing SQL'})


def collect_form(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table_name = data.get('tableName')  # 获取前端传递过来的表名参数
            table = data.get('table')
            #logger.info(f'Received table data: {table}')  # 使用日志记录器记录消息

            start_time = data.get('start_time')  # 获取前端传递过来的开始时间
            end_time = data.get('end_time')  # 获取前端传递过来的结束时间

            print(f'Received table name: {table_name}')  # 打印收到的表名
            print(f'Received table data: {table}')  # 打印收到的表数据


            users = User.objects.all()
            sql_statements = []

            for user in users:
                user_id = user.id
                profile = user.profile
                #name = user.username  # 假设您想使用username作为name

                profile_data = {
                    "profile": f"|user_id|profile|\n|{user_id}|Now it's 2024.{profile}|",
                    "table": table
                }

                print(f'Profile data being sent: {profile_data}')  # 打印 profile_data 的内容

                response = requests.post("http://222.199.216.192:2333/chat_clt", json=profile_data)

                print('Response status code:', response.status_code)
                print('Response headers:', response.headers)
                print('Response text:', response.text)

                if response.status_code == 200:
                    result = response.json()
                    print(result)
                    if result.get('response'):
                        sql = result.get('response')

                        # 使用表名参数替换 SQL 语句中的固定表名
                        sql = sql.replace('TABLE', table_name)
                        sql = sql.replace('\n', '')  # 去掉换行符
                        print(sql)

                        sql_statements.append(sql)
                    else:
                        return JsonResponse({'success': False, 'error': result.get('error')})
                else:
                    return JsonResponse({'success': False, 'error': 'Failed to get SQL from external service'})

            # 执行生成的SQL语句
            with connection.cursor() as cursor:
                try:
                    for sql in sql_statements:
                        cursor.execute(sql)

                    # 保存时间记录到 TimeRecord 表中
                    time_record = TimeRecord(table_name=table_name, start_time=start_time, end_time=end_time)
                    time_record.save()

                    return JsonResponse({'success': True})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})

            return JsonResponse({'success': True})
        except Exception as e:
            # logger.error(f'Error occurred: {e}')  # 使用日志记录器记录错误消息
            print(f'Error occurred: {e}')  # 使用 print 输出错误信息
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
@require_POST
def start_publish(request):
    data = json.loads(request.body)
    table_name = data.get('table_name')  # 获取表名
    type_value = data.get('type_value')  # 获取用户指定的 type 值
    publish_content = data.get('publish_content')  # 获取发布内容的值

    print("type_value = ", type_value)
    print("table_name = ", table_name)
    print("publish_content = ", publish_content)

    if not table_name or type_value is None:
        return JsonResponse({'error': 'Invalid data'}, status=400)

    try:
        # 删除表中 type 值不等于指定值的所有记录
        with connection.cursor() as cursor:
            delete_query = f"DELETE FROM {table_name} WHERE {type_value} != %s"
            cursor.execute(delete_query, [publish_content])
            return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
