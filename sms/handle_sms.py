from gsmmodem.modem import GsmModem
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config import PINECONE_API_KEY, PINECONE_REGION, WHITELISTED_NUMBERS, INDEX
from agent.agent import get_conversational_agent
from memory.redis_ops import redis_client, get_or_set_user_data, set_user_data, get_or_set_user_data, get_received_sms_parts, set_received_sms_parts, clear_received_sms_parts
from requests.exceptions import ConnectionError


import time
import threading



def is_whitelisted(number):
    return number in WHITELISTED_NUMBERS

def handle_conversation(sms, modem, user_data):
    usrMessage = sms.text.lower()
    usrNumber = sms.number

    user_name = user_data['user_name']
    user_obj = user_data['user_obj']
    bot_personality = user_data['bot_personality']
    bot_name = user_data['bot_name']

    try:
        conversational_agent = get_conversational_agent(usrNumber, user_name, user_obj, bot_personality, bot_name)

        response = conversational_agent({
            'input': usrMessage,
            'usrNumber': usrNumber,
            'user_name': user_name,
            'user_obj': user_obj,
            'bot_personality': bot_personality,
            'bot_name': bot_name
        })

        output = response['output']

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=350,
            chunk_overlap=0,  # number of tokens overlap between chunks
            length_function=len,
            separators=['\n\n', '\n', "        ", '.']
        )

        output_chunks = text_splitter.split_text(output)

        for chunk in output_chunks:
            modem.sendSms(sms.number, chunk)
            print("Sending response: {0}".format(chunk))
    except Exception as e:
        print("Error:", e)
        modem.sendSms(sms.number, "What was that?")



def handle_sms(sms, modem):
    print("Received SMS from: {0}, message: {1}".format(sms.number, sms.text))

    usrNumber = sms.number  # Extract the user's phone number
    
    if sms.udh:
        print("Processing multipart SMS")
        multipart = sms.udh[0]  
        multipart_id = multipart.reference
        multipart_seq_no = multipart.number
        multipart_max_seq = multipart.parts

        sms_parts = get_received_sms_parts(usrNumber)

        sms_parts[multipart_seq_no] = sms.text

        if len(sms_parts) == multipart_max_seq:
            usrMessage = ''.join([sms_parts[i] for i in range(1, multipart_max_seq + 1)])
            clear_received_sms_parts(usrNumber)  # remove the handled message parts
            print("Final concatenated message: " + usrMessage)
        else:
            set_received_sms_parts(usrNumber, multipart_seq_no, sms.text)
            print("Waiting for more parts of the message")
            return
    else:
        usrMessage = sms.text.lower()
        print("Single part message: " + usrMessage)

    if not is_whitelisted(usrNumber):
        modem.sendSms(sms.number, "You are not authorized to use this service.")
        return

    user_data, is_new_user = get_or_set_user_data(usrNumber)  # Updated this line to receive is_new_user value

    # Pinecone RC2
    # from initialization import client
    # index = client.get_index(INDEX)

    import pinecone 
    pinecone.init(api_key=PINECONE_API_KEY, enviroment=PINECONE_REGION) # One time init
    index = pinecone.Index(INDEX)


    if usrMessage.lower() == 'reset personality':
        redis_client.delete(usrNumber)
        modem.sendSms(usrNumber, "Personality reset, all variables removed")
        set_user_data(usrNumber, 'mode', 'conversational_agent')
        return

    elif usrMessage.lower() == 'reset memory':
        index.delete(deleteAll='true', namespace=usrNumber)
        modem.sendSms(usrNumber, "Memory reset, history deleted")
        #index.delete_all(namespace=usrNumber)
        return
    


    if is_new_user or int(user_data.get('setup_step', '0')) < 5:  # Update this line
        if int(user_data.get('setup_step', '0')) == 0:  # Update this line
            modem.sendSms(sms.number, "Welcome, Setup will begin shortly, your will be asked questions, the answers you give will largely determine your new companions behavior")
            modem.sendSms(sms.number, "If you change your mind later, you can type 'Reset Personality' and 'Reset Memory' and the respective data will be deleted.")
            time.sleep(2)
            modem.sendSms(sms.number, "Answering with only one or two words, please provide your name.")
            set_user_data(usrNumber, 'setup_step', '1')
            return

        elif int(user_data.get('setup_step', '0')) == 1:  # Update this line
            set_user_data(usrNumber, 'user_name', usrMessage)
            modem.sendSms(sms.number, "Once again, in a one or two words, please give your companion a name")
            set_user_data(usrNumber, 'setup_step', '2')
            return

        elif int(user_data.get('setup_step', '0')) == 2:  # Update this line
            set_user_data(usrNumber, 'bot_name', usrMessage)
            modem.sendSms(sms.number, "Be creative, how would you describe your new companion's personality? ")
            set_user_data(usrNumber, 'setup_step', '3')
            return

        elif int(user_data.get('setup_step', '0')) == 3:  # Update this line
            set_user_data(usrNumber, 'bot_personality', usrMessage)
            modem.sendSms(sms.number, "Are you have something specific you need help with or do you have a more general objective ? The more detail the better")
            set_user_data(usrNumber, 'setup_step', '4')
            return

        elif int(user_data.get('setup_step', '0')) == 4:  # Update this line
            set_user_data(usrNumber, 'user_obj', usrMessage)
            modem.sendSms(sms.number, "Setup complete. You can start chatting now.")
            set_user_data(usrNumber, 'setup_step', '5')
            set_user_data(usrNumber, 'mode', 'conversational_agent')
            return

    else:
        current_mode = user_data['mode']
        if current_mode == 'conversational_agent':
            handle_conversation(sms, modem, user_data)
        else:
            logging.error(f"Unsupported mode: {current_mode}")



def delete_all_sms(modem):
    try:
        index = 1
        while True:
            try:
                modem.write(f'AT+CMGD={index}')
                index += 1
            except Exception as e:
                # Break the loop when an exception is raised, indicating no more messages to delete
                break
        print("All messages deleted.")
    except Exception as e:
        print("Error while deleting messages:", e) 

def check_sms_storage(modem):
    storage_info = modem.write("AT+CPMS?")
    storage_info_str = ''.join(storage_info)  # Join the list elements to form a single string
    storage_status = storage_info_str.split(',')[1:6:4]  #
    used_slots, total_slots = map(int, storage_status)
    return used_slots, total_slots


def monitor_sms_storage_and_delete(stop_event, modem):
    while not stop_event.is_set():
        used_slots, total_slots = check_sms_storage(modem)
        #print(f"SMS Storage: {used_slots}/{total_slots}")

        if used_slots >= total_slots:
            print("SMS storage is full, deleting all messages.")
            delete_all_sms(modem)

        time.sleep(60)  # Check the storage every 60 seconds (adjust the interval as needed)