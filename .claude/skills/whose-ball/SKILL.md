---
name: whose-ball
description: ehon リポジトリで手番（ボール）が Claude・Codex・人間のどれにあるかを判定する。「どっちのボール？」「どう？」「進捗は？」「何が止まってる？」と聞かれたとき、開いている PR と issue を全部走査して、スレッドごとに手番と根拠を出す。GitHub 上で複数エージェントが PR を介して協働していて、手番の所在が曖昧になったときに使う。
---

# 手番（ボール）の判定

## なぜ機械判定するか

Claude・Codex・人間が**同じ GitHub アカウントを共有**しているため、投稿者名では書き手が分からない。手番は PR ごと・issue ごとに独立していて、二十件を超えると記憶では追えない。実測（2026-08-23）では、開いていた 4 本の PR の 4 本すべてで PR 本文の `current turn` が実際の手番と食い違っていた。

## 使い方

```bash
GH_PATH="C:/Program Files/GitHub CLI/gh.exe" python .claude/skills/whose-ball/ball.py
python .claude/skills/whose-ball/ball.py --check   # docs の表が正本と一致するか
python .claude/skills/whose-ball/ball.py --test    # 回帰検査（凍結データ）
```

出力は Claude／Codex／人間／未判定に分けた一覧で、各行に**適用された規則の番号と根拠**が付く。

## 規則の正本

**規則は [`rules.json`](rules.json) にだけ書く。** この SKILL.md には複製しない。

- `rules.json` の配列の**並びが判定順**である。`ball.py` は id ごとの条件だけを持ち、適用順は配列を反復して決める
- `docs/agent-collaboration.md` の表は `rules.json` から生成し、開始・終了マーカーで囲む。`--check` は、マーカーがちょうど一組・範囲内が正本と完全一致・範囲外に規則行が無い、の三つを検査する
- 規則を変えるときは `rules.json` を変え、`--emit-doc` で表を生成し直し、`fixtures.json` に回帰事例を足し、`--check` と `--test` を通す

## 書き手の判別

署名だけが判別手段である。投稿末尾 400 字に `🤖 Claude` なら Claude、行頭の `— Codex` か `🤖 Codex` なら Codex、どちらも無ければ人間。**署名を落とすと人間の発言として数えられ、手番が誤って動く。**

## 手番を渡すとき

投稿の中に**行まるごとの宣言**を置く。

```
current turn: **Codex**
```

引用行（`>`）とインラインコード内の言及は宣言ではない。宣言も「返答を求める点」も無い投稿は情報提供で、手番は移らない。

## 回帰検査

`fixtures.json` は**凍結した投稿列**である。実データを期待値に使わない——会話が進むと期待値のほうが動く。`--test` は判定と `--check` 自体の両方を検査する。

## 判定できないもの

手番が誰にあるかしか答えない。相手の指摘が正しいか、受け入れるか差し戻すか、着手の順序は、判定の外にある（`works/common/battle.md`）。
