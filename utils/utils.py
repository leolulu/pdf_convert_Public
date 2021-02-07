import requests
from retrying import retry
from typing import Mapping, Optional, Any
from typing_extensions import Literal


@retry(wait_fixed=10000, stop_max_attempt_number=60)
def requests_with_retry(url: str,
                        method: Literal['GET', 'POST'] = 'GET',
                        headers: Optional[Mapping] = None,
                        data: Optional[Mapping] = None,
                        params: Optional[Mapping] = None) -> Optional[requests.Response]:
    args: Mapping[str, Any] = {"url": url}
    if headers:
        args.update({"headers": headers})
    if data:
        args.update({"data": data})
    if params:
        args.update({"params": params})

    r = None
    if method == 'GET':
        r = requests.get(**args)
    if method == 'POST':
        r = requests.post(**args)
    return r
