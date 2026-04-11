bind = "0.0.0.0:8000"

workers = 2

timeout = 120
max_requests = 1000
max_requests_jitter = 50

accesslog = "-"
errorlog = "-"
loglevel = "info"

# 앱 사전 로드
preload_app = False

# 스레드 워커 사용
worker_class = "gthread"
threads = 1

# 연결 유지 시간
keepalive = 5

# 리버스 프록시 IP 신뢰
forwarded_allow_ips = "*"
