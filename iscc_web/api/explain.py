# -*- coding: utf-8 -*-
from blacksheep.server.controllers import ApiController, get
import iscc_core as ic


class Explain(ApiController):
    @classmethod
    def version(cls) -> str:
        return "v1"

    @get("{iscc}")
    def explain(self, iscc: str):
        """Decode ISCC"""
        try:
            norm = ic.iscc_normalize(iscc)
            ic.iscc_validate(norm)
        except Exception as e:
            return self.bad_request(f"Invalid ISCC - {e}")

        decomposed = ic.iscc_decompose(norm)
        code = ic.Code(norm)
        units = {}
        for unit in decomposed:
            uc = ic.Code(unit)
            units[uc.code] = {
                "readable": uc.explain,
                "hash_hex": uc.hash_hex,
                "hash_uint": str(uc.hash_uint),
                "hash_bits": uc.hash_bits,
            }
        return self.json(
            dict(
                iscc=norm,
                readable=code.explain,
                multiformats=code.mf_base64url,
                decomposed="-".join(decomposed),
                hash_bits=code.hash_bits,
                units=units,
            )
        )
