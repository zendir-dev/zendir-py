# ---------------------------------------------------------------------------------------------------------------------------- #
# Copyright 2025 (c) Zendir, Pty Ltd. All Rights Reserved
# See the 'LICENSE' file at the root of this package
# ---------------------------------------------------------------------------------------------------------------------------- #
import aiohttp, json, typing
# ---------------------------------------------------------------------------------------------------------------------------- #

async def rqst(method: str, url: str, data: typing.Any = None, headers: dict = None) -> typing.Any:

    """
    Sends a HTTP request with the specified request and url and returns a response.
    """

    # parse HTTP request headers
    if headers and not isinstance(headers, dict):
        raise Exception("invalid argument 'headers'")

    # parse HTTP request content body
    content = None
    if data:
        if headers is None: headers = {}
        if isinstance(data, str):
            content = data.encode()
            headers["Content-Type"]   = "text/plain"
            headers["Content-Length"] = str(len(content))
        elif isinstance(data, (dict, list)):
            content = json.dumps(data).encode()
            headers["Content-Type"]   = "application/json"
            headers["Content-Length"] = str(len(content))
        else:
            raise Exception("invalid argument 'body'")

    # send HTTP request and wait for response
    results = {}
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, data=content, headers=headers) as response:
            results["body"]    = await response.read()
            results["status"]  = response.status
            results["headers"] = dict(response.headers)
    if results["status"] != 200:
        raise Exception(results["body"].decode() if results["body"] else "")
    if results["body"]:
        if "Content-Type" not in results["headers"]:
            raise Exception("missing 'Content-Type'")
        match results["headers"]["Content-Type"]:
            case "text/plain":
                return results["body"].decode()
            case "application/json":
                return json.loads(results["body"].decode())
    return None

# ---------------------------------------------------------------------------------------------------------------------------- #