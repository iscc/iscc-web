# -*- coding: utf-8 -*-
from httpx import codes
import iscc_core as ic


def test_explain_iscc(api):
    response = api.get(f"/explain/{ic.Code.rnd(ic.MT.ISCC, bits=256).code}")
    assert response.status_code == codes.OK
    assert response.json() == {
        "iscc": "ISCC:KMDMRJYGHHVRCZ5TM6U4G6D4MXA6LAXC4ZRPOKFU7JBEQXR2BJOS6NA",
        "decomposed": "AAA4RJYGHHVRCZ5T-CMAWPKODPB6GLQPF-GAAYFYXGML3SRNH2-IAAUESC6HIFF2LZU",
        "multiformat": "uzAFTBsinBjnrEWezZ6nDeHxlweWC4uZi9yi0-kJIXjoKXS80",
        "readable": (
            "ISCC-VIDEO-V0-MSDI-c8a70639eb1167b367a9c3787c65c1e582e2e662f728b4fa42485e3a0a5d2f34"
        ),
        "units": [
            {
                "iscc_unit": "ISCC:AAA4RJYGHHVRCZ5T",
                "hash_bits": "1100100010100111000001100011100111101011000100010110011110110011",
                "hash_hex": "c8a70639eb1167b3",
                "hash_uint": "14458531974522955699",
                "readable": "META-NONE-V0-64-c8a70639eb1167b3",
            },
            {
                "iscc_unit": "ISCC:CMAWPKODPB6GLQPF",
                "hash_bits": "0110011110101001110000110111100001111100011001011100000111100101",
                "hash_hex": "67a9c3787c65c1e5",
                "hash_uint": "7469716379221213669",
                "readable": "SEMANTIC-VIDEO-V0-64-67a9c3787c65c1e5",
            },
            {
                "iscc_unit": "ISCC:GAAYFYXGML3SRNH2",
                "hash_bits": "1000001011100010111001100110001011110111001010001011010011111010",
                "hash_hex": "82e2e662f728b4fa",
                "hash_uint": "9431353882395063546",
                "readable": "DATA-NONE-V0-64-82e2e662f728b4fa",
            },
            {
                "iscc_unit": "ISCC:IAAUESC6HIFF2LZU",
                "hash_bits": "0100001001001000010111100011101000001010010111010010111100110100",
                "hash_hex": "42485e3a0a5d2f34",
                "hash_uint": "4776171008201404212",
                "readable": "INSTANCE-NONE-V0-64-42485e3a0a5d2f34",
            },
        ],
    }
