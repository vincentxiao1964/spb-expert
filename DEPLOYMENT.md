# 部署与合规自查（Web + 小程序）

## 一、必须满足（高优先级）

### 1) 生产环境关闭调试

- 确认生产环境 `DEBUG=False`
- 确认线上访问接口不会返回 Django/DRF Traceback 页面

### 2) 域名与 HTTPS

- Web 端必须通过 HTTPS 访问
- 小程序 request 合法域名必须配置 HTTPS 域名（不能用 127.0.0.1 / 局域网地址）

### 3) 关键环境变量

复制 `.env.example` 为 `.env`，填入真实值（不要提交到仓库）：

- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `CORS_ALLOWED_ORIGINS`

## 二、推荐的安全项（中优先级）

- `SECURE_SSL_REDIRECT=True`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `USE_X_FORWARDED_PROTO=True`（Nginx 反代到 Django 时）
- HSTS：
  - `SECURE_HSTS_SECONDS=31536000`
  - `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
  - `SECURE_HSTS_PRELOAD=True`

## 三、小程序后台合规配置

在微信公众平台「开发管理 → 开发设置」配置合法域名：

- request 合法域名：`https://www.barge-expert.com`
- uploadFile/downloadFile/socket 合法域名：按实际用到的能力配置

## 四、上线后自检

### 1) 后端接口自检

- `GET /api/v1/listings/?page=1` 返回 200
- `GET /api/v1/user/info/` 未登录返回 401（正常）

### 2) Web 页面自检

- 首页可打开、样式正常
- 详情页可打开

### 3) 静态文件

上传代码后执行：

```bash
python manage.py collectstatic --noinput
```

并确保 Nginx 的静态资源路径指向 `/srv`（迁移后常见错误是仍指向 `/root`，会导致 `/static/...` 返回 403，页面只剩文字）：

- `location /static/ { alias /srv/spb-expert9/staticfiles/; }`
- `location /media/  { alias /srv/spb-expert9/media/; }`

示例文件见：

- `deploy/nginx/barge-expert.nginx.conf.example`

### 4) systemd 与 unix socket

建议用低权限用户 + unix socket：

- WorkingDirectory：`/srv/spb-expert9`
- ExecStart：用 `/srv/spb-expert9/venv/bin/python3 -m gunicorn ... --bind unix:/run/spb-expert9/spb-expert9.sock`
- socket 权限：建议 `UMask=0007`，并让 `nginx` 加入 `spbexpert` 组

示例文件见：

- `deploy/systemd/spb-expert9.service`

## 五、运维提醒

- 不在聊天或任何公开渠道发送服务器密码/密钥
- 线上服务建议用 gunicorn/uwsgi + nginx + supervisor/systemd 管理进程，避免 `runserver` 被意外中断
