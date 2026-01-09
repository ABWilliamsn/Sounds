"""Freesound API client for Ambient Sounds integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import quote

import aiohttp
import async_timeout

from .const import FREESOUND_API_BASE

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10


class FreesoundClient:
    """Client for Freesound API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        """Initialize the Freesound client.
        
        Args:
            api_key: Freesound API key
            session: aiohttp client session
        """
        self.api_key = api_key
        self.session = session

    async def search_audio(
        self, query: str, per_page: int = 20
    ) -> list[dict[str, Any]]:
        """Search for audio on Freesound.
        
        Args:
            query: Search query
            per_page: Number of results per page (max 150)
            
        Returns:
            List of audio results with direct download URLs
        """
        # Freesound allows up to 150 results per page
        per_page = max(1, min(150, per_page))
        
        # Build search URL with fields we need
        # Using search endpoint with filters for ambient sounds
        encoded_query = quote(query)
        url = (
            f"{FREESOUND_API_BASE}/search/text/"
            f"?query={encoded_query}"
            f"&page_size={per_page}"
            f"&fields=id,name,tags,duration,previews,username"
            f"&token={self.api_key}"
        )
        
        try:
            async with async_timeout.timeout(TIMEOUT):
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])
                        
                        # Transform results to match our expected format
                        transformed_results = []
                        for sound in results:
                            # Get the preview URL (high quality MP3)
                            previews = sound.get("previews", {})
                            preview_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
                            
                            # Validate that preview URL is from Freesound domain for security
                            if preview_url and preview_url.startswith("https://cdn.freesound.org/"):
                                transformed_results.append({
                                    "id": sound.get("id"),
                                    "name": sound.get("name", "Unknown"),
                                    "tags": ", ".join(sound.get("tags", [])),
                                    "duration": int(sound.get("duration", 0)),
                                    "preview_url": preview_url,
                                    "username": sound.get("username", "Unknown"),
                                })
                        
                        return transformed_results
                    elif response.status == 401:
                        _LOGGER.error("Freesound API authentication failed. Please check your API key.")
                        return []
                    elif response.status == 400:
                        error_text = await response.text()
                        _LOGGER.error(
                            "Freesound API bad request (400): %s",
                            error_text,
                        )
                        return []
                    else:
                        _LOGGER.error(
                            "Freesound API error: %s - %s",
                            response.status,
                            await response.text(),
                        )
                        return []
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout connecting to Freesound API")
            return []
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Freesound API: %s", err)
            return []

    async def verify_api_key(self) -> bool:
        """Verify the API key is valid.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Test with a simple search
            url = f"{FREESOUND_API_BASE}/search/text/?query=test&page_size=1&token={self.api_key}"
            async with async_timeout.timeout(TIMEOUT):
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_text = await response.text()
                        _LOGGER.error(
                            "API key verification failed with status %s: %s",
                            response.status,
                            error_text,
                        )
                        return False
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout during API key verification")
            return False
        except aiohttp.ClientError as err:
            _LOGGER.error("Error during API key verification: %s", err)
            return False
