# 1Panel deployment notes for PDF Team Splitter

These notes explain how the Vue + FastAPI stack fits into a 1Panel workspace, how to wire it together with an Nginx proxy, and how to lock the UI behind basic auth.

## Architecture snapshot

- **Frontend service**: Node 20 + Vite single-page app that lives under `/src` and talks to `/api/pdf-team-split`. The built `dist` folder can be served by Vite Preview or any static server.
- **Backend service**: Python 3.12 FastAPI server in `server/`. It exposes `/api/pdf-team-split` for uploads, writes temporary files under `server/tmp`, and bundles the results into a ZIP.
- **Nginx proxy**: Routes `/api` requests to the backend and everything else to the frontend bundle. Adds the headroom needed to inject headers, limit body size, and flip on password protection.

Each service can be deployed separately in 1Panel, connected via the same project network.

## Frontend service (Node)

1. **Base image**: Pick a Node 20 image from the 1Panel catalog (or use `node:20` if you manage your own base). Ensure `NODE_ENV` defaults to `production`.
2. **Build command**: `npm ci && npm run build`. This primes `dist/` for serving.
3. **Run command**: `npm run preview -- --host 0.0.0.0 --port ${PORT:-4173}` so 1Panel’s ephemeral `PORT` variable drives the listener.
4. **Expose**: Mark the service as HTTP with port `4173` (or the value you use in `--port`).
5. **Environment**: No extra vars required. The frontend already talks to `/api`, so the proxy handles routing.

The frontend service simply emits static assets; the Nginx container forwards browser traffic to it.

## Backend service (FastAPI)

1. **Base image**: Use a Python 3.12 image in 1Panel so the `py` launcher is available.
2. **Install step**: `py -3.12 -m pip install -r server/requirements.txt`.
3. **Run command**: `py -3.12 -m uvicorn server.app:app --host 0.0.0.0 --port ${PORT:-8001}`.
4. **Storage**: The FastAPI code writes to `server/tmp`. Bind a persistent (or at least writeable) volume if you want to inspect uploads between restarts, otherwise the default ephemeral storage works.
5. **Environment**: No secrets are needed by default, but you can inject `LOG_LEVEL`, `UVICORN_WORKERS`, or `TMP_ROOT` overrides if your deployment demands it.

The backend service should be marked as HTTP and exposed on the same network as the frontend and proxy. The proxy uses its DNS name (e.g., `backend`) to forward API calls.

## Nginx proxy

Use a dedicated Nginx service to glue the frontend and backend. A minimal `nginx.conf` snippet:

```nginx
server {
  listen 80;
  server_name _;

location /api/ {
  proxy_pass http://backend:8001/api/;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_read_timeout 120s;
    client_max_body_size 200M;
  }

  location / {
    proxy_pass http://frontend:4173/;
    proxy_set_header Host $host;
    try_files $uri $uri/ /index.html;
  }
}
```

- Replace `frontend` and `backend` with the service names you configured in 1Panel.
- `client_max_body_size` must match or exceed the largest roster + PDF upload the UI will send.
- You can also use this proxy to enforce HTTPS (1Panel will terminate TLS in front of your HTTP services).

## Password protection

If the workspace should stay private, layer Basic Auth onto the Nginx proxy:

1. Generate an `htpasswd` file locally: `printf 'username:$(openssl passwd -apr1 password)\n' > /etc/nginx/.htpasswd`.
2. Mount that file into the Nginx container (e.g., `Config File` or `Static File` mount in 1Panel).
3. Wrap the `/` block with Basic Auth:

```nginx
location / {
  auth_basic "Private tools";
  auth_basic_user_file /etc/nginx/.htpasswd;
  proxy_pass http://frontend:4173/;
  ...
}
```

4. Optionally protect `/api` as well if you want server endpoints locked behind the same credentials.

1Panel also supports “Password protect workspace” toggles, but this gives you explicit control through Nginx so you can rotate credentials or reuse a company-wide auth store.
