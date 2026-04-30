from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from jose import ExpiredSignatureError

from src.auth.utils import create_jwt

# ── /auth/request-link ────────────────────────────────────────────────────────


async def test_request_link_ok(client: AsyncClient, mock_member: SimpleNamespace) -> None:
    with (
        patch('src.auth.service.get_member_by_email', new_callable=AsyncMock, return_value=mock_member),
        patch('src.auth.service.send_magic_link', new_callable=AsyncMock),
    ):
        response = await client.post('/auth/request-link', json={'email': 'alice@family.example'})
    assert response.status_code == 200
    assert 'detail' in response.json()


async def test_request_link_unknown_email(client: AsyncClient) -> None:
    with patch('src.auth.service.get_member_by_email', new_callable=AsyncMock, return_value=None):
        response = await client.post('/auth/request-link', json={'email': 'stranger@outside.com'})
    assert response.status_code == 400
    assert response.json()['detail'] == 'EMAIL_NOT_ALLOWED'


async def test_request_link_invalid_email_format(client: AsyncClient) -> None:
    response = await client.post('/auth/request-link', json={'email': 'not-an-email'})
    assert response.status_code == 422


# ── /auth/callback ────────────────────────────────────────────────────────────


async def test_callback_ok(client: AsyncClient, mock_member: SimpleNamespace) -> None:
    with (
        patch('src.auth.router.decode_magic_token', return_value='alice@family.example'),
        patch('src.auth.service.get_member_by_email', new_callable=AsyncMock, return_value=mock_member),
    ):
        response = await client.get('/auth/callback', params={'token': 'valid-token'}, follow_redirects=False)
    assert response.status_code == 302
    assert 'access_token' in response.cookies or 'set-cookie' in response.headers


async def test_callback_invalid_token(client: AsyncClient) -> None:
    from jose import JWTError

    with patch('src.auth.router.decode_magic_token', side_effect=JWTError('bad')):
        response = await client.get('/auth/callback', params={'token': 'garbage'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'INVALID_TOKEN'


async def test_callback_expired_token(client: AsyncClient) -> None:
    with patch('src.auth.router.decode_magic_token', side_effect=ExpiredSignatureError('expired')):
        response = await client.get('/auth/callback', params={'token': 'old-token'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'TOKEN_EXPIRED'


async def test_callback_email_not_in_db(client: AsyncClient) -> None:
    with (
        patch('src.auth.router.decode_magic_token', return_value='ghost@outside.com'),
        patch('src.auth.service.get_member_by_email', new_callable=AsyncMock, return_value=None),
    ):
        response = await client.get('/auth/callback', params={'token': 'valid-token'})
    assert response.status_code == 401


# ── /auth/me ──────────────────────────────────────────────────────────────────


async def test_me_authenticated(client: AsyncClient, mock_member: SimpleNamespace) -> None:
    jwt_token = create_jwt(str(mock_member.id), mock_member.email)
    with patch('src.members.service.get_by_id', new_callable=AsyncMock, return_value=mock_member):
        response = await client.get('/auth/me', cookies={'access_token': jwt_token})
    assert response.status_code == 200
    assert response.json()['first_name'] == mock_member.first_name
    assert response.json()['email'] == mock_member.email


async def test_me_no_cookie(client: AsyncClient) -> None:
    response = await client.get('/auth/me')
    assert response.status_code == 401
    assert response.json()['detail'] == 'NOT_AUTHENTICATED'


async def test_me_invalid_cookie(client: AsyncClient) -> None:
    response = await client.get('/auth/me', cookies={'access_token': 'garbage.jwt.value'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'INVALID_TOKEN'


async def test_me_member_deleted(client: AsyncClient, mock_member: SimpleNamespace) -> None:
    jwt_token = create_jwt(str(mock_member.id), mock_member.email)
    with patch('src.members.service.get_by_id', new_callable=AsyncMock, return_value=None):
        response = await client.get('/auth/me', cookies={'access_token': jwt_token})
    assert response.status_code == 401


# ── /auth/logout ──────────────────────────────────────────────────────────────


async def test_logout(client: AsyncClient) -> None:
    response = await client.post('/auth/logout')
    assert response.status_code == 204
    # Cookie should be cleared (set with empty value or max-age=0)
    set_cookie = response.headers.get('set-cookie', '')
    assert 'access_token' in set_cookie
