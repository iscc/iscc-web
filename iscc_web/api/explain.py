# -*- coding: utf-8 -*-
from blacksheep.server.controllers import APIController, get
import iscc_core as ic
from iscc_web.api.schema import IsccDetail, Unit


class Explain(APIController):
    @classmethod
    def version(cls) -> str:
        return "v1"

    @get("{iscc}")
    def explain(self, iscc: str):
        """Decode ISCC"""
        # iscc-core raises IndexError (instead of ValueError) for some composite codes with
        # invalid subtypes that pass `iscc_validate` (e.g. ISCC:KMUIV3NRGY).
        try:
            norm = ic.iscc_normalize(iscc)
            ic.iscc_validate(norm)
            decomposed = ic.iscc_decompose(norm)
            code = ic.Code(norm)
            units = []
            for unit in decomposed:
                uc = ic.Code(unit)
                units.append(
                    Unit(
                        iscc_unit=f"ISCC:{uc.code}",
                        readable=uc.explain,
                        hash_hex=uc.hash_hex,
                        hash_uint=str(uc.hash_uint),
                        hash_bits=uc.hash_bits,
                    )
                )
            result = IsccDetail()
            result.iscc = norm
            result.readable = code.explain
            result.multiformat = code.mf_base64url
            result.decomposed = "-".join(decomposed)
            result.units = units
        except (ValueError, IndexError) as e:
            return self.bad_request(f"Invalid ISCC - {e}")
        return result
