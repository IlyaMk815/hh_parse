import psycopg2
import requests
import json
import time


# Получаем конфигурацию. По умолчанию получает конфиг для БД.
def get_configure(conf_for='database'):
    with open('config.json', 'r') as conf_bd:
        bd_conf_data = json.load(conf_bd)[conf_for]
    return bd_conf_data


# Функция получения страницы поиска.
def get_page(page="0"):
    with open('config.json', 'r') as conf:
        js_conf = json.load(conf)
        params = js_conf['params']
        params['page'] = page
        url = js_conf['api_url']
    req = requests.get(url['url'], params)
    data = req.json()
    req.close()
    return data


# Формирование единого массива для всех существующих страниц по запросу.
def get_pages():
    page_conf = int(get_configure(conf_for='api_url')['pages'])
    items_data = []
    for page in range(0, page_conf):
        data_json = get_page(page=f"{page}")
        if len(data_json['items']) <= 1:
            break
        items_data.append(data_json)
    return items_data


# Проверка данных для избегания ошибки при обращении к ключу несуществующей записи(None)
def elem_check(data, field=None, key=None) -> str:
    if data[field] and key is not None:
        return data[field][key]
    elif data[field] is None:
        return 'NO DATA'
    else:
        return data[field]


# Формирование первичного списка вакансий
def create_vacancies():
    print('\nLoading configuration...')
    bd_conf = get_configure()
    pages_data = get_pages()
    print('\tDone.')

    print('Trying connect to database...')
    try:
        conn = psycopg2.connect(database=f'{bd_conf["database_name"]}', user=f'{bd_conf["username"]}',
                                host=f'{"localhost"}', port=f'{"5432"}', password=f'{"12345"}')
        print('Connection established.\nRecording data...')

        curr = conn.cursor()

        for page in pages_data:
            for i in page['items']:
                curr.execute(f'''insert into {bd_conf['table_name']}(vacancy_id, name, salary, currency, url, employer,
                experience) values('{i['id']}', '{i['name']}', '{elem_check(i, 'salary', 'from')}',
                '{elem_check(i, 'salary', 'currency')}', '{i['alternate_url']}', 
                '{elem_check(i, 'employer', 'name')}', '{elem_check(i, 'experience', 'name')}');''')
                conn.commit()

        print('\tRecording done!')

    except Exception as conn_dead:
        print('\nSomething went wrong!', '\nError: ', conn_dead)
    finally:
        curr.close()
        conn.close()
        print('Disconnected out of database.')


# Удаление всех данных из БД и сброс первичного ключа
def clear_database():
    bd_conf = get_configure()

    print('Trying connect to database...')
    try:
        conn = psycopg2.connect(database=f'{bd_conf["database_name"]}', user=f'{bd_conf["username"]}',
                                host=f'{"localhost"}', port=f'{"5432"}', password=f'{"12345"}')
        print('\tDone.\nDeleting data...')
        curr = conn.cursor()

        curr.execute(f'''delete from {bd_conf['table_name']};''')
        conn.commit()
        curr.execute(f'''alter sequence {bd_conf['table_name']}_id_seq restart with 1;''')
        conn.commit()
        print('\tDone.')

    except Exception as conn_dead:
        print('\nSomething went wrong!', '\nError: ', conn_dead)

    finally:
        curr.close()
        conn.close()
        print('Disconnected out of database.')


# Обновление списка вакансий в БД
# Количество обновляемых вакансий задаётся параметром 'limit_for_update' в файле конфигурации
def vacancies_update():
    bd_conf = get_configure()
    page_conf = int(get_configure(conf_for='api_url')['pages'])
    db_id = []
    new_vac_id = []
    data_arr = []

    print('Trying connect to database...')
    try:
        conn = psycopg2.connect(database=f'{bd_conf["database_name"]}', user=f'{bd_conf["username"]}',
                                host=f'{"localhost"}', port=f'{"5432"}', password=f'{"12345"}')
        print('Connection established.\nRecording data...')
        curr = conn.cursor()

        curr.execute(f'''select vacancy_id from {bd_conf['table_name']} 
                     order by id desc limit({bd_conf['limit_for_update']});''')
        result = curr.fetchall()

        for i in result:
            db_id.append(str(i[0]))

        for page in range(0, page_conf):
            data_js = get_page(page=f"{page}")
            if len(data_js['items']) <= 1:
                break
            for i in data_js['items']:
                data_arr.append(i)
                new_vac_id.append(i['id'])

        new_ids = set(db_id) ^ set(new_vac_id)

        # if new_ids:
        #     total_count = 0
        #     for item in new_ids:
        #         for j in new_vac_id:
        #             if item == j:
        #
        #                 curr.execute(f'''insert into {bd_conf['table_name']}(vacancy_id, name, salary, currency, url,
        #                 employer, experience) values('{j['id']}', '{j['name']}', '{elem_check(j, 'salary', 'from')}',
        #                 '{elem_check(j, 'salary', 'currency')}', '{j['alternate_url']}',
        #                 '{elem_check(j, 'employer', 'name')}', '{elem_check(j, 'experience', 'name')}');''')
        #                 conn.commit()
        #                 total_count += 1
        #     print(f'Added: {total_count}')

        if new_ids:
            total_count = 0
            for item in new_ids:
                for page in range(0, page_conf):
                    data_js = get_page(page=f"{page}")
                    if len(data_js['items']) <= 1:
                        break
                    for i in data_js['items']:
                        if item == i['id']:
                            curr.execute(f'''insert into {bd_conf['table_name']}
                            (vacancy_id, name, salary, currency, url, employer, experience) values('{i['id']}', 
                            '{i['name']}', '{elem_check(i, 'salary', 'from')}','{elem_check(i, 'salary', 'currency')}', 
                            '{i['alternate_url']}', '{elem_check(i, 'employer', 'name')}', 
                            '{elem_check(i, 'experience', 'name')}');''')
                            conn.commit()
                            total_count += 1

            print(f'Added: {total_count}')
        else:
            print('Nothing to update!')

    except Exception as conn_dead:
        print('\nSomething went wrong!', '\nError: ', conn_dead)
    finally:
        curr.close()
        conn.close()
        print('Disconnected out of database.')
