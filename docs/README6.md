# Data Provider: CSV / Excel

Модуль авторизации и набор преднастроенных аналитических панелей для платформы ЭПОТОС BI.

Задание: **Студент 6 Пугачев Ярослав — «Управление пользователями + шаблоны дашбордов по направлениям»**.

---

## 1. Постановка задачи

Задание состоит из двух взаимосвязанных частей:  
Программная часть: разработка модуля управления пользователями, различающего 
роли Designer (создание и редактирование) и Viewer (только просмотр), с привязкой 
дашбордов к авторам.  
Аналитическая часть: выбор 3–4 направлений (отделов) компании ЭПОТОС, 
проектирование для них дашбордов, определение KPI и создание готовых 
JSON-шаблонов с тестовыми CSV-данными.  

## 2. Анализ предметной области

Разрабатываемая BI-система предназначена для компании ЭПОТОС, занимающейся 
производством противопожарного оборудования. Разным подразделениям (например, 
отделу продаж, финансовой службе, HR) требуются совершенно разные метрики и показатели.
Руководитель отдела продаж, как правило, использует дашборд для утреннего мониторинга 
выполнения плана продаж, выручки, среднего чека и конверсии из заявки в сделку.

## 3. Обзор аналогов

В промышленных BI-решениях управление доступом базируется на ролевой модели (RBAC). 
Платформы обычно предоставляют набор готовых шаблонов (Templates) для типовых бизнес-задач, 
чтобы пользователи не собирали дашборды с нуля. В рамках учебного проекта ЭПОТОС BI 
реализуется упрощенная, но рабочая версия этой механики.

## 4. Функциональные требования

- Простая регистрация или выбор роли при входе в систему без сложной криптографической защиты.  
- Строгое разделение прав доступа: пользователь с ролью Designer видит интерфейс создания дашборда, а Viewer — нет.  
- Автоматическая привязка созданного дашборда к автору.  
- Разработка 3–4 содержательных JSON-шаблонов дашбордов для выбранных отделов.  
- Подготовка тестовых CSV-наборов с реалистичными цифрами для каждого шаблона.

## 5. Архитектурное решение

Программная часть (управление пользователями) реализована на стеке Python + FastAPI.
Модуль интегрируется с API ядра платформы, за которое отвечает Студент 1.
Данные о пользователях хранятся в простой базе данных SQLite — в той же, что используется ядром.

## 6. Проектирование данных

**[Данные модуля хранятся в SQLite базе данных с данной схемой](docs/architecture.md)**<br/><br/>
Формат данных в JSON:
```json
{
  "schema_version": "1.0",
  "dashboard_id": "sales-overview",
  "title": "Обзор продаж",
  "layout": {
    "type": "grid",
    "columns": 12
  },
  "widgets": [
    {
      "widget_id": "w1",
      "type": "line_chart",
      "position": { "x": 0, "y": 0, "w": 6, "h": 4 },
      "config": {
        "x_field": "date",
        "y_field": "revenue",
        "title": "Выручка по дням"
      }
    }
  ],
  "datasets": [
    {
      "dataset_id": "sales_2026",
      "columns": [
        { "name": "date", "type": "date" },
        { "name": "revenue", "type": "number" }
      ],
      "rows": [
        ["2026-01-01", 120000],
        ["2026-01-02", 98000]
      ]
    }
  ]
}
```
Формат тестового датасета:
```json
{
  "schema_version": "1.0",
  "dashboard_id": "sales-department-template",
  "title": "Дашборд отдела продаж",
  "layout": { "type": "grid", "columns": 12 },
  "widgets": [
    {
      "widget_id": "w1",
      "type": "kpi_card",
      "position": { "x": 0, "y": 0, "w": 3, "h": 2 },
      "data_source": { "provider": "csv_provider", "dataset_id": "sales_test" },
      "config": { "value_field": "revenue", "label": "Выручка за месяц" }
    }
  ]
}
```

## 7. Описание интерфейсов

Модуль напрямую интегрируется в общую экосистему платформы. 
JSON-шаблоны считываются ядром платформы и передаются на фронтенд. 
Виджеты внутри шаблонов (линейные графики, KPI-карточки, таблицы) 
используют компоненты, разработанные Студентом 4.

## 8. Описание API

В модуль добавлены эндпоинты для проверки прав (пример):

- POST /login — упрощенная аутентификация и выдача роли.

- Middleware или зависимости (Depends) FastAPI для проверки роли (Designer/Viewer) при доступе к защищенным маршрутам API ядра.

## 9. Описание структуры проекта

docs/
└── analytics_research.md        # Сводный аналитический документ (профили, цели, KPI)

app/
├── templates/                       # Папка с JSON-шаблонами дашбордов
│   ├── it_ops_template.json         # Шаблон дашборда для IT-подразделения
│   ├── ceo_executive_template.json  # Шаблон стратегического дашборда для CEO
│   ├── pmo_portfolio_template.json  # Шаблон дашборда проектного офиса (PMO)
│   └── sales_department_template.json # Шаблон дашборда отдела продаж
└── data/                            # Папка с моковыми данными (CSV)
    ├── it_ops_metrics.csv           # Данные по метрикам IT-инфраструктуры
    ├── ceo_executive_summary.csv    # Финансовые показатели компании
    ├── pmo_portfolio_data.csv       # Данные по портфелю проектов и бюджетам
    └── sales_department_data.csv    # Табличные данные по продажам и сделкам

## 10. Инструкция по запуску

### Клонирование репозитория
```bash
git clone https://github.com/KoteikiPivo/techno_core_platform.git
cd techno_core_platform
```
### Установка зависимостей
```bash
make init
```
### Запуск
```bash
make run
```
### Тестирование
```bash
make test
```
### Очистка
```bash
make clean
```
API будет доступен по ссылке [127.0.0.1:8011](http://127.0.0.1:8011/), а документация по [127.0.0.1:8011/docs](http://127.0.0.1:8011/docs)


## 11. Результаты тестирования

tests/test_api.py::TestAuth::test_create_dashboard_with_designer PASSED
tests/test_api.py::TestAuth::test_create_dashboard_without_role PASSED
tests/test_api.py::TestAuth::test_create_dashboard_with_viewer PASSED
tests/test_api.py::TestAuth::test_update_dashboard_with_viewer PASSED
tests/test_api.py::TestAuth::test_delete_dashboard_with_viewer PASSED
tests/test_api.py::TestDashboardsCRUD::test_create_dashboard_success PASSED
tests/test_api.py::TestDashboardsCRUD::test_create_dashboard_duplicate PASSED
tests/test_api.py::TestDashboardsCRUD::test_create_dashboard_invalid_id PASSED
tests/test_api.py::TestDashboardsCRUD::test_get_dashboard_success PASSED
tests/test_api.py::TestDashboardsCRUD::test_get_dashboard_not_found PASSED
tests/test_api.py::TestDashboardsCRUD::test_get_all_dashboards PASSED
tests/test_api.py::TestDashboardsCRUD::test_update_dashboard_success PASSED
tests/test_api.py::TestDashboardsCRUD::test_update_dashboard_wrong_id PASSED
tests/test_api.py::TestDashboardsCRUD::test_delete_dashboard_success PASSED
tests/test_api.py::TestDashboardsCRUD::test_delete_dashboard_not_found PASSED
tests/test_api.py::TestMetadata::test_get_sources PASSED
tests/test_api.py::TestMetadata::test_get_widgets PASSED
tests/test_api.py::TestLogin::test_login_success PASSED

- Подтверждено, что роли реально разграничивают доступ: пользователь под ролью Viewer получает отказ в доступе при попытке создать дашборд.
- Интеграция шаблонов проверена совместно со студентами, отвечающими за ядро.

## 12. Выводы

Модуль успешно реализован. Базовая система ролей интегрирована с ядром FastAPI. 
Проведена аналитическая работа: определены конкретные KPI, подходящие под 
специфику производственной компании ЭПОТОС. Использование ИИ помогло на этапе 
исследования метрик для отделов.

## 13. Перспективы развития

- Добавление возможности делиться конкретным дашбордом по специальной ссылке с ограниченным доступом.
- Проработка механизмов автоматической подстановки реальных корпоративных баз данных на место тестовых CSV-файлов при внедрении платформы в ЭПОТОС.
- Расширение библиотеки шаблонов на 1–2 дополнительных направления сверх минимума.

---

## Технологии

Python 3.12, [pandas](https://pandas.pydata.org/docs/), [openpyxl](https://openpyxl.readthedocs.io/), [pytest](https://docs.pytest.org/)
