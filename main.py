import vacancies_methods as vm


def wrng_answ():
    print('Неверная команда')


def main():
    print('\nВведите цифру команды: \n1 - Обновить записи в БД\n2 - Удалить записи БД\n3 - Выйти')

    try:
        action = int(input())
        if action == 1:
            vm.vacancies_update()
            main()
        elif action == 2:
            print('Вы действительно хотите удалить записи?\nЭто действие сотрёт все записи и очистит индекс! (y/n):')
            answ = input()
            if answ in ['y', 'н', 'yes', 'да']:
                vm.clear_database()
                main()
            elif answ in ['n', 'no', 'т', 'нет']:
                print('Удаление записей отменено.')
                main()
            else:
                wrng_answ()
                main()
        elif action == 3:
            return print('Выполнение завершено')
        else:
            wrng_answ()
            main()
    except ValueError:
        wrng_answ()
        main()


if __name__ == '__main__':
    main()
