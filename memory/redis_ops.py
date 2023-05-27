import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB


redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

def get_or_set_user_data(usrNumber):
    user_data_bytes = redis_client.hgetall(usrNumber)
    is_new_user = False

    if user_data_bytes:
        user_data = {key.decode(): value.decode() for key, value in user_data_bytes.items()}
    else:
        user_data = {
            'user_name': None,
            'bot_name': None,
            'bot_personality': None,
            'user_obj': None,
            'setup_step': 0,
            'mode': 'conversational_agent'
        }
        is_new_user = True

    return user_data, is_new_user




def set_user_data(usrNumber, key, value):
    redis_client.hset(usrNumber, key, value)

def get_or_set_user_data(usrNumber):
    user_data_bytes = redis_client.hgetall(usrNumber)
    is_new_user = False

    if user_data_bytes:
        user_data = {key.decode(): value.decode() for key, value in user_data_bytes.items()}
    else:
        user_data = {
            'user_name': None,
            'bot_name': None,
            'bot_personality': None,
            'user_obj': None,
            'setup_step': 0,
            'mode': 'conversational_agent'
        }
        is_new_user = True

    return user_data, is_new_user

def get_received_sms_parts(usrNumber):
    sms_parts_bytes = redis_client.hgetall(usrNumber + "_sms_parts")

    if sms_parts_bytes:
        sms_parts = {int(key.decode()): value.decode() for key, value in sms_parts_bytes.items()}
    else:
        sms_parts = {}

    return sms_parts


def set_received_sms_parts(usrNumber, key, value):
    redis_client.hset(usrNumber + "_sms_parts", key, value)


def clear_received_sms_parts(usrNumber):
    redis_client.delete(usrNumber + "_sms_parts")