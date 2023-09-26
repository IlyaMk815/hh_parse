import psycopg2
import requests
import json


def get_pages():
    with open('config.json', 'r') as conf:
        js_conf = json.load(conf)
        params = js_conf['params']
        url = js_conf['api_url']

    req = requests.get(url['url'], params)
    data = req.json()
    req.close()
    return data


def elem_check(data, field=None, key=None) -> str:
    if data[field] and key is not None:
        return data[field][key]
    elif data[field] is None:
        return 'NO DATA'
    else:
        return data[field]


def get_db_configure():
    print('\nLoading configuration...')
    with open('config.json', 'r') as conf_bd:
        bd_conf_data = json.load(conf_bd)['database']
    print('\tDone.')
    return bd_conf_data


def get_vacancies():
    bd_conf = get_db_configure()
    data_js = get_pages()

    print('Trying connect to database...')
    try:
        conn = psycopg2.connect(database=f'{bd_conf["database_name"]}', user=f'{bd_conf["username"]}',
                                host=f'{"localhost"}', port=f'{"5432"}', password=f'{"12345"}')
        print('Connection established.\nRecording data...')

        curr = conn.cursor()
        for page in range(0, 5):
            for i in data_js['items']:
                req = requests.get(i['url'])
                data = req.json()
                req.close()

                curr.execute(f'''insert into {bd_conf['table_name']}(vacancy_id, name, salary, currency, url, employer,
                experience) values('{data['id']}', '{data['name']}', '{elem_check(data, 'salary', 'from')}',
                '{elem_check(data, 'salary', 'currency')}', '{data['alternate_url']}', 
                '{elem_check(data, 'employer', 'name')}', '{elem_check(data, 'experience', 'name')}');''')
                conn.commit()
        print('\tRecording done!')

    except Exception as conn_dead:
        print('Error: ', conn_dead, '\nSomething went wrong!')
    finally:
        curr.close()
        conn.close()
        print('Disconnected out of database.')


def clear_database():
    bd_conf = get_db_configure()
    print('Trying connect to database...')
    try:
        print('\tDone.')
        conn = psycopg2.connect(database=f'{bd_conf["database_name"]}', user=f'{bd_conf["username"]}',
                                host=f'{"localhost"}', port=f'{"5432"}', password=f'{"12345"}')
        curr = conn.cursor()

        print('Connection established.\nDeleting data...')

        curr.execute(f'''delete from {bd_conf['table_name']};''')
        conn.commit()
        curr.execute(f'''alter sequence {bd_conf['table_name']}_id_seq restart with 1;''')
        conn.commit()
        print('\tDone.')

    except Exception as conn_dead:
        print('Error: ', conn_dead, '\nSomething went wrong!')

    finally:
        curr.close()
        conn.close()
        print('Disconnected out of database.')


def main():
    get_vacancies()
    clear_database()


if __name__ == '__main__':
    main()
