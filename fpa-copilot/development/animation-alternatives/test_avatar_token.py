import unittest
import json
import httpx
from avatar_token import mint_avatar_session, AvatarUnavailable


class AvatarTokenTests(unittest.IsolatedAsyncioTestCase):
    async def test_provider_enforces_five_minute_limit_and_key_stays_server_side(self):
        def handler(request):
            body=json.loads(request.content)
            self.assertEqual(str(request.url),'https://api.simli.ai/compose/token')
            self.assertEqual(body['maxSessionLength'],300)
            self.assertEqual(body['maxIdleTime'],300)
            self.assertEqual(body['audioInputFormat'],'pcm16')
            self.assertEqual(body['faceId'],'approved-test-face')
            self.assertNotIn('api_key',body)
            self.assertEqual(request.headers['x-simli-api-key'],'test-key-not-real')
            return httpx.Response(200,json={'session_token':'temporary-test-token','unrelated_secret':'do-not-return'})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result=await mint_avatar_session(client,api_key='test-key-not-real',face_id='approved-test-face')
        self.assertEqual(result,{'session_token':'temporary-test-token','max_session_seconds':300})

    async def test_missing_identity_does_not_fall_back_to_stock_face(self):
        def handler(request):
            self.fail('No request should occur before the approved identity is configured')
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with self.assertRaises(AvatarUnavailable):
                await mint_avatar_session(client,api_key='test-key-not-real',face_id='')

    async def test_failed_service_does_not_leak_upstream_error_or_secret(self):
        for status in (401,402,403,429,500):
            async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request:httpx.Response(status,text='secret-debug-data'))) as client:
                with self.assertRaises(AvatarUnavailable) as e:
                    await mint_avatar_session(client,api_key='test-key-not-real',face_id='approved-test-face')
                self.assertNotIn('secret-debug-data',str(e.exception))

    async def test_malformed_success_is_not_reported_as_working_avatar(self):
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request:httpx.Response(200,json={}))) as client:
            with self.assertRaises(AvatarUnavailable):
                await mint_avatar_session(client,api_key='test-key-not-real',face_id='approved-test-face')


if __name__=='__main__':unittest.main()
