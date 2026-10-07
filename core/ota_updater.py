import aiohttp
import logging
from typing import Optional

class OTAUpdater:
    """
    Checks GitHub Releases for updates and orchestrates background patching.
    """
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.logger = logging.getLogger("OTAUpdater")

    async def check_for_updates(self, current_version: str) -> Optional[str]:
        # Using GitHub Releases API
        api_url = f"https://api.github.com/repos/{self.repo_url}/releases/latest"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    latest_version = data.get("tag_name")
                    if latest_version > current_version:
                        return data.get("assets", [{}])[0].get("browser_download_url")
        return None
