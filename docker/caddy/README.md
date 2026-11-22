# DA13 Public Proxy Setup

This directory contains the Caddy-based public ingress for the DA13 GPU validator API and dashboard.

## Required environment values

Create a local `.env` file alongside the compose file with:

```env
DA13_PUBLIC_HOST=validator.daxda.ai
CADDY_EMAIL=admin@yourdomain.com
```

## Launch

```bash
docker compose -f docker-compose.da13-public.yml up --build -d
```

## What this gives you

- HTTPS at `https://validator.daxda.ai`
- Reverse proxy to the internal DA13 service on port 8000
- Automatic TLS certificate issuance via Let’s Encrypt
- Secure browser access to the dashboard and API routes

## Notes

- Point your public DNS record to the machine hosting Docker.
- Ensure port 80 and 443 are open on your firewall / cloud load balancer.
- If you are behind NAT, expose the host on the public internet or terminate TLS at a cloud LB in front of this service.
