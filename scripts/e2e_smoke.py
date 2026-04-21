#!/usr/bin/env python3
"""Minimal end-to-end smoke loop against local dev stack."""
from __future__ import annotations

import argparse
import sys
import time

import requests


def run_once(session: requests.Session, base_url: str, username: str, password: str) -> None:
    login = session.post(
        f"{base_url}/system/login/",
        json={"username": username, "password": password},
        timeout=20,
    )
    login.raise_for_status()
    body = login.json()
    token = body.get("access")
    if not token:
        raise RuntimeError(f"login response missing access token: {body}")

    session.headers.update({"Authorization": f"Bearer {token}"})

    me = session.get(f"{base_url}/system/me/", timeout=20)
    me.raise_for_status()
    me_body = me.json()
    if me_body.get("username") != username:
        raise RuntimeError(f"unexpected current user: {me_body}")

    dashboard = session.get(f"{base_url}/statistics/dashboard/", timeout=20)
    dashboard.raise_for_status()
    data = dashboard.json()
    if not isinstance(data, dict) or "data" not in data:
        raise RuntimeError(f"unexpected dashboard payload: {data}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run E2E smoke loop")
    parser.add_argument("--base-url", default="http://127.0.0.1:3000/api/v1")
    parser.add_argument("--username", default="demo_admin")
    parser.add_argument("--password", default="Limis@demo123")
    parser.add_argument("--loops", type=int, default=3)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()

    session = requests.Session()

    for i in range(1, args.loops + 1):
        try:
            run_once(session, args.base_url, args.username, args.password)
            print(f"loop {i}: PASS")
        except Exception as exc:  # noqa: BLE001
            print(f"loop {i}: FAIL - {exc}")
            return 1
        time.sleep(args.interval)

    print(f"all {args.loops} loops passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
