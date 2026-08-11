# MCSC Portal - Hostinger Docker Deployment Guide

This guide provides step-by-step instructions for dockerizing and deploying the **MCSC Django Portal** on **Hostinger** (Hostinger VPS or Hostinger Docker Container Hosting).

---

## 🌟 Key Features of the Docker Setup

1. **Dynamic Port Binding**: The application reads the execution port directly from the `PORT` variable in `.env` (defaulting to `8000` if not set).
2. **Automated Initialization**: The container entrypoint automatically executes `collectstatic` and database `migrate` before starting Gunicorn.
3. **Production Security**: Includes CSRF trusted origin configuration, security headers, and reverse-proxy compatibility.
4. **Volume Persistence**: Persistent Docker volumes for media uploads (`/app/media`) and collected static files (`/app/staticfiles`).

---

## 📁 Docker File Architecture

- **`Dockerfile`**: Builds a lean `python:3.11-slim` container with required C libraries (`libpq`, `libjpeg`, `zlib`).
- **`entrypoint.sh`**: Shell script executed on container start; parses `.env` for `PORT`, runs migrations, collects static assets, and launches Gunicorn bound to `0.0.0.0:${PORT}`.
- **`docker-compose.yml`**: Defines the `web` service, passes environment variables from `.env`, maps dynamic ports, and handles volume persistence.
- **`.dockerignore`**: Excludes temporary files, virtual environments, local sqlite databases, and git logs from image builds.

---

## 🛠️ Step 1: Prepare Environment File (`.env`)

On your Hostinger server (or in your project root), create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and ensure the following essential variables are configured:

```ini
# Server & Port Configuration
PORT=8000
DEBUG=False
SECRET_KEY=generate-a-strong-random-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,123.45.67.89

# Security & Trusted Origins (Required for POST requests through domain/SSL)
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,http://123.45.67.89:8000

# Database URL (Supabase PostgreSQL / Managed Database)
DATABASE_URL=postgres://user:password@db.supabase.co:5432/postgres

# Google OAuth2 Credentials
GOOGLE_OAUTH2_KEY=your-google-client-id.apps.googleusercontent.com
GOOGLE_OAUTH2_SECRET=your-google-client-secret

# Supabase S3 Media Storage (Optional)
USE_SUPABASE_STORAGE=True
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
SUPABASE_STORAGE_BUCKET_NAME=mcsc-media
```

> **Note on Port Configuration:**
> Change `PORT=8000` to any port required by your Hostinger environment (e.g. `PORT=3000`, `PORT=8080`). Both `docker-compose.yml` and `entrypoint.sh` will automatically read and bind to this port.

---

## 🚀 Step 2: Deploy on Hostinger VPS (Recommended)

### Option A: Deployment using Docker Compose

1. **SSH into Hostinger VPS**:
   ```bash
   ssh root@YOUR_HOSTINGER_VPS_IP
   ```

2. **Install Docker & Docker Compose** (if not already installed):
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose-v2
   sudo systemctl enable --now docker
   ```

3. **Upload / Clone Project to Server**:
   ```bash
   git clone https://github.com/your-org/mcsc-portal.git /var/www/mcsc
   cd /var/www/mcsc
   ```

4. **Create `.env` File**:
   ```bash
   nano .env
   # Paste your production environment variables (including PORT=8000)
   ```

5. **Build and Start Container**:
   ```bash
   docker compose up -d --build
   ```

6. **Verify Deployment**:
   ```bash
   docker compose logs -f
   ```
   You should see:
   ```text
   Starting MCSC Django Application...
   Configured Port: 8000
   Collecting static files...
   Applying database migrations...
   Launching Gunicorn server on 0.0.0.0:8000...
   ```

---

## 🌐 Step 3: Configure Nginx & SSL (HTTPS) on Hostinger VPS

To serve your application on port 80/443 with a custom domain and HTTPS SSL certificate:

1. **Install Nginx & Certbot**:
   ```bash
   sudo apt install -y nginx certbot python3-certbot-nginx
   ```

2. **Create Nginx Site Configuration**:
   ```bash
   sudo nano /etc/nginx/sites-available/mcsc
   ```

   Paste the following configuration (replace `yourdomain.com` and `8000` with your `PORT`):

   ```nginx
   server {
       server_name yourdomain.com www.yourdomain.com;

       client_max_body_size 50M;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable Site & Test Nginx**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/mcsc /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. **Obtain Free SSL Certificate via Let's Encrypt**:
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

---

## ☁️ Step 4: Hostinger Docker Container Hosting (Alternative)

If using Hostinger's managed Container Hosting service:

1. Connect your repository to Hostinger.
2. Under **Environment Variables**, set all `.env` keys (including `PORT`).
3. Set **Port Expose** to match `PORT` (e.g. `8000`).
4. Set Build Command / Dockerfile to `./Dockerfile`.
5. Trigger Deployment.

---

## 🔑 Useful Post-Deployment Commands

### Create a Django Admin Superuser
```bash
docker compose exec web python manage.py createsuperuser
```

### View Live Container Logs
```bash
docker compose logs -f web
```

### Restart Container
```bash
docker compose restart web
```

### Run Manual Migration
```bash
docker compose exec web python manage.py migrate
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|---|---|
| **CSRF Verification Failed** | Ensure `CSRF_TRUSTED_ORIGINS` in `.env` includes `https://yourdomain.com` |
| **Port Conflict** | Change `PORT=8000` in `.env` to an open port (e.g., `PORT=8081`) and run `docker compose up -d` |
| **Static files missing** | Verify `whitenoise` is in `MIDDLEWARE` and `collectstatic` completed in logs |
| **Database Connection Error** | Check `DATABASE_URL` in `.env` and verify outbound network access to PostgreSQL |
