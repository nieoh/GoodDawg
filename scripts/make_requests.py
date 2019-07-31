import os
import logging

import uuid 
import requests
import hashlib
from requests.auth import HTTPDigestAuth


# ENVIRON VARS
USER_EMAIL = os.environ['PETZI_LOGIN_EMAIL'] 
USER_PW = os.environ['PETZI_LOGIN_PW']

# OTHER VARS
SESSION_SERVER_DIGEST_USER = "ssaccess"
SESSION_SERVER_DIGEST_PW = "vauTynjgReKgUze"

# LOGGING
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
                '%(asctime)s %(name)-4s %(levelname)-4s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.debug('often makes a very good meal of %s', 'visiting tourists')



# User sign in 
def get_user_signin(user_email: str, user_password: str) -> dict:
    """ Returns a json of the API request for user sign-in. 

    Keyword arguments:
    user_email -- user log in email
    user_password -- user log in password
    """
    USER_URL = "https://api.petzila.com/api/user/login"
    user_data = {"email": user_email, "password": user_password, "loginType": "local"}
    user_signin_request = requests.post(USER_URL, data=user_data)
    logger.info('user sign in request reponse: {}'.format(user_signin_request.text))
    #TODO: add debug for not 200 response.
    #TODO: add debug for not success status in response.
    try: 
        ret = user_signin_request.json()
    except Exception as e:
        logger.debug('user sign in request no json response: {}'.format(str(e)))
        ret = {}
    return ret

SIR = get_user_signin(USER_EMAIL, USER_PW)

def user_signin_dict(SIR: dict) -> dict:
    """Returns a dictionary of user name, key and id.

    Keyword arguments:
    SIR -- user sign in response json
    """
    name, key, id = '', '', ''
    if 'data' in SIR:
        if 'username' in SIR['data']:
            name = SIR['data']['username']
        if 'token' in SIR['data']:
            key = SIR['data']['token']
        if 'id' in SIR['data']:
            id = SIR['data']['id']
    logger.info('user sign in vars: \n \
            user name: {}, \n \
            user key: {}, \n \
            user id: {}'.format(name, key, id))
    return {'user_name': name, 'user_key': key, 'user_id': id}

user_dict = user_signin_dict(SIR)


# Get petzi camera id
def petzi_header(user_key: str) -> dict:
    ret = {"X-ZUMO-APPLICATION": "", "version": "2",  "userKey": user_key} 
    logger.info('petzi header: {}'.format(ret))
    return ret

p_header = petzi_header(user_dict['user_key'])

# Get device(ptc) information
def get_ptc_status(user_id: str, petzi_header: dict) -> dict:
    DEVICE_URL = "https://api.petzila.com/api/user/{}/devices/{}"
    ptc_status_request= requests.get(DEVICE_URL.format(user_id, ""), 
                                    headers=petzi_header)
    logger.info('device status request response: {}'.format(ptc_status_request.text))
    #TODO: add debug for not 200 response.
    #TODO: add debug for not success status in response.

    try:
        ret = ptc_status_request.json()
    except Exception as e:
        logger.debug('device status request no json response: {}'.format(str(e)))
        ret = {}
    return ret

DR = get_ptc_status(user_dict['user_id'], p_header)

def device_id(ptc_status_response: dict) -> str:
    """Return petzi treat cam device id

    Keyword arugments:
    ptc_status_response -- response from device url end point
    """
    try:
        ret = ptc_status_response['data'][0]['pzcId']
        logger.info('device id is: {}'.format(ret))    
    except Exception as e:
        logger.debug('device response data does not have petzi id: {}'.format(str(e)))
        ret = ''
    return ret
   

device_id(DR)

#SDR = requests.get(DEVICE_URL.format(userID, deviceID), headers=petzi_header)
#print('with deivce id: \n ',  SDR.json())

# Start device session
# Only do this if you're getting 1003 error code with Session Not Found. 
#START_SESSION_URL = "https://api.petzila.com/api/petziConnect/startSession/{}"
#x = START_SESSION_URL.format(deviceID)
#print(x)
#SSR = requests.post(x, headers=petzi_header)
#print('hoogididigj', SSR)

# Get device session status
def get_session_status(device_id: str, petzi_header: dict) -> dict:
    """Returns session status response.

    Keyword arguments:
    device_id -- petzi treat cam device id from get_ptc_status call
    """
    SESSION_STATUS_URL = "https://api.petzila.com/api/petziConnect/sessionStatus/{}"
    session_status_request = requests.get(SESSION_STATUS_URL.format(device_id), 
            headers=petzi_header)
    logger.info('session status request response: {}'.format(session_status_request))
    #TODO: add debug for not 200 response.
    #TODO: add debug for not success status in response.
    try:
        ret = session_status_request.json()
    except Exception as e:
        logger.debug('session status request no json response: {}'.format(str(e)))
        ret = {}
    return ret

SR = get_session_status(device_id(DR), p_header)

def session_dict(SR: dict) -> dict:
    """Returns dict of session status info

    Keyword arguments:
    SR -- session status response
    """
    ss_ip, ss_nonce, ss_password, publish_point_url, stream_name, ms_nonce = '', '', '', '', '', ''
    if 'data' in SR:
        ss_ip = SR['data']['ssIp']
        ss_nonce = SR['data']['ssNonce']
        ss_password = SR['data']['ssPassword']
        publish_point_url = SR['data']['publishPoints']['iOS']
        stream_name = SR['data']['publishPoints']['streamName']
        ms_nonce = SR['data']['msNonce']

    ret = {'ssip': ss_ip,
            'ssnonce': ss_nonce, 
            'sspassword': ss_password, 
            'publish_point_url': publish_point_url,
            'stream_name': stream_name, 
            'msnonce': ms_nonce
            }

    logger.info('session info: '.format(ret))
    return ret

session_dict(SR)


# Authenticate server
API_PATH_SESSION_SERVER_AUTHENTICATION = "http://{ssIp}/api/auth/{deviceID}/{uuid}/{hashCode}"
uuid = "f008d119-53fb-4116-a683-a522d51bfc40"# #UUID.randomUUID().toString();
#uuid = "232d564a-5c3d-497f-a361-8418e9dc742d"#"046b6a7f-0b8a-43b9-b36d-6489e6daee91" 
sb = ''
sb += ssNonce
sb += uuid
sb += ssPassword
hashCode = hashlib.sha1(sb.encode('utf-8')).hexdigest() #Hashing.sha1().hashString(sb, Charset.defaultCharset()).toString();
print('hashcode: ', hashCode)


url = API_PATH_SESSION_SERVER_AUTHENTICATION.format(ssIp=ssIp, deviceID=deviceID, uuid=uuid, hashCode=hashCode) 
no_auth_header = {"Accept": "application/json", "Content-Type": "application/json"}
print(url)
authR = requests.get(url,  
        headers=no_auth_header, 
        auth=HTTPDigestAuth(SESSION_SERVER_DIGEST_USER, SESSION_SERVER_DIGEST_PW))
print(authR.json())
session_token = ''
if 'token' in authR.json():
    session_token = authR.json()['token']


# Keep session server alive
API_PATH_SESSION_SERVER_KEEP_ALIVE = "http://{ssIp}/api/keep_alive/{deviceID}"
other_header = {"Content-Type": "application/json", "token": session_token}
print(other_header)
keep_aliver=requests.put(API_PATH_SESSION_SERVER_KEEP_ALIVE.format(ssIp=ssIp, deviceID=deviceID), 
        headers=other_header,
        auth=HTTPDigestAuth(SESSION_SERVER_DIGEST_USER, SESSION_SERVER_DIGEST_PW))
print(keep_aliver.text)


# make jingle
START_JINGLE_URL = "http://{ssIp}/api/cmd/{deviceID}/start_music"
jingle_params = '{"data": {"song": "jingle", "mode": "one_time"}}'
print('jingle url: ',START_JINGLE_URL.format(ssIp=ssIp, deviceID=deviceID))
print('jingle header: ', other_header)
print('jingle data: ', jingle_params)

jingleR = requests.put(START_JINGLE_URL.format(ssIp=ssIp, deviceID=deviceID), 
        headers=other_header, 
        data=jingle_params, 
        auth=HTTPDigestAuth(SESSION_SERVER_DIGEST_USER, SESSION_SERVER_DIGEST_PW))

print(jingleR)
print(jingleR.text)

#stateR = requests.put("http://{}/api/cmd/{}/state".format(ssIp, deviceID), headers=other_header, auth=HTTPDigestAuth(SESSION_SERVER_DIGEST_USER, SESSION_SERVER_DIGEST_PW))

#print(stateR.text)




def media_stream_url(publish_point_url, stream_name, deviceID, msNonce):
    uuid = str(poop.uuid4()) 
    sb = str(msNonce) + uuid
    hash_code = hashlib.sha1(sb.encode('utf-8')).hexdigest()
    
    sb2 = str(publish_point_url)
    sb2 += "?pzcId="
    sb2 += str(deviceID)
    sb2 += "&cnonce="
    sb2 += uuid
    sb2 += "&hash="
    sb2 += hash_code
    sb2 += "/"
    sb2 += str(stream_name)

    return sb2


print('media stream url is: ', media_stream_url(publish_point_url, stream_name, deviceID, msNonce))
