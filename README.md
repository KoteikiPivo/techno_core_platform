Документация API: [koteikipivo.ru/techno/docs](https://koteikipivo.ru/techno/docs)<br/>
Также, для тестирования без установки последняя версия API развернута по ссылке https://koteikipivo.ru/techno
## Примеры запросов
### Создать дашборд
```bash
curl -X POST http://127.0.0.1:8011/api/v1/dashboards \
  -H "Content-Type: application/json" \
  -H "User-id: test-designer" \
  -H "Role: Designer" \
  -d '{
    "dashboard_id": "sales-overview",
    "title": "Обзор продаж",
    "layout": {"type": "grid", "columns": 12},
    "widgets": [
      {
        "widget_id": "w1",
        "type": "line_chart",
        "position": {"x": 0, "y": 0, "w": 6, "h": 4},
        "config": {"x_field": "date", "y_field": "revenue", "title": "Выручка по дням"}
      }
    ],
    "datasets": [
      {
        "dataset_id": "sales_2026",
        "columns": [{"name": "date", "type": "date"}, {"name": "revenue", "type": "number"}],
        "rows": [["2026-01-01", 120000], ["2026-01-02", 98000]]
      }
    ]
  }'
  ```
### Получить все дашборды
```bash
curl http://127.0.0.1:8011/api/v1/dashboards
```
### Получить дашборд по ID
```bash
curl http://127.0.0.1:8011/api/v1/dashboards/sales-overview
```
### Обновить дашборд
```bash
curl -X PUT http://127.0.0.1:8011/api/v1/dashboards/sales-overview \
  -H "Content-Type: application/json" \
  -d '{
    "dashboard_id": "sales-overview",
    "title": "Обзор продаж (обновлено)",
    "layout": {"type": "grid", "columns": 12},
    "widgets": []
  }'
```
### Удалить дашборд
```bash
curl -X DELETE http://127.0.0.1:8011/api/v1/dashboards/sales-overview
```
## Запуск локально

```bash
make init
make run

# Очистка 
make clean
```
API будет доступен по ссылке [127.0.0.1:8011](http://127.0.0.1:8011/), а документация по [127.0.0.1:8011/docs](http://127.0.0.1:8011/docs)
