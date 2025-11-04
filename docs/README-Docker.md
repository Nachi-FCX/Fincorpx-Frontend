# Docker Setup for FinCorpX

This document explains how to build and run the FinCorpX Vue.js application using Docker.

## Files Created

- `Dockerfile` - Multi-stage build configuration
- `nginx.conf` - Nginx configuration for SPA routing
- `.dockerignore` - Files to exclude from Docker build context
- `docker-compose.yml` - Docker Compose configuration for easy deployment

## Building and Running

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start the application
docker-compose up --build

# Run in detached mode (background)
docker-compose up -d --build

# Stop the application
docker-compose down
```

The application will be available at: http://localhost:3000

### Option 2: Using Docker Commands

```bash
# Build the Docker image
docker build -t fincorpx .

# Run the container
docker run -d -p 3000:80 --name fincorpx-app fincorpx

# Stop the container
docker stop fincorpx-app

# Remove the container
docker rm fincorpx-app
```

## Docker Configuration Details

### Multi-Stage Build

The Dockerfile uses a multi-stage build approach:

1. **Build Stage**: Uses Node.js 18 Alpine to build the Vue.js application
2. **Production Stage**: Uses Nginx Alpine to serve the built static files

### Nginx Configuration

The `nginx.conf` includes:
- SPA routing support (handles Vue Router client-side routes)
- Gzip compression for better performance
- Static asset caching with long expiration times
- Security headers
- Optimized for serving Vue.js applications

### Port Configuration

- Container exposes port 80 (Nginx default)
- Docker Compose maps it to localhost:3000
- You can change the external port in `docker-compose.yml`

## Customization

### Changing the Port

Edit `docker-compose.yml` and modify the ports mapping:
```yaml
ports:
  - "8080:80"  # Change 8080 to your desired port
```

### Environment Variables

Add environment variables in `docker-compose.yml`:
```yaml
environment:
  - NODE_ENV=production
  - API_URL=https://your-api-url.com
```

### Custom Nginx Configuration

Modify `nginx.conf` to customize server behavior, add SSL, or change caching rules.

## Troubleshooting

### Build Issues
- Ensure all dependencies are properly listed in `package.json`
- Check that the build command `npm run build` works locally
- Verify Node.js version compatibility

### Runtime Issues
- Check container logs: `docker-compose logs fincorpx`
- Verify port availability: `netstat -an | grep 3000`
- Test Nginx configuration: `docker exec -it fincorpx-app nginx -t`

### SPA Routing Issues
- Ensure `nginx.conf` includes the `try_files` directive
- Check that Vue Router is configured for history mode
- Verify all routes work when accessing directly via URL

## Production Deployment

For production deployment:

1. Update `nginx.conf` with your domain name
2. Add SSL configuration
3. Configure environment-specific variables
4. Set up proper logging and monitoring
5. Consider using a reverse proxy (like Traefik or nginx-proxy)

## Performance Optimization

The current setup includes:
- Gzip compression
- Static asset caching
- Optimized Docker image layers
- Multi-stage build to reduce final image size

For further optimization:
- Enable HTTP/2 in Nginx
- Add CDN for static assets
- Implement proper cache headers for API calls
- Consider using nginx-brotli for better compression
