import requests
import os

# ENVIRON VARS
USER_EMAIL = os.environ['PETZI_LOGIN_EMAIL'] 
USER_PW = os.environ['PETZI_LOGIN_PW']


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


SDR = requests.get(DEVICE_URL.format(userID, ""), headers=petzi_header)


# Get device session status
SESSION_STATUS_URL = "https://api.petzila.com/api/petziConnect/sessionStatus/{}"
SR = requests.get(SESSION_STATUS_URL.format(deviceID), headers=petzi_header)

print(SR.json())


