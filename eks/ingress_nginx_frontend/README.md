# ingress_nginx_frontend

- need separate one from `ingress_nginx_frontend`
  - no path rewrites so can serve static files

- `values.yaml`

```yaml
  annotations:
    kubernetes.io/ingress.class: nginx
```
