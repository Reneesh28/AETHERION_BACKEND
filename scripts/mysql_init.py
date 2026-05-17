from shared.database.mysql import get_mysql_connection


connection = get_mysql_connection()

cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS portfolios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    symbol VARCHAR(50),
    quantity FLOAT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS risk_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    max_drawdown FLOAT,
    risk_level VARCHAR(50)
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS simulations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    simulation_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


connection.commit()

print("MySQL tables initialized successfully")