import uuid as poop
import requests
import os
import hashlib
from requests.auth import HTTPDigestAuth


# ENVIRON VARS
USER_EMAIL = os.environ['PETZI_LOGIN_EMAIL'] 
USER_PW = os.environ['PETZI_LOGIN_PW']

# OTHER VARS
SESSION_SERVER_DIGEST_USER = "ssaccess"
SESSION_SERVER_DIGEST_PW = "vauTynjgReKgUze"

# Sign in 

USER_URL = "https://api.petzila.com/api/user/login"
userData = {"email": USER_EMAIL, "password": USER_PW, "loginType": "local"}
SIR = requests.post(USER_URL, data=userData)

print(SIR.json(), '\n')

userName = SIR.json()['data']['username']
userKey = SIR.json()['data']['token']
userID = SIR.json()['data']['id']

print('User({}) token is: {}\n'.format(userName, userKey))
print('User ID is {}\n'.format(userID))

# Get petzi camera id
petzi_header = {"X-ZUMO-APPLICATION": "", "version": "2",  "userKey": str(userKey)} 

DEVICE_URL = "https://api.petzila.com/api/user/{}/devices/{}"
DR = requests.get(DEVICE_URL.format(userID, ""), headers=petzi_header)
print('device response: {}\n'.format(DR.json()))


deviceID = DR.json()['data'][0]['pzcId']
print('device id is {}\n'.format(deviceID))


SDR = requests.get(DEVICE_URL.format(userID, deviceID), headers=petzi_header)
print('with deivce id: \n ',  SDR.json())

# Start device session
# Only do this if you're getting 1003 error code with Session Not Found. 
#START_SESSION_URL = "https://api.petzila.com/api/petziConnect/startSession/{}"
#x = START_SESSION_URL.format(deviceID)
#print(x)
#SSR = requests.post(x, headers=petzi_header)
#print('hoogididigj', SSR)

# Get device session status
SESSION_STATUS_URL = "https://api.petzila.com/api/petziConnect/sessionStatus/{}"
SR = requests.get(SESSION_STATUS_URL.format(deviceID), headers=petzi_header)

print(SR.json())
ssIp = SR.json()['data']['ssIp']
ssNonce = SR.json()['data']['ssNonce']
ssPassword = SR.json()['data']['ssPassword']
publish_point_url = SR.json()['data']['publishPoints']['iOS']
stream_name = SR.json()['data']['publishPoints']['streamName']
msNonce = SR.json()['data']['msNonce']

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
