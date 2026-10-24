"""Read a public ZIP through validated HTTP byte ranges, without a full download."""
import io
import urllib.request


class HttpRangeReader(io.RawIOBase):
    def __init__(self, url, size):
        self.url, self.size, self.position, self.transferred = url, size, 0, 0

    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.position

    def seek(self, offset, whence=0):
        position = offset if whence == 0 else self.position + offset if whence == 1 else self.size + offset
        if whence not in (0, 1, 2) or position < 0:
            raise ValueError('Invalid ZIP seek.')
        self.position = position
        return position

    def read(self, size=-1):
        size = min(self.size - self.position, size if size >= 0 else self.size)
        if size <= 0: return b''
        if size > 32 * 1024 * 1024:
            raise ValueError('Requested ZIP range exceeds 32 MiB.')
        start = self.position
        request = urllib.request.Request(self.url, headers={'Range': f'bytes={start}-{start + size - 1}'})
        with urllib.request.urlopen(request, timeout=90) as response:
            expected = f'bytes {start}-{start + size - 1}/{self.size}'
            if response.status != 206 or response.headers.get('Content-Range') != expected:
                raise ValueError('Server did not honor the exact ZIP byte range.')
            data = response.read(size)
        if len(data) != size:
            raise ValueError('Truncated ZIP byte range.')
        self.position += size
        self.transferred += size
        return data
