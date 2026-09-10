#!/usr/bin/env python3
"""Переписывает тексты сайта на английский.

Регистр — брэдбериевский: конкретная чувственная деталь вместо
абстракции, вещи ведут себя как живые, простые слова в неожиданных
сочетаниях, короткая фраза рядом с длинной.
"""
import json
from pathlib import Path

SEL = Path.home() / "Downloads" / "works-site" / "_select"

MANIFEST = (
    "I do not paint these. I say them aloud into the dark and wait to see "
    "what walks back out. Nothing returns the way I sent it. I keep the ones "
    "where the mistake came back truer than the wish."
)

TEXTS = {
    "VELOCITY": {
        "lead": "Speed, caught after it already happened. A motorcycle, a car, "
                "a woman — three things advertising has always promised in the "
                "same voice. Not one engine here is running.",
        "notes": [
            "A race with no rival and no finish line.",
            "The hurry lives in how they hold themselves. A held breath is "
            "louder than a shout.",
        ],
    },
    "BODY": {
        "lead": "The body up close, before it turns back into a person. Come "
                "near enough and skin forgets whose it was. What is left is "
                "weather, happening on a surface.",
        "notes": [
            "The polaroid lies about the film. It tells the truth about the "
            "distance.",
            "The closer you stand, the less person there is, and the more world.",
        ],
    },
    "KISSING": {
        "lead": "Forty-one attempts at one small motion. A kiss hides both "
                "faces and shows only the second when two people stopped "
                "arguing with the air between them.",
        "notes": [
            "The same instant, lived forty-one different ways.",
            "The light always comes from the side. Head-on, you would see "
            "nothing of what is happening between.",
        ],
    },
    "ORGANISM": {
        "lead": "Close enough that scale gives out. A copper pipe, a mouth, a "
                "flower, the inside of a machine — at this range they stop "
                "being separate things. Get near enough to anything and it "
                "begins to breathe.",
        "notes": [
            "You cannot tell whether this was born or assembled.",
            "A needle trembles inside something that is clearly alive, and "
            "keeps reading a number anyway.",
        ],
    },
    "THRONE": {
        "lead": "An old woman on a throne, lit like a perfume campaign. Fashion "
                "will sell anything, including the thing it usually turns its "
                "face away from.",
        "notes": [
            "Thirty portraits of one power, and it never once blinks.",
            "The red here is not blood and not luxury. The red here is "
            "temperature.",
        ],
    },
    "MYTH": {
        "lead": "Many arms, many heads. Old ways of drawing power, rebuilt by a "
                "machine that has never knelt in a temple. It gets the gods "
                "wrong, and the wrongness is the interesting part.",
        "notes": [
            "Shiva, totem, iconostasis — all of them ask the same question: "
            "how much more of a man should there be than there is.",
            "It does not know the canon, so it is not afraid to break it.",
        ],
    },
    "RITUAL": {
        "lead": "A dancer at the end of his strength. A rite and a warehouse "
                "party are the same motion; only the audience changes.",
        "notes": [
            "Warehouse, bonfire, stage — the floor makes no difference.",
            "Nobody here is dancing to be watched. You are in the room by "
            "accident.",
        ],
    },
    "CITY": {
        "lead": "Cities with no name and nobody in them. Architecture "
                "photographed the way you would photograph a face — same "
                "distance, same patience.",
        "notes": [
            "At night a city shows its bones instead of its skin.",
            "Concrete outlasts whatever it was poured for.",
        ],
    },
    "TATTOO": {
        "lead": "The master, and the work being done on skin. The darkest set "
                "here — almost no light in it, and that is not an error of "
                "exposure.",
        "notes": [
            "A drawing on a body is the only picture that grows old alongside "
            "the one who carries it.",
        ],
    },
    "BRAND": {
        "lead": "Advertising with the product taken out. What remains is the "
                "method alone: light, colour, a promise, and nothing you can "
                "buy.",
        "notes": [
            "Yellow, oil, plastic — the three materials that have always been "
            "made to mean new.",
        ],
    },
    "CREATURE": {
        "lead": "Beings whose anatomy refuses to add up. The machine has no "
                "idea how many of anything there ought to be, and now and then "
                "it is wrong beautifully.",
        "notes": [
            "An error becomes a species if you repeat it with enough "
            "conviction.",
        ],
    },
}

notes = json.loads((SEL / "notes.json").read_text())
for nm, t in TEXTS.items():
    if nm not in notes:
        continue
    notes[nm]["lead"] = t["lead"]
    notes[nm]["notes"] = list(t["notes"])
notes["_manifest"] = MANIFEST

(SEL / "notes.json").write_text(json.dumps(notes, ensure_ascii=False, indent=1))
print(f"переписано: манифест + {len(TEXTS)} заявлений")
print(f"вставок между работами: {sum(len(t['notes']) for t in TEXTS.values())}")
