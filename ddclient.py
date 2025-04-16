import requests
import time

# 🔧 KONFIG
API_TOKEN = 'your_cloudflare_api_token'
ZONE_NAME = 'yourzone.com'
RECORD_NAMES = ['yourdomain1.com', 'yourdomain2.com', 'sub.yourdomain.uk']
SLEEP_TIME = 300  # 5 perc

# API HEADERS
headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json',
}

def get_public_ip():
    return requests.get('https://api.ipify.org').text.strip()

def get_zone_id():
    url = f'https://api.cloudflare.com/client/v4/zones?name={ZONE_NAME}'
    r = requests.get(url, headers=headers).json()
    return r['result'][0]['id']

def get_record_id(zone_id, record_name):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={record_name}'
    r = requests.get(url, headers=headers).json()
    return r['result'][0]['id']

def update_dns_record(zone_id, record_id, record_name, ip):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
    data = {
        'type': 'A',
        'name': record_name,
        'content': ip,
        'ttl': 1,
        'proxied': False
    }
    r = requests.put(url, headers=headers, json=data)
    return r.json()

def main():
    last_ip = None
    zone_id = get_zone_id()
    record_ids = {}

    for name in RECORD_NAMES:
        record_ids[name] = get_record_id(zone_id, name)

    while True:
        current_ip = get_public_ip()
        if current_ip != last_ip:
            print(f'\n🔄 New public IP detected: {last_ip} → {current_ip}')
            for name in RECORD_NAMES:
                print(f'➡️  Uptdating: {name} → {current_ip}')
                result = update_dns_record(zone_id, record_ids[name], name, current_ip)
                if result['success']:
                    print(f'✅ {name} updated!')
                else:
                    print(f'❌ {name} update unsuccessful:', result)
            last_ip = current_ip
        else:
            print(f'⏳ No IP change detected ({current_ip}), sleeping for 5 minutes...')
        time.sleep(SLEEP_TIME)

if __name__ == '__main__':
    main()
