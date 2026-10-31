"""Server-side Simli integration candidate; NOT enabled on the public tour.

Official contract: https://github.com/simliai/simli-client
The API key and custom approved face ID must be supplied on the server.
"""
import httpx

MAX_SESSION_SECONDS = 300


class AvatarUnavailable(RuntimeError):
    pass


async def mint_avatar_session(client: httpx.AsyncClient, *, api_key: str, face_id: str):
    if not api_key or not face_id:
        raise AvatarUnavailable('The approved ARIA avatar connection is not configured.')
    response = await client.post('https://api.simli.ai/compose/token',
        headers={'x-simli-api-key':api_key},
        json={
            'faceId':face_id,
            'maxSessionLength':MAX_SESSION_SECONDS,
            'maxIdleTime':MAX_SESSION_SECONDS,
            'handleSilence':True,
            'audioInputFormat':'pcm16',
            'streaming_width':1280,
            'streaming_height':720,
        }, timeout=20)
    if response.status_code == 402:
        raise AvatarUnavailable('The avatar service requires available allowance.')
    if response.status_code in (401,403):
        raise AvatarUnavailable('The avatar service has not authorized this custom ARIA avatar.')
    if response.status_code != 200:
        raise AvatarUnavailable('The avatar service could not start this session.')
    try:
        token = response.json()['session_token']
    except (ValueError,KeyError,TypeError):
        raise AvatarUnavailable('The avatar service returned an incomplete session.') from None
    if not isinstance(token,str) or not token:
        raise AvatarUnavailable('The avatar service returned an incomplete session.')
    return {'session_token':token,'max_session_seconds':MAX_SESSION_SECONDS}
