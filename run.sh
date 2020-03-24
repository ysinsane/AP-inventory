pkill -F ap_inventory
gunicorn -w 4 -b 0.0.0:8000  --log-leve=warning --access-logfile=access.log --daemon -p ap_inventory.pid --error-logfile=error.log manage:app