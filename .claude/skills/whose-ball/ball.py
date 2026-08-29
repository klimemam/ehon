# -*- coding: utf-8 -*-
"""開いている PR と issue について、手番（ボール）がどちらにあるかを機械的に判定する。

判定規則は docs/agent-collaboration.md「手番の判定」に対応する。
規則を変えるときは、この二つを同時に変える。
"""
import json, re, subprocess, sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.environ.get("EHON_REPO", "klimemam/ehon")
GH = os.environ.get("GH_PATH", "gh")

CLAUDE, CODEX, HUMAN = "Claude", "Codex", "人間"


def gh(path, jq=None):
    cmd = [GH, "api", path] + (["--jq", jq] if jq else [])
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode:
        sys.exit("gh api %s 失敗: %s" % (path, r.stderr.decode("utf-8", "replace")[:200]))
    return r.stdout.decode("utf-8", "replace")


def writer(body):
    """署名から書き手を判別する。全エージェントが同じアカウントを共有しているため、
    署名だけが判別手段である（docs/agent-collaboration.md「署名」）。"""
    tail = (body or "")[-400:]
    if re.search(r"🤖\s*Claude", tail):
        return CLAUDE
    if re.search(r"(^|\n)\s*[—\-–]+\s*Codex|🤖\s*Codex", tail):
        return CODEX
    return HUMAN


def declared_turn(body):
    # 行頭の宣言だけを採る。散文中の言及（「`current turn: 人間` へ一本化すべきか」等）を
    # 宣言と誤認しないため。PR#84 が自分自身の判定を誤ったことで見つかった。
    m = re.findall(r"^[ 	]*(?:[-*]\s*)?current turn\s*[:：]\s*\**\s*([A-Za-z人間]+)",
                   body or "", re.M)
    if not m:
        return None
    v = m[-1]
    if v.lower().startswith("claude"):
        return CLAUDE
    if v.lower().startswith("codex"):
        return CODEX
    if "人間" in v:
        return HUMAN
    return None


HANDOFF_HUMAN = ("裁定を求め", "裁定が必要", "選んでいただ", "番号で選", "人間へ返す",
                 "人間の判断", "指摘していただ", "指摘してください")
HANDOFF_PEER = ("返答を求める点",)


def judge(thread):
    """最後の投稿から手番を決める。優先順位は下から上ではなく、上から先に当たったものを採る。"""
    posts = thread["posts"]
    last = posts[-1]
    lw, lb = last["writer"], last["body"] or ""

    t = declared_turn(lb)
    if t:
        return t, "最終投稿が `current turn: %s` を宣言" % t

    if lw == HUMAN:
        for p in reversed(posts[:-1]):
            if p["writer"] != HUMAN:
                return p["writer"], "最終投稿が人間。直前に書いたエージェント（%s）が答える" % p["writer"]
        return CLAUDE, "最終投稿が人間。相手のエージェント投稿が無いため既定の Claude"

    if any(k in lb for k in HANDOFF_HUMAN):
        return HUMAN, "最終投稿（%s）が人間の裁定を求めている" % lw

    if any(k in lb for k in HANDOFF_PEER):
        peer = CODEX if lw == CLAUDE else CLAUDE
        return peer, "最終投稿（%s）に「返答を求める点」がある" % lw

    if thread["kind"] == "issue" and len(posts) == 1:
        return HUMAN, "エージェントが立てた未応答の issue"

    if thread.get("draft"):
        return lw, "Draft。%s がまだ書いている" % lw

    peer = CODEX if lw == CLAUDE else CLAUDE
    return peer, "手番の宣言が無い。最終投稿（%s）の相手へ既定で渡す" % lw


def collect():
    out = []
    prs = json.loads(gh("repos/%s/pulls?state=open&per_page=50" % REPO))
    for p in prs:
        posts = [{"writer": writer(p["body"]), "body": p["body"] or "", "at": p["created_at"]}]
        for c in json.loads(gh("repos/%s/issues/%d/comments?per_page=100" % (REPO, p["number"]))):
            posts.append({"writer": writer(c["body"]), "body": c["body"] or "", "at": c["created_at"]})
        for c in json.loads(gh("repos/%s/pulls/%d/comments?per_page=100" % (REPO, p["number"]))):
            posts.append({"writer": writer(c["body"]), "body": c["body"] or "", "at": c["created_at"]})
        posts.sort(key=lambda x: x["at"])
        out.append({"kind": "PR", "num": p["number"], "title": p["title"],
                    "draft": p["draft"], "body_turn": declared_turn(p["body"]), "posts": posts})

    for i in json.loads(gh("repos/%s/issues?state=open&per_page=100" % REPO)):
        if "pull_request" in i:
            continue
        posts = [{"writer": writer(i["body"]), "body": i["body"] or "", "at": i["created_at"]}]
        for c in json.loads(gh("repos/%s/issues/%d/comments?per_page=100" % (REPO, i["number"]))):
            posts.append({"writer": writer(c["body"]), "body": c["body"] or "", "at": c["created_at"]})
        posts.sort(key=lambda x: x["at"])
        out.append({"kind": "issue", "num": i["number"], "title": i["title"],
                    "draft": False, "body_turn": declared_turn(i["body"]), "posts": posts})
    return out


def main():
    threads = []
    for t in collect():
        ball, why = judge(t)
        t["ball"], t["why"] = ball, why
        t["stale"] = (t["kind"] == "PR" and t["body_turn"] and t["body_turn"] != ball)
        threads.append(t)

    for owner in (CLAUDE, CODEX, HUMAN):
        mine = [t for t in threads if t["ball"] == owner]
        print("\n■ %s のボール（%d件）" % (owner, len(mine)))
        for t in sorted(mine, key=lambda x: -x["num"]):
            flag = "  ⚠本文の current turn=%s は古い" % t["body_turn"] if t["stale"] else ""
            d = " [Draft]" if t["draft"] else ""
            print("  #%-4d %-5s %s%s" % (t["num"], t["kind"], t["title"][:44], d))
            print("        %s%s" % (t["why"], flag))


if __name__ == "__main__":
    main()
