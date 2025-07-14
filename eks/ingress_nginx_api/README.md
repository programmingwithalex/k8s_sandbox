# ingress_nginx_api

- need separate one from `ingress_nginx_frontend`
  - must have path rewrites enabled so requests to `<alb_url>/app1` gets routed to `/` in the `app1` service

- `values.yaml`

```yaml
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: /$2
```
