# BE_one_piece

## 서버 Scent 데이터 시딩

1. 서버 컨테이너 접속
```bash
docker exec -it django bash
```

2. 스크립트 실행
```bash
PYTHONPATH=/one_piece DJANGO_SETTINGS_MODULE=config.settings.prod python scripts/seed_scent.py
```

3. 로컬에서 향기 데이터 업데이트
```aiignore
make seed
```


