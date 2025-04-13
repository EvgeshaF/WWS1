import os
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv


class MongoConnection:
    @staticmethod
    def check_mongo_config_exists():
        venv_dir = Path('.venv')
        config_path = venv_dir / 'mongo_config.env'
        return config_path.exists()

    @staticmethod
    def test_connection():
        try:
            # Load config from .venv/mongo_config.env if it exists
            venv_dir = Path('.venv')
            config_path = venv_dir / 'mongo_config.env'

            if config_path.exists():
                load_dotenv(config_path)

            host = os.getenv('MONGO_HOST')
            port = os.getenv('MONGO_PORT')
            login = os.getenv('MONGO_LOGIN')
            password = os.getenv('MONGO_PASSWORD')
            database = os.getenv('MONGO_DATABASE')

            if not all([host, port, login, password, database]):
                return False, "MongoDB configuration is incomplete"

            # URL encode the password to handle special characters
            from urllib.parse import quote_plus
            encoded_password = quote_plus(password)

            # Construct the MongoDB URI
            mongo_uri = f"mongodb://{login}:{encoded_password}@{host}:{port}/{database}?authSource=admin"

            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

            # Try to list databases to confirm authentication works
            client.list_database_names()

            return True, "Connection to MongoDB successful"
        except ConnectionFailure as e:
            return False, f"Failed to connect to MongoDB: {str(e)}"
        except Exception as e:
            return False, f"An error occurred: {str(e)}"

    @staticmethod
    def save_connection_config(host, port, login, password, database):
        try:
            venv_dir = Path('.venv')

            # Create .venv directory if it doesn't exist
            if not venv_dir.exists():
                venv_dir.mkdir()

            config_path = venv_dir / 'mongo_config.env'

            with open(config_path, 'w') as f:
                f.write(f"MONGO_HOST={host}\n")
                f.write(f"MONGO_PORT={port}\n")
                f.write(f"MONGO_LOGIN={login}\n")
                f.write(f"MONGO_PASSWORD={password}\n")
                f.write(f"MONGO_DATABASE={database}\n")

            return True, "MongoDB configuration saved successfully"
        except Exception as e:
            return False, f"Failed to save MongoDB configuration: {str(e)}"
