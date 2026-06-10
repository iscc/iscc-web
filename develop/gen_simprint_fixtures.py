# -*- coding: utf-8 -*-
"""
Generate simprint test fixtures from iscc-search's reference implementation.

The POST /simprint endpoint promises byte-identical output to iscc-search's
`iscc_search.processing.text_simprints()`. This script runs the reference implementation on a
small text corpus and stores inputs and expected outputs in `tests/data/simprint_fixtures.json`.

Run it with the iscc-search virtualenv interpreter (iscc-sct must be installed there):

    cd C:/Users/titusz/Code/iscc/iscc-search
    .venv/Scripts/python.exe C:/Users/titusz/Code/iscc/iscc-web/develop/gen_simprint_fixtures.py
"""

import json
import pathlib

from iscc_search.processing import text_simprints


OUTPUT = pathlib.Path(__file__).parent.parent / "tests" / "data" / "simprint_fixtures.json"

SHORT = "Hello World! This is a short text for simprint generation."

MULTI_CHUNK = """Alice was beginning to get very tired of sitting by her sister on the bank, and
of having nothing to do: once or twice she had peeped into the book her sister was reading, but
it had no pictures or conversations in it, "and what is the use of a book," thought Alice,
"without pictures or conversations?"

So she was considering in her own mind (as well as she could, for the hot day made her feel very
sleepy and stupid), whether the pleasure of making a daisy-chain would be worth the trouble of
getting up and picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her.

There was nothing so very remarkable in that; nor did Alice think it so very much out of the way
to hear the Rabbit say to itself, "Oh dear! Oh dear! I shall be late!" (when she thought it over
afterwards, it occurred to her that she ought to have wondered at this, but at the time it all
seemed quite natural); but when the Rabbit actually took a watch out of its waistcoat-pocket, and
looked at it, and then hurried on, Alice started to her feet, for it flashed across her mind that
she had never before seen a rabbit with either a waistcoat-pocket, or a watch to take out of it,
and burning with curiosity, she ran across the field after it, and fortunately was just in time
to see it pop down a large rabbit-hole under the hedge.

In another moment down went Alice after it, never once considering how in the world she was to
get out again. The rabbit-hole went straight on like a tunnel for some way, and then dipped
suddenly down, so suddenly that Alice had not a moment to think about stopping herself before
she found herself falling down a very deep well.

Either the well was very deep, or she fell very slowly, for she had plenty of time as she went
down to look about her and to wonder what was going to happen next. First, she tried to look
down and make out what she was coming to, but it was too dark to see anything; then she looked
at the sides of the well, and noticed that they were filled with cupboards and book-shelves;
here and there she saw maps and pictures hung upon pegs. She took down a jar from one of the
shelves as she passed; it was labelled "ORANGE MARMALADE", but to her great disappointment it
was empty: she did not like to drop the jar for fear of killing somebody underneath, so managed
to put it into one of the cupboards as she fell past it.

"Well!" thought Alice to herself, "after such a fall as this, I shall think nothing of tumbling
down stairs! How brave they'll all think me at home! Why, I wouldn't say anything about it, even
if I fell off the top of the house!" (Which was very likely true.)

Down, down, down. Would the fall never come to an end? "I wonder how many miles I've fallen by
this time?" she said aloud. "I must be getting somewhere near the centre of the earth. Let me
see: that would be four thousand miles down, I think—" (for, you see, Alice had learnt several
things of this sort in her lessons in the schoolroom, and though this was not a very good
opportunity for showing off her knowledge, as there was no one to listen to her, still it was
good practice to say it over) "—yes, that's about the right distance—but then I wonder what
Latitude or Longitude I've got to?" (Alice had no idea what Latitude was, or Longitude either,
but thought they were nice grand words to say.)"""

MULTILINGUAL = """Der International Standard Content Code ist ein Identifikator für digitale
Medieninhalte. Er wird direkt aus dem Inhalt einer Datei berechnet und benötigt keine zentrale
Registrierungsstelle.

Le Code International Normalisé de Contenu est un identifiant pour les contenus médiatiques
numériques. Il est calculé directement à partir du contenu d'un fichier.

国际标准内容代码是数字媒体内容的标识符。它直接从文件内容计算得出，不需要中央注册机构。
内容代码由多个部分组成：元数据代码、内容代码、数据代码和实例代码。

Международный стандартный код контента — это идентификатор цифрового медиаконтента.
Он вычисляется непосредственно из содержимого файла и не требует центрального органа регистрации.

رمز المحتوى القياسي الدولي هو معرف لمحتوى الوسائط الرقمية. يتم حسابه مباشرة من محتوى الملف
ولا يتطلب سلطة تسجيل مركزية.

ISCCコードはデジタルメディアコンテンツの識別子です。ファイルの内容から直接計算され、
中央登録機関を必要としません。"""


def main():
    fixtures = {
        "short": SHORT,
        "multi_chunk": MULTI_CHUNK,
        "multilingual": MULTILINGUAL,
    }
    result = {name: {"text": text, "expected": text_simprints(text)} for name, text in fixtures.items()}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, data in result.items():
        counts = {key: len(values) for key, values in data["expected"].items()}
        print(f"{name}: {counts}")


if __name__ == "__main__":
    main()
