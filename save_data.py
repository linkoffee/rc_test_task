import os
import json
from ftplib import FTP
import logging
import logging.config

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Загрузка переменных из .env файла:
load_dotenv()

# Параметры логирования:
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

# Параметры подключения к БД:
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

# Параметры подключения к FTP:
FTP_PARAMS = {
    'host': os.getenv('FTP_HOST'),
    'user': os.getenv('FTP_USER'),
    'passwd': os.getenv('FTP_PASSWD'),
    'directory': os.getenv('FTP_DIRECTORY')
}

# Файл, в который сохранятся данные:
JSON_FILE = os.getenv('JSON_FILE', 'saved_data/pg_data.json')


def fetch_data():
    """Извлекает данные из БД."""
    try:
        logger.debug('Connection to database...')
        connection = psycopg2.connect(**DB_PARAMS)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        logger.debug('Executing a database query...')
        cursor.execute("SELECT * FROM users")
        records = cursor.fetchall()
        cursor.close()
        connection.close()
        logger.debug('All data successfully retrieved from database.')
        return records
    except Exception as error:
        logger.error(f'Error while retrieving data: {error}.')
        raise


def save_data_to_json(data, file_path):
    """Сохраняет полученные данные в формате `.json`."""
    try:
        logger.debug(f'Saving data in {file_path}...')
        with open(file_path, 'w') as file:
            json.dump(data, file, default=str, indent=4)
        logger.debug('All data successfully saved in json.')
    except Exception as error:
        logger.error(f'Error saving data: {error}.')
        raise


def upload_to_ftp(file_path):
    """Загружает json файл на FTP-сервер."""
    try:
        logger.debug('Connection to FTP...')
        with FTP(
            FTP_PARAMS['host'], FTP_PARAMS['user'], FTP_PARAMS['passwd']
        ) as ftp:
            ftp.cwd(FTP_PARAMS['directory'])
            logger.debug('Upload file to FTP server...')
            with open(file_path, 'rb') as file:
                ftp.storbinary(f'STOR {os.path.basename(file_path)}', file)
            logger.debug('File successfully uploaded to FTP server.')
    except Exception as error:
        logger.error(f'Error uploading file to ftp server: {error}.')
        raise


def main():
    logger.debug('Starting program...')
    try:
        if not os.path.exists('saved_data'):
            os.makedirs('saved_data')
        data = fetch_data()
        save_data_to_json(data, JSON_FILE)
        upload_to_ftp(JSON_FILE)
        logger.debug('Successfully.')
    except Exception as error:
        logger.critical(f'The program terminated with an error: {error}')
        raise


if __name__ == '__main__':
    main()
