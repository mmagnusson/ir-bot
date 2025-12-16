# Deployment Guide

This guide covers deploying the IR AI Assistant for development and production use.

## Development Deployment

For local development, see [QUICK_START.md](../QUICK_START.md).

## Production Deployment Considerations

⚠️ **WARNING**: The MVP is not production-ready out of the box. Review the security requirements below before deploying to production.

### Required Security Enhancements

Before production deployment, implement:

1. **Authentication & Authorization**
   - User authentication (SSO/SAML preferred)
   - Role-based access control
   - Multi-factor authentication
   - Session management

2. **Data Protection**
   - Replace in-memory storage with persistent database
   - Implement encryption at rest
   - Ensure TLS/SSL for all connections
   - Secure credential storage (use secrets manager)

3. **Audit & Logging**
   - Comprehensive audit logging
   - Log retention policies
   - SIEM integration
   - Alerting on suspicious activities

4. **Rate Limiting & DDoS Protection**
   - API rate limiting per user
   - Request size limits
   - DDoS protection (CloudFlare, AWS Shield, etc.)

5. **Network Security**
   - Web Application Firewall (WAF)
   - Network segmentation
   - Reverse proxy (nginx, Traefik)
   - VPN/private network access

## Database Setup (Production)

### Option 1: PostgreSQL

1. Install PostgreSQL:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

2. Create database and user:
```sql
CREATE DATABASE ir_assistant;
CREATE USER ir_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ir_assistant TO ir_user;
```

3. Update backend to use SQLAlchemy (requires code changes):
```python
# Add to requirements.txt
sqlalchemy==2.0.23
psycopg2-binary==2.9.9

# Update incidents.py to use database instead of in-memory dict
```

### Option 2: SQLite (Development/Small Scale)

1. Update backend to use SQLite:
```python
# Add to requirements.txt
sqlalchemy==2.0.23

# Use SQLite database file
DATABASE_URL = "sqlite:///./ir_assistant.db"
```

## Docker Deployment

### Create Dockerfiles

**Backend Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=postgresql://ir_user:secure_password@db:5432/ir_assistant
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ir_assistant
      - POSTGRES_USER=ir_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Deploy with Docker Compose

```bash
# Set environment variables
export ANTHROPIC_API_KEY=your-api-key

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Cloud Deployment

### AWS Deployment

#### Option A: AWS Elastic Beanstalk

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize Elastic Beanstalk:
```bash
eb init -p python-3.11 ir-assistant
```

3. Create environment:
```bash
eb create ir-assistant-prod
```

4. Set environment variables:
```bash
eb setenv ANTHROPIC_API_KEY=your-api-key
```

5. Deploy:
```bash
eb deploy
```

#### Option B: AWS ECS (Fargate)

1. Build and push Docker images to ECR
2. Create ECS cluster
3. Define task definitions for backend and frontend
4. Create services with load balancer
5. Configure RDS for database
6. Set up CloudWatch for logging

### Google Cloud Deployment

#### Cloud Run

1. Build container:
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/ir-assistant-backend
```

2. Deploy:
```bash
gcloud run deploy ir-assistant \
  --image gcr.io/PROJECT-ID/ir-assistant-backend \
  --platform managed \
  --set-env-vars ANTHROPIC_API_KEY=your-api-key
```

### Azure Deployment

#### Azure App Service

1. Create App Service:
```bash
az webapp create \
  --resource-group ir-assistant-rg \
  --plan ir-assistant-plan \
  --name ir-assistant \
  --runtime "PYTHON:3.11"
```

2. Configure:
```bash
az webapp config appsettings set \
  --resource-group ir-assistant-rg \
  --name ir-assistant \
  --settings ANTHROPIC_API_KEY=your-api-key
```

3. Deploy:
```bash
az webapp up --name ir-assistant
```

## Reverse Proxy Setup (nginx)

**nginx.conf**:
```nginx
server {
    listen 80;
    server_name ir-assistant.example.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

## SSL/TLS Configuration

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d ir-assistant.example.com

# Auto-renewal is set up automatically
```

## Monitoring & Logging

### Application Monitoring

Consider implementing:

- **Application Performance Monitoring (APM)**
  - New Relic
  - Datadog
  - AWS CloudWatch

- **Log Aggregation**
  - ELK Stack (Elasticsearch, Logstash, Kibana)
  - Splunk
  - AWS CloudWatch Logs

- **Error Tracking**
  - Sentry
  - Rollbar

### Health Checks

Add health check endpoints:

```python
# backend/app/main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_service": ai_service.test_connection()
    }
```

### Metrics

Track key metrics:
- API response times
- AI call latency
- Incident creation rate
- Error rates
- User activity

## Backup & Disaster Recovery

### Database Backups

**Automated PostgreSQL backups**:
```bash
# Daily backup script
#!/bin/bash
pg_dump -U ir_user ir_assistant > backup_$(date +%Y%m%d).sql
```

**Backup retention**:
- Daily backups for 7 days
- Weekly backups for 4 weeks
- Monthly backups for 12 months

### Incident Data Export

Implement automated exports of incident data for compliance and audit purposes.

## Scaling Considerations

### Horizontal Scaling

- Multiple backend instances behind load balancer
- Shared database (PostgreSQL with connection pooling)
- Redis for session storage
- CDN for frontend static assets

### Vertical Scaling

- Increase instance sizes as needed
- Monitor resource usage
- Optimize database queries

### Caching

Implement caching for:
- AI responses (with appropriate TTL)
- Playbook data
- Static assets

## Cost Optimization

### AI API Costs

- Monitor Claude API usage
- Implement caching for repeated queries
- Set usage quotas per user/organization
- Consider local model for basic tasks

### Infrastructure Costs

- Use auto-scaling to match demand
- Reserve instances for predictable workloads
- Implement resource tagging for cost tracking
- Regular cost audits

## Post-Deployment Checklist

- [ ] Authentication & authorization implemented
- [ ] Database configured with backups
- [ ] SSL/TLS certificates configured
- [ ] Environment variables secured (secrets manager)
- [ ] Monitoring and alerting configured
- [ ] Log aggregation set up
- [ ] Rate limiting enabled
- [ ] WAF configured
- [ ] Backup strategy tested
- [ ] Disaster recovery plan documented
- [ ] Security audit completed
- [ ] Penetration testing performed
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Support procedures established

## Support & Maintenance

### Regular Maintenance

- Keep dependencies updated
- Monitor security advisories
- Review logs for anomalies
- Test backups regularly
- Update playbooks as needed

### Incident Management

If the tool itself has issues:
1. Check health endpoints
2. Review application logs
3. Verify database connectivity
4. Test AI service connection
5. Check resource utilization

## Getting Help

For deployment assistance:
- Review this documentation
- Check the main [README.md](../README.md)
- Consult your cloud provider's documentation
- Consider professional DevOps support for production

---

Remember: Production deployment requires careful planning and security considerations. This guide provides a starting point, but each organization's needs are unique.
