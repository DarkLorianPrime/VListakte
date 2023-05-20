import typing

from httpx import Client, Response, ConnectError
from httpx._client import UseClientDefault, USE_CLIENT_DEFAULT
from httpx._types import URLTypes, RequestContent, RequestData, RequestFiles, QueryParamTypes, HeaderTypes, CookieTypes, \
    AuthTypes, TimeoutTypes, RequestExtensions


class CustomClient(Client):
    def post(
            self,
            url: URLTypes,
            *,
            content: typing.Optional[RequestContent] = None,
            data: typing.Optional[RequestData] = None,
            files: typing.Optional[RequestFiles] = None,
            json: typing.Optional[typing.Any] = None,
            params: typing.Optional[QueryParamTypes] = None,
            headers: typing.Optional[HeaderTypes] = None,
            cookies: typing.Optional[CookieTypes] = None,
            auth: typing.Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
            follow_redirects: typing.Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
            timeout: typing.Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
            extensions: typing.Optional[RequestExtensions] = None,
    ) -> typing.Self | Response:
        try:
            result = super().post(url,
                                  content=content,
                                  data=data,
                                  files=files,
                                  json=json,
                                  params=params,
                                  headers=headers,
                                  cookies=cookies,
                                  auth=auth,
                                  follow_redirects=follow_redirects,
                                  timeout=timeout,
                                  extensions=extensions
                                  )
        except ConnectError:
            return self
        return result

    def get(
            self,
            url: URLTypes,
            *,
            params: typing.Optional[QueryParamTypes] = None,
            headers: typing.Optional[HeaderTypes] = None,
            cookies: typing.Optional[CookieTypes] = None,
            auth: typing.Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
            follow_redirects: typing.Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
            timeout: typing.Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
            extensions: typing.Optional[RequestExtensions] = None,
    ) -> typing.Self | Response:
        try:
            result = super().post(url,
                                  params=params,
                                  headers=headers,
                                  cookies=cookies,
                                  auth=auth,
                                  follow_redirects=follow_redirects,
                                  timeout=timeout,
                                  extensions=extensions
                                  )
        except ConnectError:
            return self
        return result
