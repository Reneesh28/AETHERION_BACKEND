import os
from pydantic import model_validator

from shared.config.kafka import KafkaConfig
from shared.config.redis import RedisConfig
from shared.config.database import DatabaseConfig
from shared.config.monitoring import MonitoringConfig
from shared.config.services import ServiceConfig


class Settings(
    KafkaConfig,
    RedisConfig,
    DatabaseConfig,
    MonitoringConfig,
    ServiceConfig
):
    
    @model_validator(mode="after")
    def adjust_local_settings(self) -> 'Settings':
        # If running inside a Docker container (standard container indicator is /.dockerenv), keep original values
        if os.path.exists('/.dockerenv'):
            return self

        # Otherwise, we are running locally on the host machine.
        # Automatically map Docker DNS names to localhost.
        if hasattr(self, 'KAFKA_BOOTSTRAP_SERVERS'):
            self.KAFKA_BOOTSTRAP_SERVERS = self.KAFKA_BOOTSTRAP_SERVERS.replace('kafka', 'localhost')
            
        if hasattr(self, 'REDIS_HOST') and self.REDIS_HOST == 'redis':
            self.REDIS_HOST = 'localhost'
            
        if hasattr(self, 'MYSQL_HOST') and self.MYSQL_HOST == 'mysql':
            self.MYSQL_HOST = 'localhost'
            # Adjust MySQL port to the host-mapped port (3307)
            if hasattr(self, 'MYSQL_PORT') and self.MYSQL_PORT == 3306:
                self.MYSQL_PORT = 3307
                
        if hasattr(self, 'MONGO_HOST') and self.MONGO_HOST == 'mongodb':
            self.MONGO_HOST = 'localhost'
            
        return self


settings = Settings()