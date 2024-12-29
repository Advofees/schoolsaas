# Nginx
## api-configuration
- config
    - paste the configs in `nginx.conf` file,run the following on the vps
    
        ```bash 
        sudo vi /etc/nginx/sites-available/api.andrew-nzioki.com
        ```
    - test configuration
        ```bash
        sudo nginx -t
        ```
    - reload nginx
        ```bash
            sudo systemctl reload nginx
        ```