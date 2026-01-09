"""Pixabay API client for Ambient Sounds integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

from .const import PIXABAY_API_BASE

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10


class PixabayClient:
    """Client for Pixabay API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        """Initialize the Pixabay client.
        
        Args:
            api_key: Pixabay API key
            session: aiohttp client session
        """
        self.api_key = api_key
        self.session = session

    async def search_audio(
        self, query: str, per_page: int = 20
    ) -> list[dict[str, Any]]:
        """Search for audio on Pixabay.
        
        Note: This uses the standard Pixabay API. Audio results may be limited.
        
        Args:
            query: Search query
            per_page: Number of results per page (min 3, max 200)
            
        Returns:
            List of audio results
        """
        # Pixabay requires per_page to be between 3 and 200
        per_page = max(3, min(200, per_page))
        # Use standard Pixabay API - note that audio may not be available in free tier
        url = f"{PIXABAY_API_BASE}?key={self.api_key}&q={query}&per_page={per_page}"
        
        try:
            async with async_timeout.timeout(TIMEOUT):
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("hits", [])
                    elif response.status == 400:
                        error_text = await response.text()
                        _LOGGER.error(
                            "Pixabay API bad request (400): %s. Please verify your API key is correct.",
                            error_text,
                        )
                        return []
                    else:
                        _LOGGER.error(
                            "Pixabay API error: %s - %s",
                            response.status,
                            await response.text(),
                        )
                        return []
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout connecting to Pixabay API")
            return []
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Pixabay API: %s", err)
            return []

    async def verify_api_key(self) -> bool:
        """Verify the API key is valid.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Test with a simple search (per_page must be 3 or more for Pixabay)
            url = f"{PIXABAY_API_BASE}?key={self.api_key}&q=test&per_page=3"
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
