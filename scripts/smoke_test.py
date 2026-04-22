import os
import re
import sys

import requests


BASE_URL = os.getenv('SMOKE_BASE_URL', 'http://127.0.0.1:8001').rstrip('/')
USERNAME = os.getenv('SMOKE_USERNAME', '')
PASSWORD = os.getenv('SMOKE_PASSWORD', '')
TIMEOUT = int(os.getenv('SMOKE_TIMEOUT', '10'))


def assert_status(response, expected, label):
    if response.status_code != expected:
        raise AssertionError(f'{label}: expected {expected}, got {response.status_code}')


def main():
    session = requests.Session()

    health = session.get(f'{BASE_URL}/healthz/', timeout=TIMEOUT)
    assert_status(health, 200, 'healthz')

    metrics = session.get(f'{BASE_URL}/metrics', timeout=TIMEOUT)
    assert_status(metrics, 200, 'metrics')
    if 'nufi_up 1' not in metrics.text:
        raise AssertionError('metrics: nufi_up metric is missing')

    landing = session.get(f'{BASE_URL}/', timeout=TIMEOUT)
    assert_status(landing, 200, 'landing')

    login_page = session.get(f'{BASE_URL}/login/', timeout=TIMEOUT)
    assert_status(login_page, 200, 'login page')

    dashboard_redirect = session.get(f'{BASE_URL}/dashboard/', allow_redirects=False, timeout=TIMEOUT)
    if dashboard_redirect.status_code not in {302, 301}:
        raise AssertionError(f'dashboard redirect: expected 301/302, got {dashboard_redirect.status_code}')

    if USERNAME and PASSWORD:
        token_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
        if not token_match:
            raise AssertionError('login page: CSRF token not found')

        login_response = session.post(
            f'{BASE_URL}/login/',
            data={
                'username': USERNAME,
                'password': PASSWORD,
                'csrfmiddlewaretoken': token_match.group(1),
            },
            headers={'Referer': f'{BASE_URL}/login/'},
            allow_redirects=False,
            timeout=TIMEOUT,
        )
        if login_response.status_code not in {301, 302}:
            raise AssertionError(f'login post: expected redirect, got {login_response.status_code}')

        for path in ['/dashboard/', '/income/', '/expenses/', '/budgets/', '/reports/']:
            response = session.get(f'{BASE_URL}{path}', timeout=TIMEOUT)
            assert_status(response, 200, path)

    print(f'Smoke test passed for {BASE_URL}')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Smoke test failed: {exc}', file=sys.stderr)
        raise
