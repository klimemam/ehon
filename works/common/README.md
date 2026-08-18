# 作品横断文書の入口

`works/common/` は、複数作品にまたがる制作資料だけを置く。作品本文、単独作品の覚書・批評・関連資料は `works/<slug>/` に置く。

この文書が、`common/` の正本・状態・書き込み先を示す索引の正本である。作品の版管理と規約の正本は [`../README.md`](../README.md)、リポジトリ全体の協働規約は [`../../docs/agent-collaboration.md`](../../docs/agent-collaboration.md) である。

## 読む順

1. 制作の手順は [`battle.md`](battle.md) と [`method.md`](method.md)
2. 一冊の構成は [`kousei-rev1.md`](kousei-rev1.md) と [`collection/README.md`](collection/README.md)
3. 未制作の種は [`backlog/README.md`](backlog/README.md)
4. 先行研究・文脈は [`research/README.md`](research/README.md)
5. 過去の検算・改稿記録は [`history/README.md`](history/README.md)

## 分類と正本

| 分類 | 新しく書く場所 | 現行の正本・入口 |
| --- | --- | --- |
| active control / process | [`process/`](process/) | PR 手番は [`battle.md`](battle.md)、生成法は [`method.md`](method.md)、協働全般は [`../../docs/agent-collaboration.md`](../../docs/agent-collaboration.md) |
| collection architecture / maps | [`collection/`](collection/) | 構成案は [`kousei-rev1.md`](kousei-rev1.md)、地図は [`map.md`](map.md) と [`map-axes.md`](map-axes.md)、時系列は [`phases.md`](phases.md) |
| backlog / seeds | [`backlog/`](backlog/) | 母体は [`backlog.md`](backlog.md)、読者と概念の種は [`backlog-seeds.md`](backlog-seeds.md) |
| research / surveys | [`research/`](research/) | 系譜は [`positioning.md`](positioning.md)、寓話調査は [`survey-fables.md`](survey-fables.md)、目次調査は [`survey-toc.md`](survey-toc.md) |
| audit / history | [`history/`](history/) | 検算系列と改稿記録は [`history/README.md`](history/README.md) |

## 直下に残す文書

既存作品の版と批評から多数参照されている正本は、リンクを壊さないため直下に残す。これは未分類ではない。分類は上表と各入口が持つ。

- 制作：[`battle.md`](battle.md)、[`method.md`](method.md)
- 構成・地図：[`kousei-rev1.md`](kousei-rev1.md)、[`map.md`](map.md)、[`map-axes.md`](map-axes.md)、[`naming.md`](naming.md)、[`phases.md`](phases.md)、[`now-and-next.md`](now-and-next.md)、[`visual.md`](visual.md)
- 種の母体：[`backlog.md`](backlog.md)、[`backlog-seeds.md`](backlog-seeds.md)、[`backlog-agent-economy.md`](backlog-agent-economy.md)、[`backlog-rhyme.md`](backlog-rhyme.md)
- 調査：[`positioning.md`](positioning.md)、[`survey-fables.md`](survey-fables.md)、[`survey-toc.md`](survey-toc.md)
- 歴史的な被参照記録：[`critiques-fable-rules.md`](critiques-fable-rules.md)、[`critiques-audit-round2.md`](critiques-audit-round2.md)、[`critiques-audit-round3.md`](critiques-audit-round3.md)、[`critiques-audit-round4.md`](critiques-audit-round4.md)、[`revision-from-sol-collection-critique.md`](revision-from-sol-collection-critique.md)

直下へ新しい汎用 Markdown を追加しない。上の五分類のどこにも入らない場合にだけ、この索引へ未決として記録する。

## 状態の読み方

- **canonical / 正本**：同じ責務について最初に読む文書。
- **active / draft**：更新対象だが、採決・リリース済みとは限らない。
- **source / research**：主張や作品の材料。正本の代わりに使わない。
- **archive / history**：当時の観測・批評・判断の記録。誤りがあっても本文を消さず、後続文書から訂正する。

同じ話題が複数文書にある場合、本文を統合して削除するのではなく、各分類の `README.md` で正本と履歴を宣言する。
