# -*- coding: utf-8 -*-
"""Plaintext simprint endpoint - generates granular fingerprints compatible with iscc-search."""

import asyncio
import iscc_core as ic
import iscc_sct as sct
import xxhash
from blacksheep.server.controllers import APIController, post
from loguru import logger as log
from iscc_web.api.pool import Pool
from iscc_web.options import opts
from iscc_web.api.schema import SimprintRequest


def text_chunks(text, avg_size=512):
    # type: (str, int) -> Generator[str, None, None]
    """
    Generate variable-sized text chunks using content-defined chunking.

    :param text: Input text to chunk
    :param avg_size: Target average chunk size in characters (default: 512)
    :yields: Text chunks
    """
    data = text.encode("utf-32-be")
    avg_size_bytes = avg_size * 4  # 4 bytes per character in utf-32-be
    for chunk_bytes in ic.alg_cdc_chunks(data, utf32=True, avg_chunk_size=avg_size_bytes):
        yield chunk_bytes.decode("utf-32-be")


def text_simprints(text, avg_chunk_size=512, ngram_size=13):
    # type: (str, int, int) -> dict[str, list[str]]
    """
    Generate simprints from plain text (top-level function - pool workers must pickle it).

    Output is bit-identical to iscc-search's `text_simprints`: CONTENT_TEXT_V0 simprints via
    minhash over character n-grams per CDC chunk, SEMANTIC_TEXT_V0 simprints via iscc-sct.

    :param text: Plain text input
    :param avg_chunk_size: Target average chunk size in characters (default: 512)
    :param ngram_size: Size of character n-grams for feature extraction (default: 13)
    :return: Dictionary mapping simprint types to lists of base64-encoded simprints
    """
    result = {}

    # Generate CONTENT_TEXT_V0 simprints
    cleaned_text = ic.text_clean(text)
    content_simprints = []
    for chunk in text_chunks(cleaned_text, avg_size=avg_chunk_size):
        # Generate n-grams from collapsed/normalized text
        ngrams = ("".join(chars) for chars in ic.sliding_window(ic.text_collapse(chunk), ngram_size))
        # Hash each n-gram
        features = [xxhash.xxh32_intdigest(s.encode("utf-8")) for s in ngrams]
        # Apply minhash to create similarity-preserving fingerprint
        minimum_hash_digest = ic.alg_minhash_256(features)
        # Encode as base64 simprint
        content_simprints.append(ic.encode_base64(minimum_hash_digest))

    result["CONTENT_TEXT_V0"] = content_simprints

    # Generate SEMANTIC_TEXT_V0 simprints
    semantic_result = sct.gen_text_code_semantic(text, simprints=True, bits_granular=256)
    if semantic_result.get("features") and len(semantic_result["features"]) > 0:
        semantic_simprints = semantic_result["features"][0].get("simprints", [])
        if semantic_simprints:
            result["SEMANTIC_TEXT_V0"] = semantic_simprints

    return result


class Simprint(APIController):
    @classmethod
    def version(cls) -> str:
        return "v1"

    @post()
    async def create_simprint(self, query: SimprintRequest, pool: Pool):
        """Create granular simprints from plain text."""
        if len(query.text.encode("utf-8")) > opts.max_upload_size:
            return self.status_code(400, f"Bad Request - text size must be <= {opts.max_upload_size} bytes")

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(pool, text_simprints, query.text)
        except Exception:
            # Exception details may contain server paths (e.g. model file locations).
            log.exception("Simprint processing failed")
            return self.status_code(422, "Unprocessable Entity - simprint processing error.")

        return self.json(result)
