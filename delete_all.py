import subprocess

# Limpa configs antigas
subprocess.run(['docker', 'exec', 'evolution-postgres', 'psql', '-U', 'postgres', '-d', 'evolution', '-c', 'DELETE FROM \"Typebot\";'])

