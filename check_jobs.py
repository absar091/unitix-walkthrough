import json

with open('/home/ubuntu/.hermes/cron/jobs.json') as f:
    data = json.load(f)

for j in data['jobs']:
    print(j.get('id'), '| script:', j.get('script'),
          '| enabled:', j.get('enabled'),
          '| state:', j.get('state'),
          '| env:', j.get('env_vars'))
