import os
import requests
import streamlit as st
from typing import Any

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


def _headers() -> dict:
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _handle_response(response: requests.Response) -> dict | list | None:
    if response.status_code == 204:
        return None
    try:
        data = response.json()
    except Exception:
        response.raise_for_status()
        return None
    if response.status_code >= 400:
        detail = data.get("detail", "Terjadi kesalahan.")
        if isinstance(detail, list):
            messages = [f"{e.get('field', '')}: {e.get('message', '')}" for e in detail]
            raise APIError(response.status_code, " | ".join(messages))
        raise APIError(response.status_code, str(detail))
    return data


class APIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


def get(path: str, params: dict = None) -> Any:
    response = requests.get(f"{BASE_URL}{path}", params=params, headers=_headers(), timeout=10)
    return _handle_response(response)


def post(path: str, data: dict = None, files: dict = None) -> Any:
    if files:
        response = requests.post(f"{BASE_URL}{path}", files=files, data=data or {}, headers=_headers(), timeout=30)
    else:
        response = requests.post(f"{BASE_URL}{path}", json=data, headers=_headers(), timeout=10)
    return _handle_response(response)


def put(path: str, data: dict = None) -> Any:
    response = requests.put(f"{BASE_URL}{path}", json=data, headers=_headers(), timeout=10)
    return _handle_response(response)


def patch(path: str, data: dict = None) -> Any:
    response = requests.patch(f"{BASE_URL}{path}", json=data, headers=_headers(), timeout=10)
    return _handle_response(response)


def delete(path: str) -> None:
    response = requests.delete(f"{BASE_URL}{path}", headers=_headers(), timeout=10)
    _handle_response(response)