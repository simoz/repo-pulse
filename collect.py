"""Collect GitHub traffic using gh; no third-party Python dependencies."""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
# Data lives outside the public code repo (e.g. a checkout of a private repo).
DATA = Path(os.environ.get('DATA_DIR', ROOT)).resolve()

def api(path):
    p = subprocess.run(['gh', 'api', path], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr.strip())
    return json.loads(p.stdout)

def merge(previous, incoming):
    # Replace observations by date: overlapping windows must never be summed.
    result = {row['timestamp']: row for row in previous}
    result.update({row['timestamp']: row for row in incoming})
    return sorted(result.values(), key=lambda row: row['timestamp'])

def main():
    owner = os.environ.get('STATS_OWNER', 'simoz')
    path = DATA / 'data/traffic.json'
    data = json.loads(path.read_text()) if path.exists() else {'repositories': {}}
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    repos, page = [], 1
    while True:
        batch = api(f'user/repos?affiliation=owner&per_page=100&page={page}')
        repos.extend(r for r in batch if r['owner']['login'].lower() == owner.lower())
        if len(batch) < 100:
            break
        page += 1
    errors = []
    for repo in repos:
        name = repo['full_name']
        record = data['repositories'].setdefault(name, {'history': {}})
        record.update(name=name, private=repo['private'], stars=repo['stargazers_count'], archived=repo['archived'])
        record['errors'] = []
        for metric in ('views', 'clones'):
            try:
                response = api(f'repos/{name}/traffic/{metric}')
                record['history'][metric] = merge(record['history'].get(metric, []), response[metric])
                record[metric] = dict(count=response['count'], uniques=response['uniques'], collected_at=now)
            except RuntimeError as exc:
                record['errors'].append(metric)
                errors.append(f'{name} {metric}: {exc}')
    data.update(updated_at=now, owner=owner, active_repositories=[r['full_name'] for r in repos], errors=errors)
    path.parent.mkdir(exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)
    # Embedded data lets the private dashboard work directly from a downloaded file.
    template = (ROOT / 'dashboard.html').read_text()
    payload = json.dumps(data).replace('<', '\\u003c')
    (DATA / 'index.html').write_text(template.replace('/*DATA*/null', payload))
    # Logs may be public: report counts only, details stay in the data file.
    print(f'{len(repos)} repositories, {len(errors)} errors')
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
