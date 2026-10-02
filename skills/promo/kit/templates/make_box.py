# Generates the feed (4:5) and square (1:1) projects from box.template.html.
import os
FORMATS = {
    "feed":   dict(W=1080, H=1350, TITLE="Feed 4:5", PHONE_W=460, PHONE_TOP=190, SIDE_LEFT=610, SIDE_HEAD=70,
                   PROOF_HEAD_TOP=90, PROOF_HEAD=72, PAIR_TOP=330, CARD_H=700, FOOT_BOTTOM=50, SCRIM_TOP=880, CAP_TOP=1090),
    "square": dict(W=1080, H=1080, TITLE="Square 1:1", PHONE_W=380, PHONE_TOP=140, SIDE_LEFT=540, SIDE_HEAD=60,
                   PROOF_HEAD_TOP=60, PROOF_HEAD=60, PAIR_TOP=230, CARD_H=720, FOOT_BOTTOM=40, SCRIM_TOP=640, CAP_TOP=830),
}
tpl = open("box.template.html").read()
for name, v in FORMATS.items():
    html = tpl.replace("{{ID}}", name)
    for k, val in v.items():
        html = html.replace("{{%s}}" % k, str(val))
    assert "{{" not in html, name
    os.makedirs(name, exist_ok=True)
    open(f"{name}/index.html", "w").write(html)
    for link in ("assets", "kit"):
        if not os.path.lexists(f"{name}/{link}"):
            os.symlink(f"../shared/{link}", f"{name}/{link}")
    for f in ("hyperframes.json", "meta.json"):
        open(f"{name}/{f}", "w").write(open(f).read())
    print("wrote", name)
