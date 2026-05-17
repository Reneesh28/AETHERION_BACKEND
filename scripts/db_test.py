from shared.database.health import mysql_health_check, mongodb_health_check

print("Checking MySQL Health...")
try:
    mysql_ok = mysql_health_check()
    print("MySQL Health Status:", mysql_ok)
except Exception as e:
    print("MySQL Health Check Failed:", e)

print("\nChecking MongoDB Health...")
try:
    mongo_ok = mongodb_health_check()
    print("MongoDB Health Status:", mongo_ok)
except Exception as e:
    print("MongoDB Health Check Failed:", e)
