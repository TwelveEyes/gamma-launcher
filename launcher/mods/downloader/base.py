from os.path import basename
from pathlib import Path
from requests import Session
from tqdm import tqdm
from urllib.parse import urlparse

from launcher.hash import check_hash
from launcher.mods.archive import extract_archive

g_session = Session()
g_session.headers.update({'User-Agent': 'pyGammaLauncher'})


class DefaultDownloader:

    @property
    def archive(self) -> Path:
        if not self._archive:
            raise RuntimeError("archive not available, run download() first")

        return self._archive

    @property
    def url(self) -> str:
        return self._url

    def check(self, dl_dir: Path, update_cache: bool = False) -> None:
        return (dl_dir / basename(urlparse(self._url).path)).exists()

    def download(self, to: Path, use_cached=False, hash: str = None) -> Path:
        self._archive = self._archive or (to / basename(urlparse(self._url).path))

        if self._archive.exists() and use_cached:
            if not hash:
                return self._archive

            if check_hash(self._archive, hash):
                return self._archive

        with open(self._archive, "wb") as f, tqdm(
            desc=f"  - Downloading {self._archive.name}",
            unit="iB", unit_scale=True, unit_divisor=1024
        ) as progress:
            r = g_session.get(self._url, stream=True)
            for chunk in r.iter_content(chunk_size=1 * 1024 * 1024):
                if chunk:
                    progress.update(f.write(chunk))

        return self._archive

    def extract(self, to: Path, tmpdir: str = None) -> None:
        print(f'Extracting {self.archive}')
        extract_archive(self.archive, to)