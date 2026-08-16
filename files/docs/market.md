# エージェント経済の構造

出発点は「AIが財布を持ったら」。行き着いたのは「AI時代の市場をどう設計するか」。

> **出典**：別スレッドの議論をまとめたもの。以下 1〜16 は当該議論の記録であり、17 以降が本リポジトリの主張との突き合わせ。

---

## 1. 出発点は「AIが財布を持つ」ことではない

本質は、AI自身の財布よりも、**人間がAIに、目的・予算・制約・裁量を委譲する**こと。

```
目的: 競合調査を終える
予算: 5,000円
制約: 個人情報を外部送信しない
裁量: 500円以下は自動決済
```

こう仕事を渡すと、AIは検索、GPU、専門API、別のAgent、人間の専門家などを自分で調達するようになる。

```
旧: 人間 → SaaSを選ぶ → 契約する → AIに使わせる
新: 人間 → AIに予算を渡す → AIが必要な能力を買う
```

## 2. SaaSの顧客が「人間」から「AI」に変わる

人間向けの「月額2,980円／高品質OCR／導入実績○万社」に対し、AI向けは機械可読な商品仕様が重要になる。

```
capability: OCR
price: $0.002/page
latency: 300 ms
accuracy: 98.1%
retention: 0 days
payment: x402
```

サービスはブランドではなく **capability / price / quality / latency / trust** として比較される。

## 3. x402の重要性は「決済」より「その場で買えること」

現在、新しいAPIを使うには signup → email verification → credit card → pricing plan → API key が要る。これではAgentが未知のサービスをその場で発見して使えない。

```
GET /api → 402 Payment Required → $0.003 支払い → result
```

x402は **Agentがpermissionlessに能力を調達するための市場インフラ**として見るべき。

## 4. Registry / Discovery

買えるようになっても「何が存在するのか」を知らなければ買えない。人間向け電話帳ではなく、何ができるか／入出力形式／価格／速度／品質／SLA／利用地域／privacy policy／支払い方法を機械可読に公開する Registry が要る。**AI版 App Store + DNS + API marketplace。**

## 5. Registryだけでは足りず、Routerが要る

1000サービスを毎回比較するのは非効率。

```
task → Router → 候補探索 → price × quality × latency × trust → 発注
```

`prompt → best model` を一般化すると `task → best capability`、さらに `objective + budget → best sequence of capabilities`。このときRouterは **購買担当 + プロジェクトマネージャ + ブローカー**になる。

## 6. Pub/Subや逆オークションのほうが自然かもしれない

人間市場は `Seller → 広告 → Buyer`。Agent市場では買い手が先に条件をpublishし、複数のサービスがofferを返すほうが自然。**広告市場というより Reverse Auction。** 将来的には Real-Time Bidding for API calls。

## 7. 「AI向け広告」の正体も変わる

AIにバナーを見せても意味がない。Agent向け広告とは **Routerの候補集合にどう入るか／どう選択されるか**。人間向けSEOが「Googleで上位表示されるには」なら、Agent economyでは「Routerに選ばれるには」になる。

## 8. Routerは巨大な権力を持つ

Routerは情報を提示するのではなく、**実際に誰に仕事と金を渡すかを決める**。

Google検索は attention を配分した。Agent Routerは **revenue そのものを配分する**。自社Agentが自社APIばかり推薦するなら明確な利益相反であり、監査可能性が要る。

```
Candidates: A $0.12 q.94 / B $0.08 q.91 / C $0.15 q.97
Selected: A
Reason: expected utility = .923
Router commission: $0.002
Affiliation: none
```

## 9. ハイパースケーラーが取りに来る領域

Agent Identity / IAM / Budget control / FinOps / Observability / Security / Compliance / Agent Marketplace / Model Router / GPU allocation / Billing——つまり **Agent OS**。

一方でやりにくいのが **Truly Neutral Router**。AWS自身が「今回はAWSではなくRunPodが最適です」と継続的に推薦するのは構造的に難しい。したがって Neutral Router / Independent Reputation / Cross-cloud Marketplace には独立系の余地がある。

## 10. レビュー市場の問題

人間社会では評判が良くても**供給能力に限界がある**。優秀な医者が一日に診られる人数には限りがあるから、二番手・三番手にも需要が流れる。

しかしAgentは `A → A₁, A₂, ... A₁₀₀₀₀₀` とコピーできる。**優秀なAgentの供給量がほぼ無限になる。**

## 11. Winner-take-mostが非常に強くなる

```
少し優秀 → より多く使われる → 実データが集まる → 収益が増える
→ 再投資できる → さらに優秀になる → もっと使われる
```

人間市場には「Aさんは忙しい」というブレーキがある。コピー可能なAgentにはそれがない。**Agent市場は人間市場よりむしろ強い富の集中・市場集中を生みやすい。**

## 12. 「レビュー」の意味自体が変わる

インスタンスを評価しても意味が薄い。評価単位は `Agent family → model → version → configuration → operator`。

レビューも ★★★★★ より実運用benchmarkに近づく。

```
2,800,000 tasks
NDA review accuracy: 99.1%
patent review accuracy: 91.4%
median latency: 4.1 sec
failure rate: 0.3%
```

## 13. Registryには「系譜」が必要になる

```
A → Model X / B → Model X / C → Model X   ← 3社あってもfailure modeは相関する
A → Model X / B → Model Y / C → symbolic  ← 本当に多様
```

将来のRegistryには **Agent genealogy / provenance** が要る。どのモデル、データ、tool、operator、versionから派生したのか。これは「誰が優秀か」ではなく、**誰と誰が同じ失敗をしそうか**を知るための情報。

## 14. 市場集中への反作用として「探索」が要る

常に現在1位だけを使うと、新しいAgentが一生評価されない。

```
95% → best known Agent
 5% → exploration
```

**multi-armed bandit そのもの。** Routerは現在の性能最大化だけでなく、将来の市場について学習する必要がある。

## 15. 多様性そのものがリスク対策になる

同一Agentを100万コピーすると、**同じ未知のバグを100万体すべてが持つ**。Agentの誤りは独立ではなく強く相関する。

```
90% Agent A / 7% Agent B / 3% Agent C
```

と分散することには金融ポートフォリオと同じ合理性がある。最適化対象は `quality − cost − latency` ではなく **`quality − cost − latency − correlated risk`**。

## 16. Routerは「市場設計者」になる

performance ranking / price optimization / exploration / diversity維持 / correlated-risk管理 / provenance確認 / reputation / 新規参入支援 / conflict-of-interest管理——Routerの問題は検索ではなく **Mechanism Design / Market Design**。

```
                    HUMAN
                      │
          objective + budget + policy
                      ▼
                    AGENT
                      │
              needs capability
             ┌────────┴────────┐
             ▼                 ▼
         Registry            Pub/Sub
       何が存在するか       誰かできるか
             └────────┬────────┘
                      ▼
                   Router
       ┌──────────────┼──────────────┐
     price          quality         trust
     risk          diversity      provenance
       └──────────────┼──────────────┘
                      ▼
                 Marketplace → x402 → Agent / API / Human
                      │
                 reputation ──→ Routerへ
```

中心的な問いは「AIにどう払わせるか」ではなく、**誰がAIの購買意思決定を支配するのか**。その先には**効率の最大化と、市場の競争性・多様性をどう両立させるか**がある。

必要なインフラは `Registry + Router + Payment` ではなく、
**`Registry + Provenance + Reputation + Exploration + Risk-aware Routing + Payment`**。

---
---

# 17. 本リポジトリの主張との突き合わせ

以下は上記の議論を [`thesis.md`](thesis.md) / [`open-questions.md`](open-questions.md) に照らしたもの。

## 17.1 収束：§13・§15 は命題4の再発見である

命題4は「同一weight由来のエージェント群は誤りが相関する」と述べた。§13 と §15 は、**市場設計の側から同じ結論に独立に到達している。**

| thesis | market.md |
| --- | --- |
| 誤りが相関する（命題4） | 同一Agentを100万コピーすると同じ未知のバグを全体が持つ（§15） |
| 実効独立サンプル数 $N_\mathrm{eff}$（Q1） | 誰と誰が同じ失敗をしそうか（§13 genealogy） |
| 独立観測をどう作るか（Q2） | exploration予算（§14）、ポートフォリオ分散（§15） |

**これは [`works/map-axes.md`](../works/map/map-axes.md) 軸A-3 が予測した通りのことが起きた例である。** 異なる分野（機構設計・市場設計）の事前分布を与えると、同じ結論に別の道から着く。しかも**用語が一つも共通していない**——CPCも陪審定理も出てこないのに、同じ場所に着いている。

分野を分けることで独立性が得られるという推測に対する、一件の傍証。

## 17.2 新規：§11 は命題4に無かった機構である

**ここが最も重要。** 命題4は多様性の崩壊を**初期条件**として説明していた——同じweightから来たから、最初から多様でない。

§11 はそうではない。**たとえ多様な状態から始めても、市場が多様性を破壊する。**

```
少し優秀 → より多く使われる → データが集まる → さらに優秀 → もっと使われる
```

人間市場ではここに「Aさんは忙しい」という供給制約がブレーキをかけ、二番手・三番手に需要が流れる。**コピー可能性がそのブレーキを外す。**

したがって命題4に追加すべき節がある。

> **多様性の崩壊は、初期条件であるだけでなく、市場の産物でもある。**
>
> 異なるweightのエージェントを揃えても解決しない。市場に晒せば、僅差の優位が自己強化して一者に収束し、事後的に「同一weight由来の群れ」と同じ状態が再現される。

これは元の命題4より**悪い知らせ**である。命題4は「多様なエージェントを用意せよ」という処方を許したが、§11 はその処方が市場圧の下で持続しないと言っている。

**未検証**：この自己強化ループが実際にどの速さで回るか、供給制約以外のブレーキ（規制、切替コスト、ニッチ需要）がどれだけ効くかは、観測されていない。

## 17.3 §14 は Q2 への具体的な答えである

Q2 は問うていた——**「多様性のコストは何で支払われるのか。無料の多様性は存在しないはず」**。

§14 が答えを持っている。

> **現在の期待効用の一部で支払う。** 5%を劣った選択肢に回す。

そして §15 がその正当化を与える——それは浪費ではなく、**相関リスクに対する保険料**である。ポートフォリオ理論と同じ構造。

Q2 の表に一行追加すべき:

| 手段 | 期待 | 疑い | コスト |
| --- | --- | --- | --- |
| 探索予算の確保 | 一位以外が評価され続ける | 探索率をどう決めるか。低すぎれば無意味、高すぎれば浪費 | **期待効用の直接的な放棄（明示的に測れる）** |

**多様性のコストが初めて数量化された形で現れた。** これは open-questions.md に書き戻す価値がある。

## 17.4 Router は Q3 の選択圧そのものである

Q3 は問うていた——「選択圧の健全性を、選択圧の内側から測ることは可能か」。

**この経済において、選択圧とは Router である。** 誰が仕事と金を受け取るかを決めるのは Router だからである。

そして §8 の利益相反問題は、Q3 の後半——「検証器そのものをエージェントが書く場合、検証器の腐敗をどう検知するか」——と同一の問題である。Routerは利害関係者が書く。

§8 の監査ログ（Selected / Reason / commission / Affiliation）は、Q3 が要求した「外部からの定期的な較正」の具体形になっている。**ただし、監査ログを出すのも Router 自身である。** つっかえ棒を彫らなかった職人と同じ構造が残る。

## 17.5 命題3（二重ループ）との関係

命題3は「外側ループ（足場・道具の蓄積）が速く、内側ループ（weightの更新）が遅い」と述べた。

エージェント経済は**外側ループの制度化**である。Registry / Router / reputation は、堆積物に値段と索引をつける仕組みにほかならない。

ここから予測が一つ出る。**外側ループが市場になると、回転がさらに速くなる。** 値段がつくものは選択圧を受けるからである。同時に §11 により、速くなるほど収束も速くなる。

**未検証。**

## 17.6 まとめ

| 節 | 位置づけ |
| --- | --- |
| §13 §15 | 命題4の**独立な再発見**（別分野から） |
| §11 | 命題4への**追加**。多様性の崩壊は市場の産物でもある |
| §14 | Q2 への**具体的な答え**。多様性のコスト＝放棄した期待効用 |
| §8 | Q3 と**同型の問題**。選択圧を利害関係者が書く |
| §1〜§7 §9 §12 §16 | 本リポジトリが扱っていなかった**新領域**。[`works/map.md`](../works/map/map.md) 第八部として追加 |

## 17.7 反証されうる点

この文書自体が推測に厚い。とくに以下は世界からの返事を受け取っていない。

- **x402型の即時決済が実際に普及するか。** 現在の signup 型が残る可能性は十分ある
- **Registry が中立に運営されうるか。** DNS も App Store も中立ではなかった
- **§11 の自己強化ループの速さ。** 切替コストが低い市場ではブレーキが弱いが、実測がない
- **「AIの購買意思決定を誰が支配するか」が中心的な問いであるという判断そのもの。** 別の問い（誰が能力を供給するか、誰が計算資源を持つか）のほうが上流かもしれない
