"""Generate the article's macros and family classification table from sealed counts."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared import ROOT, RESULT, read
from audit import audit


def main():
    audit()
    r = read(RESULT / "scores.json")
    original = read(RESULT / "upstream_control.json")
    lines = ["% Generated from experiments/second_family. Do not edit."]

    def macro(key, value):
        lines.append(r"\newcommand{\Second" + key + "}{" + str(value) + "}")

    macro("Matched", r["matched"])
    macro("Extras", r["event_extras"])
    macro("Native", r["summaries"]["native"]["correct"])
    macro("LagCount", r["summaries"]["lag"]["correct"])
    macro("CnnCount", r["summaries"]["cnn"]["correct"])
    macro("Missed", r["n"]-r["matched"])
    macro("Normal", r["quiet"]["test"]["alarms"])
    macro("QuietHours", f"{r['quiet']['test']['hours']:.2f}")
    macro("Upper", f"{r['quiet']['test']['upper95']:.2f}")
    macro("Cal", r["quiet"]["cal"]["alarms"])
    for suffix, contrast in (
        ("Pdf", "original_vs_cnn"),
        ("Lag", "lag_vs_cnn"),
        ("State", "carry_vs_reset"),
    ):
        item = r["paired"][contrast]
        macro(suffix + "Effect", f"{100 * item['difference']:.1f}")
        macro(suffix + "Lo", f"{100 * item['ci95'][0]:.1f}")
        macro(suffix + "Hi", f"{100 * item['ci95'][1]:.1f}")
        macro(suffix + "Wins", item["wins"])
        macro(suffix + "Losses", item["losses"])
        macro(suffix + "P", f"{item['p']:.3f}")
    macro("UpSP", original["counts"]["pred"]["correct"])
    macro("UpNS", original["counts"]["no"]["correct"])
    macro("UpN", original["counts"]["pred"]["n"])
    rows = []
    for k, label in (
        ("original", "Original source decision"),
        ("cnn", "CNN-F with subtraction"),
        ("cnn_no_sub", "CNN-F without subtraction"),
        ("lag", "Fixed-lag family estimate"),
        ("carry", "Merged histories, state carried"),
        ("reset", "Merged histories, state reset"),
    ):
        item = r["summaries"][k]
        classes = item["by_family"]
        rows.append(
            f"{label} & {classes['load']['load']}/18 & {classes['line']['line']}/18 & {item['correct']}/36"
        )
    macro("FamilyRows", (" " + r"\\" + "\n").join(rows) + r" \\")
    (ROOT / "generated/second_family.tex").write_text("\n".join(lines) + "\n", encoding="utf8")


if __name__ == "__main__":
    main()
