import subprocess
subprocess.run(['docker', 'exec', 'evolution-postgres', 'psql', '-U', 'postgres', '-d', 'evolution', '-c', 'DELETE FROM \"Typebot\";'])
subprocess.run(['docker', 'restart', 'evolution-api'])
