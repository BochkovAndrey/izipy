#!/usr/bin/env python3
"""Скрипт для ожидания готовности PostgreSQL"""
import time
import sys
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def wait_for_postgres():
    """Ожидание доступности PostgreSQL с экспоненциальной задержкой"""
    max_retries = 30
    retry_count = 0
    base_delay = 1
    
    # Получаем параметры подключения из переменных окружения
    host = os.getenv('POSTGRES_HOST', 'postgres')
    port = int(os.getenv('POSTGRES_PORT', 5432))
    user = os.getenv('POSTGRES_USER', 'airflow')
    password = os.getenv('POSTGRES_PASSWORD', 'airflow')
    dbname = os.getenv('POSTGRES_DB', 'superset')
    
    logger.info(f"📊 Ожидание PostgreSQL {host}:{port}/{dbname}...")
    
    # Пробуем импортировать psycopg2
    try:
        import psycopg2
        from psycopg2 import OperationalError
        logger.info("✅ psycopg2 успешно импортирован")
    except ImportError as e:
        logger.error(f"❌ psycopg2 не установлен: {e}")
        return False
    
    while retry_count < max_retries:
        try:
            # Пробуем подключиться к PostgreSQL
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname,
                connect_timeout=5,
                sslmode='disable'
            )
            conn.close()
            logger.info("✅ PostgreSQL доступен!")
            return True
            
        except OperationalError as e:
            retry_count += 1
            
            # Экспоненциальная задержка
            delay = min(base_delay * (2 ** (retry_count - 1)), 10)
            
            if "does not exist" in str(e):
                logger.warning(f"⏳ База данных {dbname} еще не создана...")
            elif "Connection refused" in str(e):
                logger.warning(f"⏳ PostgreSQL еще не принимает подключения...")
            else:
                logger.warning(f"⏳ Попытка {retry_count}/{max_retries}: {str(e)[:100]}")
            
            if retry_count < max_retries:
                logger.info(f"💤 Ожидание {delay}с перед следующей попыткой...")
                time.sleep(delay)
            else:
                logger.error(f"❌ PostgreSQL не доступен после {max_retries} попыток")
                return False
                
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка: {e}")
            return False
    
    return False

if __name__ == "__main__":
    success = wait_for_postgres()
    sys.exit(0 if success else 1)