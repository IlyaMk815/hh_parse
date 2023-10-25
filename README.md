# hh_parse

<h3> Описание </h3>
<p>Это небольшой демонстрационный проект, использующий API сервиса HeadHunter для сбора вакансий по заданным параметрам и взаимодействия с БД PostgreSQL.</p>

<p>Хоть проект написан под конкретный сервис, его возможно использовать при работе с сервисами с похожей на хедхантер структурой за счёт использования конфигурационного файла.</p>

<p>Выборка записей происходит по запросу к API, адрес которого указывается в конфигурационном файле в разделе "api_url", так же в этом разделе указывается количество страниц для обработки.
<br>Параметры запроса указаны в разделе "params" и должны соответствовать требованиям документации к API (в данном случае headhunter'a).
<br>Параметры подключения к базе указываются в разделе "database" конф. файла.</p>
Функционал проекта:
<ul>
  <li>Создание записей в БД;</li>
  <li>Обновление записей;</li>
  <li>Удаление записей с обнулением индекса первичного ключа;</li>
</ul>

Управление проектом реализовано через консольное меню.


![hh_vac_screen](https://github.com/IlyaMk815/hh_parse/assets/92967219/2890cbbb-80e8-4a48-a4b3-e32e03b60b9a)

Пример сформированных записей в бд:
![hh_vac_screen1](https://github.com/IlyaMk815/hh_parse/assets/92967219/8beca376-06b9-4699-8fbc-c6b8690c9e1b)