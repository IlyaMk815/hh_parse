import vacancies_methods as vm


def main():
    print('Выберите действие: \n1. Создать записи в БД\n2. Обновить записи в БД\n3. Удалить записи БД')
    action = int(input())

    if action == 1:
        vm.create_vacancies()

    elif action == 2:
        vm.vacancies_update()

    elif action == 3:
        vm.clear_database()

    else:
        print("Неверная команда")


if __name__ == '__main__':
    main()
