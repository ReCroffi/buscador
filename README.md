# Buscador e Monitorador de Precos

Aplicacao FastAPI para busca exata de produtos em multiplas lojas, ranking de ofertas, historico de precos e alertas por Telegram/email.

## Recursos

- Busca assíncrona em Amazon, Mercado Livre, KaBuM e conectores preparados para Pichau, Terabyte, Magazine Luiza, Casas Bahia, Americanas, AliExpress, Shopee, Carrefour e Fast Shop.
- Matching estrito com normalizacao, fuzzy score, capacidades, versoes e modelos/SKU.
- Persistencia PostgreSQL com Alembic.
- Cache Redis, Celery Beat/Worker e APScheduler opcional.
- Frontend HTMX + Tailwind com cards responsivos e criacao de alertas.
- Notificacoes Telegram Bot API e SMTP.
- Logs estruturados, retry exponencial, limite de concorrencia e proxy rotation preparado.

## Como rodar

1. Copie `.env.example` para `.env`.
2. Ajuste tokens de Telegram/SMTP quando quiser notificacoes reais.
3. Suba tudo:

```bash
docker compose up --build
```

4. Abra `http://localhost:8000`.

## API

Buscar produto:

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"iPhone 16 Pro Max 512GB Titanio Natural","strict":true}'
```

Criar alerta:

```bash
curl -X POST http://localhost:8000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{"query":"RTX 5070 TI ASUS TUF","target_price":5200,"email":"voce@example.com"}'
```

Historico:

```bash
curl http://localhost:8000/api/history/iPhone%2016%20Pro%20Max%20512GB
```

## Arquitetura

- `app/api`: rotas REST e HTMX.
- `app/models`: entidades SQLAlchemy.
- `app/schemas`: contratos Pydantic.
- `app/services`: casos de uso, matching, ranking, alertas.
- `app/scrapers`: scrapers por loja com contrato comum.
- `app/tasks`: Celery e scheduler.
- `app/notifications`: Telegram e SMTP.
- `app/templates`: dashboard e emails.

## Roadmap

- APIs oficiais/afiliados por loja quando disponiveis.
- Persistir snapshots HTML de falha para auditoria.
- Calculo de frete por CEP em conectores especificos.
- Painel completo de historico com Chart.js consumindo `/api/history`.
- Anti-bloqueio com pool de proxies, fingerprints e circuit breaker por loja.
- Deduplicacao semantica entre lojas por GTIN/EAN/SKU.
- Regras por categoria para matching ainda mais rigoroso.

## Observacao importante

Scraping de lojas muda com frequencia e pode estar sujeito a termos de uso. A estrutura esta pronta para producao, mas cada conector deve ser mantido continuamente e, quando possivel, substituido por API oficial.

