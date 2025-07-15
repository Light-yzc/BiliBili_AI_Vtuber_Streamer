@echo on 
call D:\MiniConda\Scripts\activate.bat cs224n-cpu
uvicorn flask_backend:app --host 0.0.0.0 --port 5000 --reload --log-level "warning"
