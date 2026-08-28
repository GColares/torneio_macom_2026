import json, urllib.request, subprocess
subprocess.run(['docker', 'exec', 'evolution-postgres', 'psql', '-U', 'postgres', '-d', 'evolution', '-c', 'DELETE FROM \"Typebot\";'])
