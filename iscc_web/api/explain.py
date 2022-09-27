# -*- coding: utf-8 -*-
from blacksheep.server.controllers import ApiController, get
import iscc_core as ic
from iscc_web.api.schema import IsccDetail, Unit


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
        # TODO remove IndexError with next iscc-core release
        except (ValueError, IndexError) as e:
            return self.bad_request(f"Invalid ISCC - {e}")

        result = IsccDetail()
        decomposed = ic.iscc_decompose(norm)
        code = ic.Code(norm)
        units = []
        for unit in decomposed:
            uc = ic.Code(unit)
            # TODO should be caught by `iscc_validate` - fix in iscc-core lib (ISCC:CE22222222)
            try:
                readable = uc.explain
            except ValueError as e:
                return self.bad_request(f"Invalid ISCC - {e}")
            unit = Unit(
                iscc_unit=f"ISCC:{uc.code}",
                readable=readable,
                hash_hex=uc.hash_hex,
                hash_uint=str(uc.hash_uint),
                hash_bits=uc.hash_bits,
            )
            units.append(unit)

        result.iscc = norm
        result.readable = code.explain
        result.multiformat = code.mf_base64url
        result.decomposed = "-".join(decomposed)
        result.units = units
        return result
