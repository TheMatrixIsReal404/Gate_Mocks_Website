import urllib.request
import json

api_key = 'AIzaSyDAPuhGaoq4El7hZCHxA6J0Zax_DXMaCdY'
auth_url = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}'

try:
    payload = json.dumps({"returnSecureToken": True}).encode('utf-8')
    req = urllib.request.Request(auth_url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        token = res.get('idToken')
        print('Auth Token acquired! UID:', res.get('localId'))

        fs_url = f'https://firestore.googleapis.com/v1/projects/gate-cse-platform/databases/(default)/documents/questions?pageSize=5&key={api_key}'
        fs_req = urllib.request.Request(fs_url, headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(fs_req) as fs_resp:
            fs_data = json.loads(fs_resp.read().decode('utf-8'))
            docs = fs_data.get('documents', [])
            print('Firestore docs count:', len(docs))
            for d in docs:
                print('  Doc ID:', d['name'].split('/')[-1])
except Exception as e:
    print('Error:', e)
