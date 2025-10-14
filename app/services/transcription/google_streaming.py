"""
Google Cloud Speech-to-Text streaming utilities.

This module exposes a minimal interface to stream PCM16 audio to
Google Cloud Speech and yield interim/final transcripts.

Requirements:
- google-cloud-speech
- GOOGLE_APPLICATION_CREDENTIALS env var pointing to a service account JSON

Constraints:
- Accepts mono 16-bit PCM (LINEAR16) audio frames at a fixed sample rate.
"""
from __future__ import annotations

from typing import Iterator, Iterable, Optional
from queue import Queue, Empty
import threading

from google.cloud import speech_v1 as speech


class StreamingSTTClient:
    """Thin wrapper around Google streaming_recognize using queues for live audio."""

    def __init__(
        self,
        language_code: str = "en-US",
        sample_rate_hz: int = 16000,
        encoding: str = "LINEAR16",
        enable_automatic_punctuation: bool = True,
        model: Optional[str] = None,
    ) -> None:
        self.language_code = language_code
        self.sample_rate_hz = sample_rate_hz
        self.encoding = encoding
        self.enable_automatic_punctuation = enable_automatic_punctuation
        self.model = model
        self.client = speech.SpeechClient()

    def _request_generator(self, audio_queue: Queue, closed_event: threading.Event) -> Iterable[speech.StreamingRecognizeRequest]:
        config = speech.RecognitionConfig(
            encoding=getattr(speech.RecognitionConfig.AudioEncoding, self.encoding),
            sample_rate_hertz=self.sample_rate_hz,
            language_code=self.language_code,
            enable_automatic_punctuation=self.enable_automatic_punctuation,
            model=self.model or "latest_long",
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
            single_utterance=False,
        )
        # First request must contain the config
        yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)

        # Subsequent requests contain audio content
        while not (closed_event.is_set() and audio_queue.empty()):
            try:
                chunk = audio_queue.get(timeout=0.1)
            except Empty:
                continue
            if chunk is None:
                break
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    def stream(self, audio_iter: Iterator[bytes]) -> Iterator[dict]:
        """Stream audio chunks and yield transcript dicts: {text, is_final}.

        audio_iter: iterator of raw PCM16 bytes (mono) chunks
        """
        audio_queue: Queue = Queue(maxsize=100)
        closed_event = threading.Event()

        # Producer thread: feed audio into queue
        def producer() -> None:
            try:
                for chunk in audio_iter:
                    if not chunk:
                        continue
                    audio_queue.put(chunk)
            finally:
                closed_event.set()
                audio_queue.put(None)

        prod_thread = threading.Thread(target=producer, daemon=True)
        prod_thread.start()

        responses = self.client.streaming_recognize(self._request_generator(audio_queue, closed_event))

        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            yield {
                "text": result.alternatives[0].transcript,
                "is_final": bool(result.is_final),
            }



