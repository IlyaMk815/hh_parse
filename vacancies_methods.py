import psycopg2
import requests
import json
from tqdm import tqdm


# Получение конфигурации. По умолчанию получает конфиг для БД.
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


# Установка подключения к БД
def db_connect(bd_conf):
    conn = psycopg2.connect(database=f'{bd_conf["database_name"]}', user=f'{bd_conf["username"]}',
                            host=f'{"localhost"}', port=f'{"5432"}', password=f'{"12345"}')
    return conn


# Функция вывода исключений
def exception_print(conn_dead):
    print('\nSomething went wrong!', '\nError: ', conn_dead)


# Удаление всех данных из БД и сброс первичного ключа
def clear_database():
    bd_conf = get_configure()

    print('Trying connect to database...')
    try:
        conn = db_connect(bd_conf)
        print('\tDone.\nDeleting data...')
        curr = conn.cursor()

        curr.execute(f'''delete from {bd_conf['table_name']};''')
        conn.commit()
        curr.execute(f'''alter sequence {bd_conf['table_name']}_id_seq restart with 1;''')
        conn.commit()
        print('\tDone.')

    except Exception as conn_dead:
        exception_print(conn_dead)
    finally:
        curr.close()
        conn.close()
        print('Disconnected out of database.')


# Обновление списка вакансий в БД
def vacancies_update():
    print('Collecting items...')
    bd_conf = get_configure()
    pages_data = get_pages()
    db_id = []
    vac_id = []

    for page in pages_data:
        for i in page['items']:
            vac_id.append(i['id'])

    print('Trying connect to database...')
    try:
        conn = db_connect(bd_conf)
        print('Connection established.')
        curr = conn.cursor()

        # Записи из БД выбираются с конца, их количество зависит от количества записей вакансий из запроса
        # это сделано для того, чтобы не нагружать базу данных лишними запросами к ней
        # к примеру если в БД будет 1 млн. записей, а в запросе 2000
        curr.execute(f'''select vacancy_id from {bd_conf['table_name']} 
                     order by id desc limit({len(vac_id)});''')
        result = curr.fetchall()

        for i in result:
            db_id.append(str(i[0]))

        new_ids = set(db_id) ^ set(vac_id)

        if new_ids:
            total_count = 0
            for item in tqdm(new_ids, desc='Recording data: '):
                for page in pages_data:
                    for i in page['items']:
                        if item == i['id']:
                            curr.execute(f'''insert into {bd_conf['table_name']}
                            (vacancy_id, name, salary, currency, url, employer, experience, date) values('{i['id']}',
                            '{i['name']}', '{elem_check(i, 'salary', 'from')}','{elem_check(i, 'salary', 'currency')}',
                            '{i['alternate_url']}', '{elem_check(i, 'employer', 'name')}',
                            '{elem_check(i, 'experience', 'name')}', '{i['published_at']}');''')
                            conn.commit()
                            total_count += 1

            print(f'Added: {total_count}')
        else:
            print('Nothing to update!')

    except Exception as conn_dead:
        exception_print(conn_dead)
    finally:
        curr.close()
        conn.close()
        print('Disconnected out of database.')
