import subprocess
cmd = ['docker', 'exec', 'evolution-postgres', 'psql', '-U', 'postgres', '-d', 'evolution', '-c', 'DELETE FROM \"Typebot\";']
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
