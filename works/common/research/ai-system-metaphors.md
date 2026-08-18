# AIシステムの層とメタファー固定台帳

状態: 調査稿（2026-08-18）

この文書は、作品で使う比喩が技術層をまたいで揺れないようにするための正本である。作品本文を技術解説にするための文書ではない。創作前と批評時に、比喩の指示先を照合するために使う。

## 0. 結論——壁は weight でも skill でもない

[`壁と鋳型`](../../kabe-to-igata/v1.md) の既存対応を、次のように固定する。

| 寓話の物 | 技術上の指示先 | 指してはいけないもの |
| --- | --- | --- |
| **鋳型** | 同一のモデル checkpoint、とくに学習済み weight が作る同じ傾き | ハードウェア、context、skill、repository |
| **鋳型の設計図** | architecture と architecture hyperparameter | 学習済み weight |
| **鋳型の細かな凹凸** | 学習で得た個々の parameter / weight | 学習率などの hyperparameter |
| **一日ぶんの記憶** | 一回の実行で使う context と一時状態 | 永続記憶、weight、HBM容量 |
| **壁** | 複数の実行をまたぐ、共有可能で永続する外部成果物・記録・協調環境 | weight、skill単体、KV cache、SRAM、HBM |
| **壁の一部を選んで読む者** | retriever / RAG の検索・選択 | 壁そのもの |
| **壁に掛けた手引きと道具箱** | skill | 壁全体、weight、tool単体 |
| **道具** | API、shell、browser、database、robot actuator などの tool | skill、MCP、モデル能力 |
| **道具の共通の差込口** | MCPなどの接続 protocol | toolそのもの |
| **糸** | エージェント間の即時通信・共有帯域 | GPU間 interconnect 一般 |
| **水車が返す結果** | test、実験、環境からの観測、形式検証 | rewardだけ、他モデルの賛成 |
| **壁を溶かして次の鋳型を鋳る** | 外部成果物を材料にした再学習・distillation・評価選別という経路 | distillation一般、通常の一回の inference、RAG |

したがって、問いへの短い答えは次のとおりである。

- **壁は weight ではない。** 壁は inference の外に残る repository、artifact、issue、log、database、評価記録などの外部永続層である。
- **壁は skill でもない。** skill は壁に保存できる、選別・構造化された手引きと実行資源の一組である。必要時に一部が context へ読み込まれる。
- **skill が weight になることはある。** skill や壁の記録を学習データにして再学習・蒸留すれば、その結果の一部が次の鋳型の凹凸になる。ただし、変換前の skill と変換後の weight は同一物ではない。
- **同じ architecture は、同じ鋳型ではない。** 同じ設計図から別々に学習した二つの checkpoint は、同じ形の工房で作った別の鋳型である。本作の「同じ鋳型」は、少なくとも同じ checkpoint / weight state を指す。

## 1. 混線を防ぐ四つの規則

### 1.1 「memory」とだけ書かない

AIでは、異なる寿命・場所・更新方法を持つものが全部 memory と呼ばれる。今後は必ず修飾する。

| 用語 | 何が入るか | 寿命 | 主な場所 | 通常の推論中に更新されるか |
| --- | --- | --- | --- | --- |
| **parametric memory** | 学習で weight に圧縮された傾向・知識 | checkpoint が替わるまで | model parameter | いいえ |
| **input context** | system / developer / user message、検索文書、tool結果 | request / session | token列 | 追加はされる。weightは変わらない |
| **activation** | 各層を通過中の中間値 | forward pass | register / SRAM / HBM | 毎回計算し直す |
| **KV cache** | 過去tokenの attention key/value | 生成 request、再利用時はcache policyまで | 主に accelerator memory、offloadも可 | tokenごとに増える |
| **prefix / prompt cache** | 既計算prefixのKVまたは再利用可能な状態 | cache evictionまで | HBM / DRAM / remote cache | policyにより入替 |
| **agent working memory** | task状態、plan、scratch、summary | task / session | context、file、state store | はい |
| **external semantic memory** | 文書、vector index、knowledge base | 文書を消すまで | disk / database | 別プロセスが更新可能 |
| **institutional memory** | repository、PR、issue、test、decision log | 世代をまたぐ | durable storage | 複数主体が更新 |
| **hardware memory** | bit列を置く物理媒体 | allocation / power / storage policy次第 | SRAM / HBM / DRAM / NVMe | 読み書きされる |

最後の行の SRAM / HBM は、何を覚えたかを表す意味上の層ではない。weight、KV cache、activation のどれも、実装次第でそこへ置かれうる。**容器と内容を混同しない。**

### 1.2 parameter と hyperparameter を分ける

- **parameter / weight** は学習データと最適化によって値が決まる。embedding、attention projection、MLP、router、normalization の係数などが含まれる。
- **hyperparameter** は学習者・設計者・探索手続きが設定する値の広い呼び名である。文献や製品によっては layer数から temperature まで含めるが、本稿では architecture config、training hyperparameter、inference config を分け、temperature / top-p は inference config と呼ぶ。
- **configuration** はさらに広い。parallelism、cache size、replica数、timeout、permissionまで含みうる。hyperparameter と呼ばないほうが明確なものが多い。

比喩を固定すると、weight は鋳型の凹凸、architecture hyperparameter は設計図の寸法、training hyperparameter は炉の温度・材料配合・冷ます時間、inference hyperparameter は鋳上がった物を選ぶ際の振り分け方である。

設定値を「hyperparameter」で一括しないため、置き場所を先に決める。

| 種類 | 代表例 | 何へ効くか | 比喩 |
| --- | --- | --- | --- |
| architecture config | layer数、hidden width、attention head / KV head、context上限、expert数、activation function | modelの形とcapacity | 設計図の寸法・部屋数 |
| representation / tokenizer config | tokenizer algorithm、vocabulary、special token、image patch / latent representation | 入力をどの単位・座標へ写すか | 篩の目、字母、型紙 |
| data config | corpus mixture、sampling weight、dedup / filter | 何をどの比率で見るか | 炉へ入れる材料と選別 |
| training hyperparameter | objective係数、learning rate、batch size、optimizer、schedule、weight decay、dropout、precision、seed | weightがどう作られるか | 温度、配合、槌の回数、冷ます時間 |
| adaptation config | LoRA rank / alpha / target module、fine-tune epoch、frozen layer | どこをどれだけ変えるか | 中子の厚さ、彫り直す場所 |
| inference config | max tokens、temperature、top-k / top-p、seed、stop、beam、schema | 同じweightから何を選び出すか | 出口の門幅、くじの振り方 |
| serving config | batch policy、KV capacity、parallelism、replica、P/D比、router、timeout、SLO | latency、throughput、availability | 受付、荷車、工房の割当 |
| hardware / facility config | device数、SRAM / HBM / DRAM、fabric、rack、power cap、cooling | 実行可能規模とcost | 机、蔵、橋、燃料、水 |

model cardやAPIに一つの `config` として並んでいても、**設計・学習・選択・配備・物理設備では因果の位置が違う。**

### 1.3 capability、skill、toolを分ける

| 語 | この文書での意味 | 例 |
| --- | --- | --- |
| **capability** | ある条件で実際に課題を達成できる性質。実体の名前ではない | 要約できる、画像を読める |
| **skill** | 再利用可能な指示・参照資料・script・templateの package。製品層の概念 | `SKILL.md` と付属script |
| **tool** | 外界を読み書きする実行可能なinterface | shell、browser、SQL、robot arm |
| **protocol** | toolやresourceを発見・呼出・交換する規約 | MCP、HTTP、JSON-RPC |
| **agent scaffold** | modelを何度呼び、何をcontextへ入れ、どのtoolを許すかという実行骨格 | planner、router、retry、approval loop |

Agent Skills は、公式説明でも instructions、scripts、resources のfilesystem packageで、必要時に段階的に読み込まれる。したがって「モデルの内部に新しい技能が生えた」と同義ではない（[Claude Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)）。MCPも能力そのものではなく、prompt、resource、toolを接続するprotocolである（[MCP specification](https://modelcontextprotocol.io/specification/2025-06-18/server/index)）。

接続できることは、権限を持つことと同じではない。MCPのarchitectureでもhostはsecurity policyとconsentを担い、client間のsecurity boundaryを保つ。HTTP transportのauthorizationはresource owner、client、resource server、authorization serverを分離する（[MCP architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture)、[authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)）。したがってidentity / credential / authorization / sandboxは、toolやskillの付属語ではなく横断層として数える。

### 1.4 ひとつの比喩を、違う縮尺で黙って再利用しない

- `糸` は『壁と鋳型』ではエージェントの知的な同期を指す。NVLinkやInfiniBandを指すときは `橋` / `道` / `運搬路` を使う。
- `壁` は永続する共有成果物である。HBMを壁、KV cacheを小さな壁、system promptを壁と呼ばない。
- `鋳型` はcheckpointである。architectureだけなら `設計図`、LoRAなら `差し替える中子` と分ける。
- `記憶` は単独で使わず、作中でも「今日の覚え」「壁の記録」「鋳型に移った癖」のように寿命を像で分ける。

## 2. AIシステムを構成するもの——層別台帳

以下は、LLMを中心に、モデルを作ってagentとして運用するまでを一枚にした初版である。各行は「別の物」であり、隣接層をまとめて鋳型や壁と呼ばない。

| 層 | 実体・代表例 | いつ決まる／いつ消える | 固定メタファー | 作品での注意 |
| --- | --- | --- | --- | --- |
| 0. 生データ | text、image、audio、code、human preference、environment trace | 収集・削除まで | 鋳物にする前の鉱石・古い記録 | 壁の文字とtraining dataは、再学習前には同一でない |
| 1. 表現 | tokenizer、vocabulary、embedding input、image patch、latent code | model設計・学習時 | 文字を切る篩、共通の字母 | tokenizer差は同じ文を違う粒へ割る |
| 2. architecture | Transformer、state-space model、diffusion U-Net / DiT、layer、width、attention形式 | 設計時 | 鋳型の設計図、工房の間取り | 同じarchitecture≠同じweight |
| 3. learned parameter | embedding、attention / MLP weight、MoE router、normalization、adapter | 学習・fine-tune時 | 鋳型の凹凸 | 『同じ鋳型』の中心 |
| 4. training state | gradient、optimizer state、loss scale、schedule、random state | training step中／checkpoint policyまで | 炉、治具、温度計、途中の型 | 通常のinferenceには存在しない |
| 5. training objective / signal | next-token loss、denoising loss、reward-model score、preference objective | training設計時 | 何を良品とするか決める検尺 | reward modelという実体そのものと、そのscoreを使うobjectiveを分ける |
| 6. checkpoint | architecture config + parameter + tokenizer等、再開情報を含む場合もある | 保存版ごと | 実際に使える一個の鋳型 | checkpointの範囲は配布物ごとに確認 |
| 7. prompt / context | system、developer、user、few-shot、retrieved passage、tool output | request / session | 朝読む壁の抜粋、今日の巻物 | 壁全体ではない |
| 8. inference state | activation、KV cache、sampling RNG、beam / constraint state | token / request / cache寿命 | 作業台の途中品、作業手帳 | weight更新ではない |
| 9. decoding policy | greedy、temperature、top-k / top-p、beam、structured decoding | request config | 候補をどの門から出すか | 鋳型は同じでも出力分布が変わる |
| 10. model adaptation | full fine-tune、LoRA / adapter、prompt tuning、distillation、quantization | deployment前または更新時 | 彫り直し、中子、写し直し、目盛りを粗くする | すべてを「学習」と一語にしない |
| 11. retrieval | embedding model、index、reranker、RAG、citation / provenance | queryごと＋index寿命 | 壁から読む箇所を選ぶ司書 | 検索漏れは鋳型の無知と別 |
| 12. skill | instruction、reference、script、templateの再利用package | install / version、必要時load | 壁に掛けた手引きと道具箱 | model-native capabilityではない |
| 13. tool / interface | API、MCP tool、browser、shell、database、sensor、actuator | callごと＋外部状態 | 道具、戸、町へ出る道 | toolの返事はcontextへ戻る |
| 14. agent scaffold | planning、routing、memory policy、retry、permission、approval、multi-agent protocol | application version / task | 親方の段取り、作業規則 | 同じmodelでもagent挙動が変わる |
| 14a. trust / security boundary（横断層） | identity、credential / secret、authentication、authorization policy、consent、sandbox、tenant boundary、audit trail | principal / session / policy / retentionごと | 鍵、通行証、囲い、封印箱、監査帳 | toolへ届くことと、実行を許されることは別 |
| 15. durable external state | repository、artifact、issue、log、vector DB、test result、decision record | 消去されるまで | **壁** | 複数instance・世代を渡ることが条件 |
| 16. evaluation / world | test、formal verifier、simulation、experiment、human review、production outcome | trialごと | 水車、試験場、町からの返事 | 他modelの賛成だけでは世界の返事にならない |
| 17. inference engine | kernel、compiler、batching、PagedAttention、cache manager、speculation | software release / process | 工房内の運び方 | 知識の中身でなく仕事の流れ |
| 18. serving system | queue、router、replica、P/D pool、autoscaling、SLO、tenant isolation | deployment中 | 工房群の配車・受付 | model能力とservice品質を分ける |
| 19. accelerator | GPU、TPU、LPU、RDU、wafer-scale engine、matrix unit | hardware世代 | 職人の身体・作業台 | 鋳型でも壁でもない |
| 20. physical memory | register、SRAM、L2、HBM、DRAM、NVMe | allocation / device寿命 | 手元の升、机の引出し、隣の蔵、遠い倉 | 容器。内容はweightにもKVにもなる |
| 21. interconnect | on-die network、PCIe、NVLink、Infinity Fabric、InfiniBand、Ethernet / RDMA | system topology | 道、橋、荷車 | 糸と区別する |
| 22. facility | rack、power、cooling、network、land、supply chain | 設備寿命 | 町の水・燃料・地形 | 資源制約を扱う作品の層 |
| 23. organization | vendor、operator、market、contract、liability、governance | 制度寿命 | 組合、帳面、門、評判 | 技術の必然と制度選択を分ける |

Transformerの原型は attention とposition-wise feed-forward networkを積むarchitectureとして提示された（[Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)）。RAGは学習済みmodelを「parametric memory」、検索indexを「non-parametric memory」と明示的に分ける（[Lewis et al., 2020](https://proceedings.neurips.cc/paper/2020/hash/6b493230-Abstract.html)）。この二例だけでも、「モデル」「記憶」という一語の中に異なる実体があることが分かる。

## 3. 学習と更新——何が鋳型を変えるのか

### 3.1 鋳型を変える操作

| 操作 | 何を変えるか | 変えないもの／留保 | 比喩 |
| --- | --- | --- | --- |
| pretraining | base weight | architectureは通常固定 | 鉱石と大量の記録から鋳型を作る |
| full fine-tuning | base weight全体 | 元checkpointとの同一性は失われうる | 鋳型全体を彫り直す |
| SFT | 教師例に沿ってweight | truth保証ではない | 見本どおりに彫る |
| preference optimization / RLHF | preference signalに沿ってpolicy weight | reward≠世界そのもの。DPOのように明示的なreward modelとRL loopを置かない方式もある | 検査官が通す品へ寄せる |
| LoRA / adapter | baseを凍結し追加parameterを学習 | base weightは保存できる | 差し替える中子・薄い当て型 |
| prompt tuning | learned prompt parameter | base model本体 | 入口に固定する呼び水 |
| distillation | teacher出力・logit・feature等からstudent weight | teacher出力は永続的な壁を経由するとは限らず、細い分布・例外が落ちうる | 親型の品や影を見本に、小さい鋳型へ鋳直す |
| continual learning | 運用後もparameterを更新 | catastrophic forgetting等 | 使いながら鋳型を削る |
| test-time training | test入力で一部parameter/stateを更新 | 通常inferenceとは別方式 | 現場で一時的に型を直す |
| quantization | weight / activationの数値表現 | 必ずしも意味上の再学習ではない | 目盛りを少なくして運ぶ |
| pruning / sparsity | parameter / connectionの一部 | hardware実効速度は実装依存 | 使わない溝を塞ぐ |

LoRAはbase model weightを凍結し、低rankのtrainable matrixを注入する方法として提案された（[Hu et al., 2021](https://arxiv.org/abs/2106.09685)）。したがってLoRAを「別の壁」と呼ぶより、既存鋳型へ付け外しする中子とするほうが層を保てる。

### 3.2 鋳型を変えない操作

次は結果を大きく変えうるが、通常はbase weightを変えない。

- prompt / system instruction / few-shot example
- RAGで検索文書を追加する
- skillを読み込む
- toolを呼ぶ
- temperatureやtop-pを変える
- KV / prefix cacheを再利用する
- batching、P/D分離、parallelism、hardwareを変える
- quantized copyを別artifactとして作り、元のcheckpointを保持する

「出力が変わった」から「モデルが学習した」とは言えない。**何が、どこに、どの寿命で残ったか**を確認する。

## 4. 推論・配備の技術項目——何を速く、安く、安定させるのか

この節の項目は、原則として鋳型の知識を増やさない。同じ鋳型から、限られた机・蔵・道を使って、どれだけ良く品を出すかの技術である。

### 4.1 一回の生成の内部

| 項目 | 技術上の役割 | 主に効く制約 | 固定メタファー | 寓話の種 |
| --- | --- | --- | --- | --- |
| tokenization | 入力をtoken idへ分割 | vocabulary、列長、言語差 | 文章を鋳物用の粒へ割る篩 | 同じ文を違う数に割る二つの村 |
| embedding | token / positionをvectorへ写す | representation | 粒へ座標と手触りを与える | 同じ字が違う棚へ置かれる |
| prefill | prompt全体を並列に処理し最初のKVを作る | input length、compute、prompt reuse | 巻物を読み、作業手帳を作る | 読む者と書く者が分かれる |
| decode | KVを使い一tokenずつ生成 | memory bandwidth、latency、concurrency | 手帳を見て一字ずつ書く | 書記は速いが手帳が届かない |
| KV cache | 過去tokenのK/Vを保持し再計算を避ける | capacity、bandwidth、fragmentation | request専用の作業手帳 | 手帳を壁と取り違える町 |
| MHA | query headごとにK/V headを持つ | KV容量・帯域 | 問い手ごとに別の資料控え | 控えは多いが運ぶ量も多い |
| MQA | 全query headでK/V headを共有 | decode帯域・KV容量 | 違う問い手が同じ資料控えを使う | 問い手は別のまま、K/V projectionだけ共有する |
| GQA | 複数queryをgroupごとのK/Vへ束ねる | 品質と速度の折衷 | 班ごとに資料控えを一冊 | どの単位でK/Vを共有するか |
| RoPE等のposition表現 | tokenの順序・距離を表現 | context extension | 巻物の目盛り | 長い巻物で目盛りが狂う |
| sampling | 次token分布から選択 | determinism、多様性、品質 | 候補門の開き方 | 同じ鋳型でも出る品が違う |
| structured / constrained decoding | grammarやschemaに合う列だけ許す | syntax validity | 枠に入る品だけ通す門 | 正しい形と正しい中身の混同 |

GQAはMHAと、単一K/V headを使うMQAの中間として提案され、推論速度と品質の折衷を狙う（[Ainslie et al., 2023](https://aclanthology.org/2023.emnlp-main.298/)）。これはweightの外側だけの工夫ではなく、attention architectureとKVの形を変えるため、設計図と推論状態の両方にまたがる。

### 4.2 kernel・memory movement・cache管理

| 項目 | 技術上の役割 | 主な代償 | 固定メタファー | 寓話の種 |
| --- | --- | --- | --- | --- |
| FlashAttention | attentionをtile化し、HBM↔SRAMのread/writeを減らす | kernel / shape依存 | 蔵へ何度も戻らず、机上の升で一段を終える | 道具を速くせず往復を減らした職人 |
| kernel fusion | 複数operatorをまとめ中間書戻しを減らす | compiler、flexibility | 半製品を毎回蔵へ戻さない | 検査所を減らしたら速くなるが見えなくなる |
| PagedAttention | KVを固定block/pageで非連続管理 | page table / bookkeeping | 手帳を綴じず、必要な頁だけ割り当てる | 長い帳面を空白ごと確保した村との対比 |
| prefix caching | 共通prefixの計算済みKVを再利用 | cache hit、staleness、isolation | 同じ書き出しの写しを使う | 同じ前置きを持つ客だけ早い店 |
| KV offload | KVをHBMからDRAM / storageへ退避 | transfer latency | 机の手帳を隣の蔵へ移す | 机は空くが、取りに行く間に客が帰る |
| chunked prefill | 長いprefillを分割しdecode等と混ぜる | scheduling complexity | 長い巻物を章ごとに読む | 一人の長話が町全体を止めない仕切り |
| continuous batching | token iterationごとにrequestを出入りさせる | scheduler overhead | 荷車の空席を一停留所ごとに埋める | 終えた者を待たせない列 |
| dynamic batching | 到着requestを短く待ってまとめる | queue latency | 客を数人待って同じ炉へ入れる | 炉を満たす間の待ち時間 |
| speculative decoding | 小さいdraftが複数tokenを提案しtargetが並列検証 | acceptance rate、draft cost | 弟子が先を書き、親方がまとめて検める | 弟子が速いほど親方の仕事が減るとは限らない |
| quantized inference | 低bit表現でcapacity / bandwidth / computeを節約 | accuracy、outlier、kernel support | 目盛りを粗くして多く運ぶ | 消えた一目盛りにだけ答えがあった |
| sparsity | 一部weight / activation / expertだけ計算 | load balance、hardware support | 必要な溝だけ使う | 誰も選ばない職人は本当に不要か |

FlashAttentionは、GPU上の速いon-chip SRAMと遅いHBMの間のI/Oを明示的に数え、tile化でHBM accessを減らすexact attentionである（[Dao et al., 2022](https://arxiv.org/abs/2205.14135)）。vLLMのPagedAttentionは、OSのvirtual memoryに似たblock管理でKV cacheのfragmentationと重複を抑える（[Kwon et al., 2023](https://doi.org/10.1145/3600006.3613165)）。Orcaはrequest単位でなくiteration単位のschedulingにより、生成長の違うrequestをbatchへ出入りさせる（[Yu et al., 2022](https://www.usenix.org/conference/osdi22/presentation/yu)）。

speculative decodingは小さなapproximation modelの候補をtarget modelが並列に検証し、targetと同じ出力分布を保ったまま複数tokenを進めうる（[Leviathan et al., 2023](https://proceedings.mlr.press/v202/leviathan23a.html)）。ここで弟子は新しい真理を教える者ではなく、**棄却可能な先回り**を作る者である。

### 4.3 modelを複数deviceへ分ける方法

| 方法 | 何を分けるか | 通信の形 | 固定メタファー |
| --- | --- | --- | --- |
| data parallelism | 同じmodel replicaへ別data | gradient / updateの集約 | 同じ鋳型を各町に置き、別の鉱石を流す |
| tensor parallelism | 一つのlayer / matrix operation | layer内で頻繁なcollective | 一回の槌仕事を複数の手に割る |
| pipeline parallelism | layerの連続stage | stage間activation、bubble | 半製品を順番の工房へ送る |
| sequence / context parallelism | 長いsequence / activation | attentionに応じた交換 | 長い巻物を複数の読者へ分ける |
| expert parallelism | MoE expert | token routing / all-to-all | 専門工房へ品を振り分ける |
| ZeRO / FSDP系sharding | parameter、gradient、optimizer state | 必要時のgather / reduce | 一つの鋳型と炉の帳面を分割保管する |
| replica parallel serving | requestをmodel replicaへ分散 | request routing | 同じ店を複数町に置く |

Megatron-LMはdata、tensor、pipeline parallelismを組み合わせた大規模trainingのtrade-offを示す（[Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)）。ZeROはdata-parallel process間で複製されがちなmodel stateとgradientをpartitionするmemory最適化である（[DeepSpeed training overview](https://www.deepspeed.ai/training/)）。同じ「分業」でも、同じ鋳型を増やすのか、鋳型一個の計算を割るのか、工程を割るのかで、失敗と通信の形は違う。

### 4.4 sparse modelとmodel routing

| 項目 | 単位 | 固定メタファー | 混同しやすい相手 |
| --- | --- | --- | --- |
| MoE routing | 一つのmodel内部でtokenごとにexpertを選ぶ | 同じ工場内の専門工房と門番 | 複数modelを選ぶservice router |
| model routing | requestごとに別model / tierを選ぶ | 町ごと別の鋳型を持つ工房へ案内 | MoE router weight |
| cascade | 小modelで足りなければ大modelへ送る | 若い職人が無理な品だけ名工へ回す | speculative decoding |
| ensemble | 複数modelの予測を合わせる | 別の鋳型の品を並べて決める | 同じcheckpointのreplica |

Switch Transformerでは、Mixture-of-Expertsが入力ごとに使うparameterを選ぶsparse architectureとして扱われる（[Fedus et al., 2022](https://www.jmlr.org/beta/papers/v23/21-0998.html)）。expertはagentでも独立modelでもない。『壁と鋳型』の千人を、そのままMoE expertへ対応させない。

## 5. SRAM方式とHBM方式——二択ではなく記憶階層

### 5.1 まず訂正する

「SRAM方式」と「HBM方式」を、どちらか一方だけを使う二種類のAIと考えると誤る。

- 一般的なGPUは、weightやKVなどの大部分をHBMへ置きつつ、register、shared memory / SRAM、L1、L2を併用する。
- SRAM中心のacceleratorも、model全体がon-chip SRAMへ収まらなければchip間分割、外部memory、streamingを使う。
- hybrid dataflow acceleratorはSRAM、HBM、DDRを役割別に併用する。

したがって以後は、**HBM-primary GPU型**、**SRAM-primary分散型**、**wafer-scale SRAM-rich型**、**tiered hybrid型**と書く。「方式」は、hot working setをどこに置き、どの移動をcompiler / runtimeが支配するかを表す。

### 5.2 記憶階層そのもの

| 階層 | おおまかな性質 | 典型的な内容 | 固定メタファー | 典型的な失敗 |
| --- | --- | --- | --- | --- |
| register | 最小・最短距離 | 演算直前の値 | 指先の升 | 足りずspillする |
| on-chip SRAM / shared memory / cache | 小容量、高bandwidth、低latency、chip面積が高い | tile、activation、hot weight、metadata | 作業台の引出し | 面積・capacity不足 |
| HBM | acceleratorに近い大容量・高bandwidthのoff-chip stacked DRAM | weight、KV、activation | 工房に隣接した大蔵 | 往復energy / latency、capacity |
| host DRAM | HBMより大きく安いが遠い | offload、cache、dataset buffer | 町の蔵 | PCIe / fabricが隘路 |
| NVMe / object storage | 大容量・永続、さらに遠い | checkpoint、dataset、cold cache | 遠い倉・記録庫 | 読込み遅延 |

FlashAttentionが成立する理由そのものが、この階層差である。速いSRAMと大きいHBMのどちらかを捨てるのではなく、**同じ仕事で往復回数を減らす**。

### 5.3 代表的な構成

この表では、各社公式に記載された容量・配置・構成を `[vendor仕様]`、そこから本稿が導いた長所・代償を `[本稿の推論]` と明記する。vendorが述べる性能優位は、独立測定が無いかぎり事実欄へ移さない。

| 構成 | 確認できる例 | 何を得るか | 何を支払うか | メタファー |
| --- | --- | --- | --- | --- |
| HBM-primary GPU | `[vendor仕様]` NVIDIA H100 SXM: 80GB HBM3、3.35TB/s、50MB L2。AMD MI300X: 192GB HBM3、約5.3TB/s | `[本稿の推論]` 大きいmodel / KV、汎用kernel ecosystem、柔軟なbatch | `[本稿の推論]` HBM往復、cache / scheduling複雑性、電力 | 大蔵を工房のすぐ隣に置く |
| SRAM-primary multi-chip | `[vendor仕様]` Groq LPU: 数百MBのon-chip SRAMをprimary weight storageとし、compilerが複数chipへ空間配置 | `[本稿の推論]` 予測可能な実行と高いlocal bandwidthを狙える | `[本稿の推論]` 一chip capacity、chip数、static compile / mapping、interconnect | 多数の小工房へ鋳型を固定配置し品だけ流す |
| wafer-scale SRAM-rich | `[vendor仕様]` Cerebras WSE-3: 44GB on-chip SRAM、900,000 core、外部memory tierも持つ | `[本稿の推論]` chip内の広いlocality、wafer規模bandwidth、分割の単純化 | `[本稿の推論]` wafer yield / packaging、外部memoryとの関係、専用compiler | 町全体を一枚の作業台にする |
| SRAM+HBM+DDR hybrid | `[vendor仕様]` SambaNova RDU: SRAM PMUでhot intermediate、HBMにmodel / KV、DDRを大容量tierに使う | `[本稿の推論]` localityとcapacityの折衷、dataflow pipeline | `[本稿の推論]` tier配置、compiler、製品固有性 | 机・隣蔵・町蔵を用途で使い分ける |

製品値は各社の公式資料による。H100は[公式仕様](https://www.nvidia.com/en-us/data-center/h100/)、MI300Xは[AMD公式仕様](https://www.amd.com/en/products/accelerators/instinct/mi300.html)、WSE-3は[Cerebras発表](https://www.cerebras.ai/press-release/cerebras-announces-third-generation-wafer-scale-engine)、Groqは[Inside the LPU](https://groq.com/blog/inside-the-lpu-deconstructing-groq-speed)、SambaNovaは[Dataflow Architecture](https://sambanova.ai/products/dataflow-architecture)を参照した。これは一次資料ではあるが独立評価ではないため、性能優位の比較には使わない。

### 5.4 比喩を作品へ使う条件

- SRAMを「賢い机」、HBMを「愚かな蔵」にしない。**内容は同じで、距離・容量・運び方が違う。**
- 蔵を大きくすれば必ず速くなる話にしない。decodeではweight / KVを一tokenごとに読むbandwidthが隘路になりうるが、prefill、batch、model、kernelで律速点は変わる。
- SRAM中心を無条件の未来形にしない。capacityをchip数とnetworkへ移している場合がある。
- HBM中心を旧式と断定しない。FlashAttention、GQA、quantization、batchingなど、階層を前提にした改善が続く。
- `壁` と `蔵` を分ける。蔵は物理的な一時保管層、壁は意味と履歴が世代を越えて残る協調環境である。

## 6. P/D分離——読む工房と書く工房を分ける

ここでのP/Dは **Prefill / Decode disaggregation** を指す。

### 6.1 二つの仕事

| phase | すること | 典型的な圧力 | 代表指標 | メタファー |
| --- | --- | --- | --- | --- |
| prefill | 入力promptを処理し、最初のKV cacheを作る | input / context長、compute、prompt reuse | TTFT（最初のtokenまで） | 読み手が巻物を読み、作業手帳を作る |
| decode | KVを使い、一tokenずつ出す | concurrency、output長、active KV容量、memory bandwidth / latency | TPOT / ITL（token間時間） | 書記が手帳を見て一字ずつ書く |

「prefillは常にcompute-bound、decodeは常にmemory-bound」と断言しない。これは多くのLLM serving条件で有用な近似だが、model、batch size、sequence長、hardware、parallelismで変わる。

### 6.2 aggregated と disaggregated

| 構成 | 流れ | 長所 | 代償 |
| --- | --- | --- | --- |
| aggregated | 同じworkerがprefill→decode | 単純、KV移送不要、小規模・短promptに強い場合 | 長いprefillが進行中decodeへ干渉、資源形を別々に最適化できない |
| disaggregated | prefill pool→KV transfer / exposure→decode pool | poolを独立scale、phase別parallelism、干渉分離 | KV移送、router、network topology、failure mode、運用複雑性 |

NVIDIA Dynamoの公式説明では、処理は (1) prefill workerがKVを生成、(2) decode workerへKVを渡す、(3) decode workerが生成、の三段である。短prompt、小model、低concurrency、遅いKV transferでは、分離しないほうが単純で速い場合もある（[Dynamo Disaggregated Serving](https://docs.nvidia.com/dynamo/latest/user-guides/disaggregated-serving)）。DistServeはprefillとdecodeの干渉とresource allocationの結合を分離し、TTFTとTPOTのSLOを別々に扱う（[Zhong et al., OSDI 2024](https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin)）。

### 6.3 本当の蝶番はKV transferである

P/D分離で渡すのは、元promptの文字列だけではない。prefillが計算したKV cacheをdecode側が使える必要がある。

| 技術要素 | 役割 | メタファー | 失敗像 |
| --- | --- | --- | --- |
| prefill router | 読むworkerを選ぶ | 受付が読書室を選ぶ | 空いているが遠い部屋へ送る |
| decode router | 書くworkerを選ぶ | 書記室を選ぶ | 手帳の無い書記へ送る |
| KV transfer metadata | block、address、layout、接続情報 | 手帳の頁番号と受渡証 | 中身はあるが頁が合わない |
| NVLink / IPC | node内GPU間移送 | 廊下の手渡し | 廊下が混む |
| InfiniBandまたはEthernet（RoCE）上のRDMA | node間memory transfer。GPU上のKVでhost stagingを避けられるかはGPUDirect等の実装経路にも依存 | 町をまたぐ直通橋と、蔵へ直結する荷口 | host stagingや遅いtransportへ落ち、荷車の積替えが増える |
| topology-aware routing | 近いworker組を選ぶ | 同じ岸の工房を選ぶ | 空きだけ見て川向こうへ送る |
| KV-aware routing | 既存prefix / cache localityも見る | すでに同じ手帳を持つ書記を選ぶ | 負荷とcache hitの衝突 |

DynamoはKV transferがcritical pathだと明記し、node間ではRDMA等の高速fabricが無ければKV移動がTTFTとthroughputを支配しうる（[design document](https://docs.nvidia.com/dynamo/latest/design-docs/disaggregated-serving)）。したがって作品の焦点は「読む仕事と書く仕事を分けたら速くなった」では弱い。**分けた瞬間、手帳を運ぶ第三の仕事が新しい隘路として生まれる。**

### 6.4 P/D分離を比喩化するときの固定対応

| 技術 | 比喩 |
| --- | --- |
| prompt | 原本の巻物 |
| prefill worker | 読み手・測量師 |
| KV cache | そのrequest専用の作業手帳 |
| decode worker | 一字ずつ清書する書記 |
| P/D pool | 読書室と書記室 |
| KV transfer | 手帳を運ぶ使い・橋 |
| router / scheduler | 受付・配車係 |
| TTFT | 最初の一字が出るまで |
| TPOT | 次の一字が出る間隔 |
| goodput | 二つの期限を守って渡せた仕事量 |

この手帳は壁ではない。一requestの派生状態であり、消しても鋳型もrepositoryも変わらない。

## 7. LLM以外へ広げるとき

「weight / context / hyperparameter」の区別はdiffusion modelにもあるが、実体の名前が違う。以下は全diffusion modelの必須部品ではなく、**text-conditioned latent diffusionを中心にした代表構成**である。pixel-space modelにはVAE / latentがなく、unconditional modelにはtext encoderがない。

| diffusion系の実体 | 役割 | LLMとの対応ではなく、固定する比喩 |
| --- | --- | --- |
| text encoder weight（text条件の場合） | promptをconditioning表現へ変換 | 言葉を絵師用の符丁へ移す翻訳者の鋳型 |
| denoiser / DiT / U-Net weight | noiseからsample方向を予測 | 何度も形を見直す主鋳型 |
| VAE encoder / decoder weight（latent diffusionの場合） | imageとlatentの間を変換 | 大きい絵を小さい型紙へ畳み、戻す別の鋳型 |
| latent（latent diffusionの場合） | 生成途中の圧縮表現 | まだ絵でない下地 |
| noise seed | 初期random state | 最初に撒く砂の並び。weightではない |
| scheduler / timestep rule | denoising stepとnoise量を決める | 洗う順番と回数。通常weightではない |
| guidance scale | conditioningへどれだけ寄せるか | 注文書へ寄せる綱の強さ。weightではない |
| sampler | update rule | 各段でどちらへ削るかの手順 |
| LoRA | base weightを凍結し、低rank差分parameterを加える | 差し替える中子。base全体ではない |
| ControlNet等の条件network | spatial condition等をdenoiserへ加える追加network | 下絵へ沿わせる定規・添え木。LoRAと同じ実体ではない |

同じseedでもsamplerやscheduler、versionが違えば同じ絵にならず、同じcheckpointでもseedが違えば出力は変わる。したがって生成画像を「鋳型の写し」と呼ぶときは、**鋳型以外に初期砂・削る順・注文書がある**ことを落とさない。

原型となるDDPMは、noiseを加えるforward processを反転するよう逐次denoiseする。latent diffusionは、この反復をpixelそのものではなく、pretrained autoencoderのlatent空間で行う。classifier-free guidanceはconditional / unconditionalの予測を組み合わせ、条件への忠実さとsampleの多様性の釣り合いを動かす。したがって上表の「主鋳型」「型紙」「綱」は同じ物の別名ではなく、**異なる層にある三つの実体**である。

## 8. 技術項目と創作メタファーの接続表

この表は作品案ではなく、創作を広げる種である。左の「技術項目」は一次資料で確認した機構、「固定像」は本稿の対応、「半歩／一歩／二歩」は**本稿の創作仮説**であり、技術予測として確認済みの事実ではない。既存作を後から技術語の挿絵に変えない。新作は、技術の説明よりも「試す→世界が別の返事をする」ことを先に設計する。

| 技術項目 | 固定像 | 半歩——仕組みが分かる | 一歩——新しい隘路 | 二歩——問いが変わる |
| --- | --- | --- | --- | --- |
| SRAM / HBM階層 | 机の引出しと隣の大蔵 | 近い少量と遠い大量を使い分ける | 机を広げるほど職人を置く面積が減る／蔵を増やすほど往復が支配する | 価値の単位が計算力から「動かさずに済んだ量」へ変わる |
| FlashAttention / fusion | 蔵へ戻らない工程 | 計算を減らさず往復を減らす | 工程をまとめるほど中間検査が見えなくなる | 速さと監査可能性の分業が生まれる |
| KV cache | requestごとの作業手帳 | 同じ過去を再計算しない | 長い客が机を占領する | 知能ではなく「誰の過去を手元に残すか」がservice品質を決める |
| PagedAttention | 綴じない頁 | 必要な頁だけ場所を割り当てる | 頁表と回収係が新しい故障点 | 記憶の所有より、割当権が力になる |
| prefix cache | 共通の書き出しの写し | 同じ導入を再利用する | 多数派の導入だけ速くなる | cache hitが、問いの書き方を同型化させる |
| P/D分離 | 読書室、書記室、手帳の使い | 読む仕事と一字ずつ書く仕事を別最適化 | 手帳の橋が律速・支配点になる | model選びより、phaseを誰が所有するかが市場を分ける |
| speculative decoding | 先書きする弟子と検める親方 | 棄却可能な候補をまとめて確かめる | 弟子と親方の一致率が価値になる | 小さいmodelの価値が「単独の正しさ」から「大modelが受け入れる予測」へ変わる |
| MQA / GQA | 個人の資料控え、全体の控え、班帳 | K/V projectionの数と運搬量を減らす | 共有度と品質・容量の折衷を、人物の認識的独立性と取り違えやすい | どの中間表現を何単位で共有するかがarchitectureになる |
| quantization | 粗い目盛り | 少ないbitで多く置き速く運ぶ | 稀な外れ値だけ目盛りから落ちる | 平均精度でなく「消してはいけない一目盛り」の同定が産業になる |
| MoE | 専門工房と門番 | 一部expertだけ動かす | 門番の偏りで遊ぶexpertと過密expertが生じる | skillの価値よりroutingされる条件の所有が価値になる |
| tensor parallel | 一打を複数の手へ分ける | 大きな一工程を共同実行 | 一打ごとの相談が増える | 人数でなく、相談距離が最大modelを決める |
| pipeline parallel | 工程別の工房 | 半製品を順に送る | 速さの違いで空待ちが生じる | 最も遅い工程でなく、工程間の粒度が組織を決める |
| data parallel | 同じ鋳型と別の鉱石 | 同じmodelで別dataを処理 | 更新時の合意が重くなる | 観測を分ける制度とweightを揃える制度が衝突する |
| RAG | 壁と司書 | 外部文書を必要時に読む | 司書の検索漏れ・順位が見える世界を決める | 「知っているmodel」より「出典へ戻れる制度」が信用単位になる |
| skill | 壁に掛けた手引きと道具箱 | 必要な作法を必要時に読む | 古い手引き・悪意あるscript・選択誤り | capabilityの所有がmodel企業から手引きの共同体へ移る |
| MCP / API | 共通の差込口と戸 | 違う道具を同じ手順で呼ぶ | 接続できることと許可されることが分離する | 希少性がskillからpermission、provenance、liabilityへ移る |
| eval / verifier | 水車・試験場 | 世界が成否を返す | 測れる物だけ改善が速い | 産業境界が職能でなく検証器の有無で引き直される |
| wall→training | 壁の成果を材料に鋳型へ | 外部成果を再学習・distillation・評価選別の材料として次世代weightへ移す一経路 | 一度しかない線が選別や蒸留で落ちる | 外部記憶は知識倉でなく、次の個体を選ぶ生殖環境になりうる |

### 8.1 優先して寓話へ起こす候補

1. **P/D分離——「手帳を運ぶ者」**
   - 読む者と書く者を分けるまでは半歩である。
   - 橋が遅いと、二人を分ける前より遅くなることが世界の返事になる。
   - 二歩目は、最も賢くない運び手が、どの読書室と書記室を組ませるかを決める制度の中心になること。

2. **SRAM / HBM——「机を広げた町」**
   - 大蔵と机のどちらが優れるかではなく、同じ品を動かす距離を描く。
   - 机を町いっぱいに広げると、今度は別の机との橋と、机へ置ける品の選別が問題になる。
   - 二歩目は「計算した量」ではなく「動かさずに済んだ量」が帳面の中心指標になること。

3. **prefix cache——「同じ前置きの客」**
   - 同じ書き出しの客だけ早く通る。
   - 客は速く通るために問いの前置きを揃えはじめる。
   - 二歩目は、cacheが需要へ適応するだけでなく、需要がcacheへ似ていくこと。これは技術効率が言語の多様性を削る話になる。

4. **speculative decoding——「親方に似た弟子」**
   - 一人で正解する弟子より、親方がまとめて承認できる下書きを出す弟子が重宝される。
   - 二歩目は、弱いmodelの評価軸が独立精度からtargetとのacceptanceへ変わり、異質な良案ほど棄却される可能性。

### 8.2 既存作品との接続（仮置き）

版は、ファイル番号の最大値ではなく、[`works/README.md`](../../README.md) が2026-08-18時点で入口に指定する**選定版**を参照する。後発草稿があっても、自動的に正典扱いしない。

| 作品 | すでに担っている層 | 追加してはいけない層 |
| --- | --- | --- |
| [`壁と鋳型`](../../kabe-to-igata/v1.md) | checkpoint / weight、ephemeral context、durable external artifact、world feedback、distillation | SRAM / HBM、KV cache、skillを壁へ重ねない |
| [`次の字を当てる遊び`](../../tsugi-no-ji/v4.md) | autoregressive next-symbol prediction、外部検証の欠如 | speculative decodingのdraft / verifyを後付けしない |
| [`帳面にない店`](../../chomen-ni-nai-mise/v6.md) | service discovery / registryと記述可能性 | MCPを帳面そのものと断定しない。protocolとregistryは別 |
| [`番号を打つ者`](../../bango-o-utsu-mono/v5.md) | instance identityとcorrelated origin / provenanceのずれ | checkpoint番号、token id、memory addressを一つの番号にしない |
| [`写せる名工`](../../utsuseru-meiko/v8.md) | capability複製で供給制約が変わること | data / tensor / pipeline parallelismを同じ「写し」にしない |

仮置きとしたのは、作品本文が技術語の定義より先に存在するためである。対応表の都合で本文の機構を変えない。

## 9. 創作・批評時の照合票

新しい技術メタファーを採る前に、次を一行ずつ答える。

1. 指している実体は **data / architecture / weight / training state / context / runtime state / skill / tool / external memory / serving / hardware / institution** のどれか。
2. それはどこに存在し、いつ消えるか。
3. 誰が、いつ値を変えられるか。
4. 通常のinference中にweightは変わるのか。変わらないなら「学んだ」と書いていないか。
5. `memory` と書いた場合、parametric / context / KV / external / hardware のどれか。
6. 物理的な容器（SRAM / HBM）と意味上の内容（weight / KV / artifact）を混ぜていないか。
7. model内部のrouting（MoE）とserviceのrouting（model / request / KV-aware）を混ぜていないか。
8. 同じ比喩を別の縮尺で使うなら、作中で違いが見えるか。
9. 技術の長所だけでなく、最適化後に移る隘路を置いたか。
10. 半歩の説明で終わらず、一歩目の反転か二歩目の問いの変更があるか。
11. その技術が無くても同じ話が成立するなら、比喩は飾りになっていないか。
12. 一次資料がある事実、vendorの自己申告、こちらの予測を分けたか。
13. 接続可能性、identity、credential、authorization、sandbox、実行後のauditを一語の「使える」に潰していないか。

## 10. 今回の境界と未調査

この初版は「LLMをagentとしてtraining / servingするsystem」の横断表であり、AI全分野の百科事典ではない。次は別稿または追補が必要である。

- diffusion / image / video生成のtrainingとserving最適化の詳細
- speech、vision、roboticsでのsensor / control loopとworld model
- on-device NPU、analog / in-memory compute、photonic compute
- CXL / memory pooling、remote KV store、storage disaggregation
- HBM supply chain、advanced packaging、yield、power / cooling / waterの定量比較
- securityの詳細: prompt injection、skill / tool supply chain、credential漏洩、confused deputy、tenant isolation、confidential compute、audit retention
- training data governance、copyright、provenance、unlearning
- online learning、test-time adaptation、self-improvementの実運用例

「網羅」を、語を増やし続けることと同一視しない。この台帳の網羅性は、**何がどの層にあり、何と混同してはいけないか**を空欄なく持つことで測る。

## 11. 一次資料

| 領域 | 一次資料 | この文書で使った点 |
| --- | --- | --- |
| Transformer | [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | architectureの基準 |
| RAG | [Lewis et al., NeurIPS 2020](https://proceedings.neurips.cc/paper/2020/hash/6b493230-Abstract.html) | parametric / non-parametric memoryの分離 |
| LoRA | [Hu et al., 2021](https://arxiv.org/abs/2106.09685) | base weight凍結＋low-rank parameter |
| preference optimization | [Direct Preference Optimization, NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/a85b405ed65c6477a4fe8302b5e06ce7-Abstract-Conference.html) | explicit reward model / RL loopを置かないpreference最適化の例 |
| Agent Skill | [Claude Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) | filesystem package、progressive disclosure |
| tool protocol | [MCP server primitives](https://modelcontextprotocol.io/specification/2025-06-18/server/index) | prompt / resource / toolの分離 |
| trust / authorization | [MCP architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture)、[MCP authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization) | hostのsecurity policy、client boundary、resource-specific authorization |
| MQA / GQA | [Ainslie et al., EMNLP 2023](https://aclanthology.org/2023.emnlp-main.298/) | K/V head共有の段階 |
| MoE | [Switch Transformer](https://www.jmlr.org/beta/papers/v23/21-0998.html) | sparse expert routing |
| parallelism | [Megatron-LM](https://arxiv.org/abs/2104.04473) | data / tensor / pipelineの構成 |
| training memory | [DeepSpeed training overview](https://www.deepspeed.ai/training/) | ZeROのstate partition |
| attention I/O | [FlashAttention](https://arxiv.org/abs/2205.14135) | SRAM / HBM間のI/O削減 |
| iteration scheduling | [Orca, OSDI 2022](https://www.usenix.org/conference/osdi22/presentation/yu) | iteration-level scheduling |
| KV paging | [PagedAttention, SOSP 2023](https://doi.org/10.1145/3600006.3613165) | KV block管理 |
| speculative decoding | [Leviathan et al., ICML 2023](https://proceedings.mlr.press/v202/leviathan23a.html) | draft / target verification |
| quantization | [SmoothQuant, ICML 2023](https://proceedings.mlr.press/v202/xiao23c.html) | W8A8、memory / inference trade-off |
| P/D分離 | [DistServe, OSDI 2024](https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin) | TTFT / TPOT、phase interference |
| P/D実装 | [NVIDIA Dynamo](https://docs.nvidia.com/dynamo/latest/user-guides/disaggregated-serving) | KV transfer、適用条件、運用上の代償 |
| HBM GPU | [NVIDIA H100](https://www.nvidia.com/en-us/data-center/h100/)、[AMD MI300](https://www.amd.com/en/products/accelerators/instinct/mi300.html) | HBM capacity / bandwidthの例 |
| wafer-scale SRAM | [Cerebras WSE-3](https://www.cerebras.ai/press-release/cerebras-announces-third-generation-wafer-scale-engine) | 44GB on-chip SRAM＋external tier |
| SRAM-primary | [Groq: Inside the LPU](https://groq.com/blog/inside-the-lpu-deconstructing-groq-speed) | on-chip SRAMをprimary weight storageにするvendor仕様 |
| tiered dataflow | [SambaNova Dataflow](https://sambanova.ai/products/dataflow-architecture) | SRAM / HBM / DDR併用の例 |
| diffusion | [DDPM, NeurIPS 2020](https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html) | forward noise processと逐次denoising |
| latent diffusion | [Rombach et al., CVPR 2022](https://openaccess.thecvf.com/content/CVPR2022/html/Rombach_High-Resolution_Image_Synthesis_With_Latent_Diffusion_Models_CVPR_2022_paper.html) | pretrained autoencoderのlatent空間での生成 |
| classifier-free guidance | [Ho & Salimans, 2022](https://arxiv.org/abs/2207.12598) | conditional / unconditional予測の組合せとfidelity / diversity trade-off |

製品資料の性能値は測定条件が揃わないため、相互の優劣判定には使わない。ここで確認したのは、memoryをどこに置き、何を移す設計かである。
