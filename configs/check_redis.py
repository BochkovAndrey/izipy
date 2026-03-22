#!/usr/bin/env python3
import redis
import os
import time
import sys

def check_redis():
    redis_host = "redis"
    redis_port = 6379
    redis_password = os.getenv("REDIS_PASSWORD", "")
    
    for i in range(30):
        try:
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                socket_connect_timeout=5,
                decode_responses=True
            )
            if r.ping():
                print("✅ Redis connection successful!")
                return True
        except Exception as e:
            print(f"⏳ Attempt {i+1}/30: Redis not ready - {str(e)}")
            time.sleep(2)
    
    print("❌ Redis connection failed after 30 attempts!")
    return False

if __name__ == "__main__":
    sys.exit(0 if check_redis() else 1)