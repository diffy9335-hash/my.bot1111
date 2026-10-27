# Football Arena — Telegram Mini App (virtual coins only)

MVP with live football schedule/results via football-data.org, synthetic game-only 1X2 odds, parlays, virtual balances, daily reward, transaction ledger, and secure Telegram auth. **No money, prizes, withdrawals, purchases, Stars, or currency exchange.**

## Quick start (Python 3.11+)

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # Windows: copy .env.example .env
```

Set `BOT_TOKEN` from @BotFather, `PUBLIC_URL` to your HTTPS deployment, `FOOTBALL_API_KEY` from https://www.football-data.org/client/register (optional for demo); edit `.env`.

**Terminal 1:** `python run.py`  (HTTP server + periodic football synchronization)
**Terminal 2:** `python -m app.bot` (Telegram bot, polling)

Register the HTTPS Mini App URL with @BotFather if you also want an app-menu entry. `/start` provides a Web App button. For a local test in browser, temporarily set `DEV_AUTH=true` **only on a private local server** and visit `http://localhost:8000/?dev=123`; **never enable DEV_AUTH on public deployments**.

In demo mode, fictitious future fixtures are provided for UI and betting tests, **not real games**. The demo will NOT fake final results or grant wins. Once configured with football-data.org, the scheduler pulls real kickoff/status/full-time scores every `SYNC_MINUTES` (15 minutes by default) and settles qualifying 1X2 slips automatically. Free-tier availability and API limits vary. Market odds are NOT supplied by football-data.org: **the 1X2 prices in this implementation are fixed synthetic gameplay odds**, not real betting odds. The full implementation of bookmaker odds and their rights/licensing is separate work.

## Safety and operations
- Telegram `initData` server-side HMAC+freshness check; never trust Telegram `initDataUnsafe`.
- Account balances/settlement calculated server-side with SQLite transactions; no deposits, gifts, refunds for money, or peer-to-peer transfers.
- `FINISHED` with numeric full-time scores is needed to settle. Postponed/cancelled legs are voided at 1.0 for payout. All-other-void tickets refund stake. **Operational assumption:** cancellation is final when API reports this state; adapt to your contest rules if rescheduled matches should wait.
- The demo is an MVP, not production-hardened. Deploy behind HTTPS reverse proxy, disable DEV_AUTH, restrict CORS, add abuse prevention, backups, monitoring, PostgreSQL for multiple workers, structured observability, wagering cutoff buffers, rules/privacy docs, and jurisdiction/age reviews before public launch.
- One API service instance runs the synchronization scheduler. Do not run multiple workers without a distributed scheduler/lock.
- Odds are stored at placement and not overwritten during match sync. Check the data source's permission for your intended usage.
- `ADMIN_TELEGRAM_IDS` comma-separated numeric IDs grant `/api/admin/sync` privilege.

## Structure
- `app/main.py`: API and authentication
- `app/core.py`: database, atomic bets, settlements, ledger
- `app/sync.py`: provider sync and scheduler
- `app/bot.py`: Telegram bot
- `static/`: Mini App UI
- `tests/`: basic settlement/auth tests

## Version 0.2 additions
- Virtual additional picks per game: over/under 2.5 goals and both teams to score (yes/no), supported in single bets and parlays. Fixed synthetic odds: 1.92 on goals totals, 1.88 on BTTS.
- Telegram notification queue: once a ticket settles, the Telegram bot attempts to notify the player. Start `python -m app.bot` together with the API to deliver notifications; if user blocked the bot, delivery can fail/retry.
- Admin API: `GET /api/admin/overview` and `POST /api/admin/matches/{match_id}/cancel`, authorized by `ADMIN_TELEGRAM_IDS`. Cancelling a non-finished game voids its legs and settles affected eligible tickets.
- This is an evolving prototype, not yet a deployed, fully production-ready gambling/compliance platform. No real-money features.


## Version 0.3 — redesigned Mini App and admin dashboard
- Redesigned responsive dark mobile UI, bottom tabs, enhanced match and betting cards, admin tab visible to authorized users only.
- Admin dashboard: overview, last 50 players, ledger audit entries, manual match cancel and sync, carefully logged virtual balance corrections.
- Every balance correction is an atomic ledger transaction, with required operator ID and reason. Admin endpoints verify the user's Telegram signature and check `ADMIN_TELEGRAM_IDS`.
- Docker Compose starts the API and bot with one shared persistent SQLite volume. Start using `docker compose up -d --build` after configuring `.env`. Open port 8000 only on loopback and put a TLS reverse proxy (Caddy/Nginx) in front. `PUBLIC_URL` must be a real HTTPS URL.
- `pytest -q` runs the backend tests. Do not enable `DEV_AUTH=true` on public servers. Database remains SQLite; for higher traffic upgrade to PostgreSQL and add robust monitoring and rate limiting before a public launch.
- Admin testing: set your numeric Telegram ID in `ADMIN_TELEGRAM_IDS`, open Mini App in Telegram, then choose **Админ**.

## Version 0.4 — match discovery and coupon experience
- League filter chips on the matches page. A dedicated match detail view shows all supported 1X2, total 2.5 and both-teams-to-score markets. No unlicensed match statistics are presented.
- New editable coupon screen: remove selections, enter a virtual stake, inspect combined odds and potential payout before sending to the server. Selection cap remains 8 unique matches.
- Match odds and virtual potential payouts are illustrative only. Server still authoritatively validates all selections and recalculates locked odds.
- This is UI functionality, not evidence that live football feeds or public deployment are configured.

## Версия 0.5 — кэшаут без отмены ставок

Обычной отмены уже принятой ставки нет. На странице «История ставок» для одиночной ставки во время матча можно запросить предложение на кэшаут. Экспрессы не имеют кэшаута и рассчитываются по окончании событий. Сервер рассчитывает стоимость приблизительно по модели Пуассона исходя из текущего счёта и времени до конца основного времени с удержанием 12% от модельной выплаты. По мере снижения вероятности выигрыша уменьшается и сумма предложения. Это игровые коэффициенты, а не официальные котировки букмекеров.

В целях предотвращения злоупотреблений предложение доступно только во время игры (2–84-я минуты), при наличии текущего счёта из API, обновлённого не более 3 минут назад. При изменении котировки запрос подтверждения будет отклонён, потребуется получить новую. Все расчёты выполняются транзакционно, повторное начисление исключено. Следует учитывать, что сведения football-data.org не являются гарантированным live-фидом низкой задержки; в продакшене потребуется быстрый провайдер live-данных, а при отсутствии его кэшаут будет недоступен. `SYNC_MINUTES=2` служит ориентиром и должен соответствовать ограничениям API-тарифа. Бот, сайт и API должны работать в едином доверенном окружении. Никогда не включайте DEV_AUTH в публичной среде.

## Версия 0.6 — Live-центр

Добавлен API `GET /api/live`, вкладка Live и автоматическое обновление вкладки каждые 20 секунд. Сервер пишет историю **изменений счёта между снимками** провайдера в таблицу `match_events`. Это не детальная поминутная статистика: если API пропустил несколько голов, появится одно событие изменения счёта. Минута на интерфейсе **приблизительная**, вычисленная по UTC-времени начала, без учёта остановок и дополнительных таймов. Состояние свежести определяется по `updated_at` (не старше 180 секунд), поэтому прежние меры безопасности кэшаута сохранены. Для точных минут, карточек, авторов голов и котировок нужен другой лицензированный событийный API. Отображение в Mini App проверено синтаксически, но не тестировалось внутри Telegram на устройстве.

## Версия 0.7 — защита от повторов и устаревших статусов

- Для `POST /api/slips` добавлено необязательное поле `request_key` (8–100 символов). Mini App создаёт UUID и повторяет тот же ключ при повторной отправке после сетевой ошибки. Сервер хранит ключ в уникальном индексе на пользователя: повтор возвращает исходную ставку без списания монет. Попытка использовать тот же ключ с другими параметрами отклоняется.
- Новые ставки закрываются за 5 минут до времени начала матча по серверным часам, без возможности отмены после принятия.
- Синхронизация игнорирует переход `FINISHED` обратно в другой статус, неполные финальные снимки и live-снимки без счёта. Это временная защита от неполных ответов API; она не заменяет профессиональный live-фид и сверку исправленных результатов.
- Кэшаут по-прежнему **только для одиночных ставок**, только с актуальным live-счётом и без гарантии доступности. Экспрессы нельзя закрывать досрочно.
- Для публичного запуска необходимы проверка корректности источника, многоинстансовая блокировка синхронизации, rate limiting, мониторинг и HTTPS. Реальные live-данные не тестировались без API-ключа.

## Версия 0.8 — мониторинг, резервирование и HTTPS

- Служебная таблица `sync_runs` сохраняет 500 последних попыток автоматического обновления: начало, окончание, режим, количество обновлённых и рассчитанных матчей, краткую ошибку. Для администратора добавлен `GET /api/admin/operations`; вход — только через валидированную подпись Telegram и `ADMIN_TELEGRAM_IDS`. `stale=true`, если последняя успешная синхронизация старше трёх интервалов (но не меньше 5 минут). Это мониторинг внутри приложения, **не внешняя система оповещения**.
- Отдельный контейнер `backup` делает проверенную SQLite резервную копию через `sqlite3.Connection.backup()`, пригодную при включённом WAL. Каждые `BACKUP_HOURS` часов (по умолчанию 24), сохраняет последние `BACKUP_KEEP` копий (по умолчанию 14) в отдельном Docker volume `football_backups`. Копии остаются на том же VPS — для защиты от потери сервера их необходимо выгружать во внешнее хранилище с шифрованием. Для ручной копии: `docker compose exec backup python -m app.operations --once`.
- Для HTTPS добавлен Caddy reverse proxy (профиль `production`). Укажите реальный `DOMAIN` и `PUBLIC_URL=https://<ваш-домен>` в `.env`, настройте DNS A/AAAA на IP сервера и откройте входящие TCP 80/443 и UDP 443 (для HTTP/3). Далее `docker compose --profile production up -d --build`. API по-прежнему слушает только `127.0.0.1:8000`, а внешне открывается через TLS.
- Для локального теста без Caddy: `docker compose up -d --build` (порт 8000 только на localhost).
- В публичной среде установите `DEV_AUTH=false`, сильную защиту VPS и реальные `BOT_TOKEN`, `FOOTBALL_API_KEY`. Не храните `.env` в публичном репозитории; не отправляйте токен в чат. `DEMO_MODE=false` для реальных игр.

### Восстановление базы после аварии

1. Остановите API, бота и сервис копирования: `docker compose stop api bot backup`.
2. Скопируйте нужный файл из `football_backups` **в отдельное безопасное место**. Проверьте целостность `PRAGMA integrity_check` и актуальность даты копии.
3. Замените `/data/football.sqlite3` в томе `football_data` сохранённым файлом при остановленных процессах и удалите только старые файлы `football.sqlite3-wal` и `football.sqlite3-shm` **после полной остановки** (если они остались). Рекомендуется перед этим сделать копию текущего тома.
4. Запустите `docker compose up -d` и проверьте `/api/health`, страницу администрирования и последние ставки. Восстановление удаляет изменения после момента создания копии.

**Ограничения:** тесты запускаются локально на SQLite; реальная конфигурация Docker/Caddy, live API и Telegram-интерфейс должны быть проверены на выделенном тестовом VPS до публичного запуска. Отдельно необходимы rate limiting, отказоустойчивый провайдер и правовая/возрастная проверка. Виртуальные монеты не покупаются, не продаются и не выводятся.


### Профиль игрока (v0.9)
В нижнем меню доступна вкладка «Профиль». Endpoint `GET /api/profile` требует проверенную Telegram-авторизацию и возвращает только собственные данные игрока: имя, баланс, статистику завершённых ставок и 12 последних записей журнала операций. Возвраты и кэшауты не включаются в знаменатель процента выигрышей.

## v1.0 — уровни, XP, достижения и задания

* В профиле показаны XP, текущий уровень и прогресс до следующего уровня.
* Исторический XP выводится из совершённых ставок (20 XP за ставку, до 100), рассчитанных купонов (15 XP, до 100) и выигрышных купонов (25 XP, до 100). Размер ставки не влияет на XP.
* Ежедневные задания по UTC: открыть профиль и забрать награду (+15 XP), получить ежедневный бонус (+20 XP), сделать один прогноз (+25 XP). Награды — **только XP**; повторное получение блокирует уникальный ключ в БД.
* Достижения (без денежных/монетных призов): первый прогноз, пять прогнозов, три расчёта, первая победа и первый экспресс.
* API: `GET /api/progression` и `POST /api/quests/{quest_id}/claim`. Требуется Telegram авторизация.
* Это виртуальная игра: XP и монеты не имеют денежной ценности, продажи, вывода или призового обмена нет.
* Для установки поверх существующей версии сохраняйте SQLite-базу; таблица `quest_claims` создаётся автоматически.


## Реферальная система v1.1

Укажи `BOT_USERNAME` (имя бота без @) в `.env`. В разделе **Друзья** появится ссылка вида `https://t.me/USERNAME?start=ref_12345`. Впервые открывший бота по этой ссылке привязывается к пригласившему. Уже зарегистрированных игроков привязать нельзя. Самоприглашение, повторные привязки и присвоение другого реферера запрещены.

Подтверждение: приглашённый возвращается в бот или Mini App **на следующий UTC-день или позже**. Тогда обоим зачисляется XP (+50 пригласившему, +25 другу) ровно один раз. Монеты за приглашения не начисляются; деньги, призы и ставки не участвуют. Событие обрабатывается автоматически при посещении, без фоновой задачи. В Mini App показываются приглашения и их статусы.

Для запуска на сервере нужен действующий токен, HTTPS URL и уже настроенный Mini App. Реферальная ссылка формата `?start=` открывает бота, который показывает кнопку Mini App.

## v1.2 — Общий чат Mini App

Добавлена вкладка **Чат** с общей лентой сообщений. Клиент запрашивает новые
сообщения каждые 3,5 секунды (HTTP polling, без отдельного WebSocket-сервиса).
Пользователь может открыть публичную карточку другого игрока по имени:
отображаются имя, число ставок, побед и поражений; баланс, ID Telegram и
история начислений не публикуются. Общий чат не связан с денежными ставками.

API: `GET /api/chat/messages?after=0`, `POST /api/chat/messages`,
`POST /api/chat/messages/{id}/report`, `GET /api/players/{id}/public`.
Администратор (`ADMIN_TELEGRAM_IDS`): `GET /api/admin/chat/reports`,
`DELETE /api/admin/chat/messages/{id}`,
`POST /api/admin/chat/players/{id}/mute` с телом `{"minutes":60}`.
В админке появилась загрузка жалоб, удаление и мут на 60 минут.

Для отправки требуется валидная Telegram Mini App подпись (режим `DEV_AUTH`
можно использовать **только локально**). Ограничения: 350 символов,
минимум 5 секунд между сообщениями, максимум 50 сообщений в час; хранится
до 10 тысяч последних записей. Функция жалобы сама по себе не скрывает
сообщение, требуется модерация. Автоматического фильтра токсичности пока нет.
Перед открытием доступа реальным пользователям рекомендуется добавить
правила сообщества, политику хранения сообщений и проверку модерации.

Проверки: `PYTHONPATH=. pytest -q`, `node --check static/app.js`.

## v1.3 — сезоны и подписки

- Сезон длится **90 суток**, начиная с `SEASON_ANCHOR_UTC` (по умолчанию `2026-10-26T00:00:00+00:00`). Следующий сезон начинается автоматически, старые результаты остаются в истории ставок.
- Сезонные очки: **+3 за выигранный купон, +1 за кэшаут, 0 за проигрыш/возврат**. Очки не зависят от суммы ставки, не являются валютой, вывод невозможен. Купон учитывается в сезоне его создания после определения исхода. Экспресс считается одним купоном.
- `GET /api/seasons/current`: первые 50 игроков, место авторизованного пользователя в общем списке (даже вне топа), даты и правила сезона.
- `POST /api/players/{id}/follow`, `DELETE /api/players/{id}/follow`, `GET /api/players/{id}/subscription`, `GET /api/subscriptions`: подписки без чатов и уведомлений. Самоподписка запрещена, повторная подписка идемпотентна.
- Публичный профиль по-прежнему не раскрывает баланс, историю операций или Telegram ID. Веб-интерфейс показывает публичные имена, подписчиков и сезонную позицию.
- Новая таблица `follows` создаётся при запуске приложения автоматически. Существующие данные сохраняются.

Проверка: `python -m pytest -q` и `node --check static/app.js`.

## v1.4 — эксклюзивный значок чемпиона
- Золотой значок `✦` рядом с ником **только у победителя топ-1 завершённого 90-дневного сезона**. Значок сохраняется навсегда и отображается в чате, рейтинге, собственном и публичном профиле. В публичном профиле показано число выигранных сезонов.
- При равенстве очков побеждает игрок с большим числом побед, затем рассчитанных купонов, затем меньшим внутренним ID. Для пустых сезонов (нет положительных очков) чемпион не назначается.
- Список чемпионов фиксируется в таблице `season_champions` и не меняется задним числом. Текущий незавершённый сезон наград не даёт.
- Новые таблицы автоматически создаются при запуске сервера. Важно: финализация прошлых сезонов предполагает, что результаты за сезон уже полностью обработаны; перед включением в публичный проект надо дождаться расчёта всех матчей последнего дня.

## v1.5 — Season & Community Update

**Сезон:** `/api/seasons/current` возвращает число оставшихся дней, вчерашнее место и изменение позиции. Фоновое обслуживание записывает дневной снимок ранга, фиксирует завершённых чемпионов и отправляет уведомления. Первый снимок для дня делается при первом запуске обслуживания, а не строго в полночь; изменение позиции за сутки появляется только если вчера существовал снимок.

**Лента прогнозов:** вкладка «Лента», два режима («Все» / «Подписки»), публикация выбранного исхода на предстоящий матч с комментарием (до 280 символов), одна публикация на матч от автора, задержка 30 секунд, реакции, жалобы и переход в публичный профиль. Нельзя публиковать прогнозы после закрытия приёма за 5 минут до начала. Нет переводов монет, XP или сезонных очков за публикации или реакции. Администратор может просматривать жалобы и скрывать публикации через API.

**Уведомления Mini App:** вкладка «События», новые подписчики, исход рассчитанного купона, старт и последний день сезона, подтверждённый титул чемпиона. Информация внутри Mini App; это не отдельная push-система. Уведомления создаются идемпотентно, прочитанность хранится у пользователя. Купоны синхронизируются с историей ограниченным окном последних 500 рассчитанных при каждом цикле; старые записи остаются в исходной истории ставок.

**Аудит рейтинга:** журнал флагов при необычно большом числе купонов (150+ за сезон), строго для ручной проверки без автоматических наказаний. В админке добавлены просмотр флагов и принудительное сохранение снимка. Данные рейтинга не зависят от количества монет; по-прежнему +3/+1/0 за статус купона. Для боевого запуска требуются доработки антифрода, ежедневная проверка результатов и надёжный учёт завершения сезона.

API: `GET /api/community/feed?mode=all|following`, `POST /api/community/posts`, `POST /api/community/posts/{id}/like`, `POST /api/community/posts/{id}/report`, `GET /api/notifications`, `POST /api/notifications/{id}/read`, админские `GET /api/admin/community/reports`, `DELETE /api/admin/community/posts/{id}`, `GET /api/admin/seasons/audit`, `POST /api/admin/seasons/snapshot`.

Новые таблицы создаются автоматически при старте сервера. Для существующей базы данных не удаляйте SQLite-файл при обновлении. Нужны ключ футбольного API, работающий сервер и HTTPS Mini App; публичный деплой не выполнялся. Тесты: `python -m pytest -q`, `node --check static/app.js`.


## v1.6 — Таблица истории баланса в профиле

В профиле появилась таблица с суммами «Получено / Потрачено / Итог» за сегодня, за всё время и отдельно по дням (7, 30, 90). Источник — личный журнал `ledger`, серверный API `GET /api/profile/balance-history?days=30` требует Telegram-авторизации. День определяется по UTC. Стартовый баланс не учитывается как доход; сумма исторических изменений включает все записи журнала, в том числе виртуальные бонусы и админские корректировки.

## v1.7 — График баланса

В личном профиле история монет содержит адаптивный SVG-график **остатка виртуальных монет на конец каждого дня**, вместе с таблицей доходов/расходов. Выбор 7/30/90 дней обновляет и график, и таблицу через авторизованный API `GET /api/profile/balance-history`. График учитывает дни без операций и строит баланс относительно реального текущего остатка; стартовый остаток периода вычисляется вычитанием чистого изменения за выбранное окно. Даты группируются по UTC. Без внешних JS-библиотек и сторонних сервисов.


## v1.8 — Pre-Release / локальная проверка Windows

- Добавлен доступный из нижней навигации раздел «Помощь» с правилами виртуальных ставок, кэшаута, экспрессов, рейтинга, чата и обращений к поддержке. Сторонние денежные транзакции отсутствуют.
- `run.py` по умолчанию слушает только `127.0.0.1`; если `DEV_AUTH=true`, он отказывается слушать внешний адрес, даже если настроен `HOST=0.0.0.0`.
- Для **локального теста интерфейса без Telegram** на Windows можно дважды щёлкнуть `START_WINDOWS.bat`. Требуется Python 3.11+ и интернет для установки зависимостей. Откроется `http://127.0.0.1:8000/?dev=123`. Это **тестовый пользователь, не Telegram-авторизация**. Не размещайте такой сервис в интернете.
- Для настоящего Telegram Mini App выключите `DEV_AUTH`, укажите `BOT_TOKEN` и `PUBLIC_URL` с HTTPS, запустите сервер и `python -m app.bot` раздельно. Запуск Telegram-бота и публичного HTTPS пока не подтверждён.
- Перед открытием теста на VPS обязательно выполнить ревизию безопасности, нагрузочное тестирование, проверку SQLite при конкурентных запросах и полную live-сверку результатов. Это не подтверждённый продакшен-релиз.
