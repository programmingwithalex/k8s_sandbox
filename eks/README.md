# alex_example

- two separate nginx instances for `api` and `frontend` because `api` needs URL rewrites while the frontend can't have them

- `servicemonitor.yaml` necessary for Prometheus to be able to pull metrics from the service

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# * allows Prometheus to scrape metrics from this FastAPI app
# * automatically exposes metrics at /metrics endpoint that Prometheus can scrape
Instrumentator().instrument(app).expose(app)
```

- separate namespaces for applications and monitoring
  - `alex-sandbox` - apps
  - `monitoring` - grafana, prometheus, etc.
