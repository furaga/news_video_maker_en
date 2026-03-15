"""edge-tts English TTS client"""
import asyncio
import logging
from pathlib import Path

import edge_tts

from news_video_maker.config import AUDIO_DIR, TTS_VOICE

logger = logging.getLogger(__name__)


async def _synthesize_async(text: str, output_path: Path, voice: str, rate: str) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(output_path))
    logger.info("TTS complete: %s", output_path)
    return output_path


def synthesize(text: str, output_path: Path, voice: str = TTS_VOICE, rate: str = "+15%") -> Path:
    """Synthesize English text to an MP3 file using edge-tts."""
    return asyncio.run(_synthesize_async(text, output_path, voice, rate))
