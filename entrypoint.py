# import the flask web framework
from flask import Flask
import json
import redis as redis
from flask import Flask, request
from loguru import logger
import statistics  # Import to calculate the mean

HISTORY_LENGTH = 10
DATA_KEY = "engine_temperature"

# create a Flask server, and allow us to interact with it using the app variable
app = Flask(__name__)

# define an endpoint which accepts POST requests, and is reachable from the /record endpoint
@app.route('/record', methods=['POST'])
def record_engine_temperature():
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")

    engine_temperature = payload.get("engine_temperature")
    logger.info(f"engine temperature to record is: {engine_temperature}")

    # Initialize Redis database connection
    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    
    # Store the engine temperature in Redis
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")

    # Ensure only the last HISTORY_LENGTH records are kept
    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    
    # Retrieve all engine temperature values from Redis
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine temperature list now contains these values: {engine_temperature_values}")

    # Convert the list of temperature values to floats
    engine_temperature_values = list(map(float, engine_temperature_values))

    # Calculate the most recent and average engine temperature
    current_engine_temperature = engine_temperature_values[0]  # Most recent value (head of the list)
    average_engine_temperature = statistics.mean(engine_temperature_values)  # Mean of all values

    # Log the calculated values
    logger.info(f"Current engine temperature: {current_engine_temperature}")
    logger.info(f"Average engine temperature: {average_engine_temperature}")

    logger.info(f"record request successful")
    
    # Return the dictionary with current and average engine temperature
    return {
        "current_engine_temperature": current_engine_temperature,
        "average_engine_temperature": average_engine_temperature
    }, 200


# practically identical to the above
@app.route('/collect', methods=['POST'])
def collect_engine_temperature():
    return {"success": True}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)