# -*- coding: utf-8 -*-
"""開いている PR と issue について、手番（ボール）がどちらにあるかを判定する。

判定規則の正本は rules.json である。この実装は規則の id を実装するだけで、
規則そのものを持たない。docs/agent-collaboration.md の表も rules.json から
生成する（--emit-doc / --check）。

  python ball.py            判定する
  python ball.py --check    rules.json と docs の表が一致するか検査する
  python ball.py --emit-doc docs 用の表を出力する
  python ball.py --test     fixtures.json で回帰検査する
"""
import json, re, subprocess, sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("EHON_REPO", "klimemam/ehon")
GH = os.environ.get("GH_PATH", "gh")
DOC = os.path.join(HERE, "..", "..", "..", "docs", "agent-collaboration.md")

CLAUDE, CODEX, HUMAN, UNKNOWN = "Claude", "Codex", "人間", "未判定"
RULES = json.load(open(os.path.join(HERE, "rules.json"), encoding="utf-8"))

# 行まるごとが宣言である場合だけ認識する。引用（>）とインラインコード内の
# 例示は宣言ではない。PR#84 が自分自身を誤判定したことで判明した境界である。
DECL = re.compile(r"^[ \t]*(?:[-*]\s*)?current turn\s*[:：]\s*\**\s*"
                  r"(Claude|Codex|人間)\b\**\s*(?:[（(].*?[）)])?\s*$",
                  re.M | re.I)


def gh(path):
    r = subprocess.run([GH, "api", path], capture_output=True)
    if r.returncode:
        sys.exit("gh api %s 失敗: %s" % (path, r.stderr.decode("utf-8", "replace")[:200]))
    return json.loads(r.stdout.decode("utf-8", "replace") or "[]")


def writer(body):
    """署名から書き手を判別する。全員が同じアカウントを共有しているため、
    署名だけが判別手段である。署名を落とすと人間の発言として数えられる。"""
    tail = (body or "")[-400:]
    if re.search(r"🤖\s*Claude", tail):
        return CLAUDE
    if re.search(r"(?m)^\s*[—\-–]+\s*Codex|🤖\s*Codex", tail):
        return CODEX
    return HUMAN


def declared_turn(body):
    m = DECL.findall(body or "")
    if not m:
        return None
    v = m[-1].lower()
    return CLAUDE if v.startswith("claude") else CODEX if v.startswith("codex") else HUMAN


def judge(thread):
    """rules.json の順に当てる。返り値は (手番, 規則id, 根拠)。"""
    posts, last = thread["posts"], thread["posts"][-1]
    lw, lb = last["writer"], last["body"] or ""
    peer = CODEX if lw == CLAUDE else CLAUDE

    t = declared_turn(lb)
    if t:
        return t, 1, "最終投稿が `current turn: %s` を宣言" % t

    if lw == HUMAN:
        for p in reversed(posts[:-1]):
            if p["writer"] != HUMAN:
                return p["writer"], 2, "最終投稿が人間。直前に書いたエージェント（%s）が答える" % p["writer"]
        return UNKNOWN, 0, "人間の投稿だけで、エージェントの投稿が一件も無い"

    if "返答を求める点" in lb:
        return peer, 3, "最終投稿（%s）に「返答を求める点」がある" % lw

    if thread["kind"] == "issue" and len(posts) == 1:
        return HUMAN, 4, "エージェントが立てたまま返答の無い issue"

    if thread.get("draft"):
        return lw, 5, "Draft。%s がまだ書いている" % lw

    return lw, 6, "宣言も「返答を求める点」も無い。手番は移らない（%s のまま）" % lw


def posts_of(kind, num, body, created):
    out = [{"writer": writer(body), "body": body or "", "at": created}]
    for c in gh("repos/%s/issues/%d/comments?per_page=100" % (REPO, num)):
        out.append({"writer": writer(c["body"]), "body": c["body"] or "", "at": c["created_at"]})
    if kind == "PR":
        for c in gh("repos/%s/pulls/%d/comments?per_page=100" % (REPO, num)):
            out.append({"writer": writer(c["body"]), "body": c["body"] or "", "at": c["created_at"]})
        # レビュー要約は上の二つに現れない。Codex はここに書くことがある。
        for r in gh("repos/%s/pulls/%d/reviews?per_page=100" % (REPO, num)):
            if (r.get("body") or "").strip():
                out.append({"writer": writer(r["body"]), "body": r["body"],
                            "at": r.get("submitted_at") or created})
    out.sort(key=lambda x: x["at"])
    return out


def collect():
    out = []
    for p in gh("repos/%s/pulls?state=open&per_page=50" % REPO):
        out.append({"kind": "PR", "num": p["number"], "title": p["title"], "draft": p["draft"],
                    "body_turn": declared_turn(p["body"]),
                    "posts": posts_of("PR", p["number"], p["body"], p["created_at"])})
    for i in gh("repos/%s/issues?state=open&per_page=100" % REPO):
        if "pull_request" in i:
            continue
        out.append({"kind": "issue", "num": i["number"], "title": i["title"], "draft": False,
                    "body_turn": declared_turn(i["body"]),
                    "posts": posts_of("issue", i["number"], i["body"], i["created_at"])})
    return out


def doc_table():
    rows = ["| # | 条件 | 手番 |", "| --- | --- | --- |"]
    for r in RULES["rules"]:
        rows.append("| %s | %s | %s |" % (r["id"] or "—", r["when"], r["turn"]))
    return "\n".join(rows)


def main():
    if "--emit-doc" in sys.argv:
        print(doc_table()); return
    if "--check" in sys.argv:
        doc = open(DOC, encoding="utf-8").read().replace(chr(13), "")
        ok = doc_table() in doc
        print("一致" if ok else "不一致：docs/agent-collaboration.md の表が rules.json と違う")
        sys.exit(0 if ok else 1)
    if "--test" in sys.argv:
        cases = json.load(open(os.path.join(HERE, "fixtures.json"), encoding="utf-8"))
        bad = 0
        for c in cases:
            for p in c["posts"]:
                p.setdefault("writer", writer(p["body"]))
            got, rid, _ = judge(c)
            if got != c["expect"] or rid != c["rule"]:
                bad += 1
                print("✗ %s: 期待 %s(規則%s) → 実際 %s(規則%s)" % (c["name"], c["expect"], c["rule"], got, rid))
            else:
                print("✓ %s → %s（規則%s）" % (c["name"], got, rid))
        print("\n%d件中 %d件失敗" % (len(cases), bad))
        sys.exit(1 if bad else 0)

    threads = []
    for t in collect():
        ball, rid, why = judge(t)
        t.update(ball=ball, rule=rid, why=why,
                 stale=(t["body_turn"] and t["body_turn"] != ball))
        threads.append(t)
    for owner in (CLAUDE, CODEX, HUMAN, UNKNOWN):
        mine = [t for t in threads if t["ball"] == owner]
        if not mine and owner == UNKNOWN:
            continue
        print("\n■ %s のボール（%d件）" % (owner, len(mine)))
        for t in sorted(mine, key=lambda x: -x["num"]):
            flag = "  ⚠本文の宣言（%s）は古い" % t["body_turn"] if t["stale"] else ""
            print("  #%-4d %-5s %s%s" % (t["num"], t["kind"], t["title"][:44], " [Draft]" if t["draft"] else ""))
            print("        規則%s：%s%s" % (t["rule"], t["why"], flag))


if __name__ == "__main__":
    main()
