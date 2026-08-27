import json, urllib.request, subprocess

EVOLUTION_URL = 'http://localhost:8080'
INSTANCE_NAME = 'BotPesquisa'
API_KEY = 'MACONARIA2026APIKEY'

# Limpa tudo
subprocess.run(['docker', 'exec', 'evolution-postgres', 'psql', '-U', 'postgres', '-d', 'evolution', '-c', 'DELETE FROM \"Typebot\";'])

url_create = f'{EVOLUTION_URL}/typebot/create/{INSTANCE_NAME}'
payload_config = {
    'enabled': True,
    'description': 'Pesquisa FAD',
    'url': 'https://viewer.typebot.io',
    'typebot': 'meu-typebot-mkq5f8e',
    'triggerType': 'keyword',
    'triggerOperator': 'equals',
    'triggerValue': 'TESTAR',
    'expire': 0,
    'delayMessage': 1000,
    'listeningFromMe': False
}
req = urllib.request.Request(url_create, data=json.dumps(payload_config).encode('utf-8'), headers={'apikey': API_KEY, 'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req) as response:
        print('Config:', response.status)
except Exception as e:
    print('Erro:', e)
