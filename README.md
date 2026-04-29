# claude-code-template

Claude Code を使った仕様駆動開発（Spec-Driven Development）のためのプロジェクトテンプレートです。アイデアメモから始めて、PRD・機能設計・アーキテクチャなどの永続ドキュメントを段階的に整備し、それを元に新機能を実装していくワークフローを提供します。

## 特徴

- **仕様駆動開発のワークフロー**: アイデア → PRD → 機能設計 → アーキテクチャ → 実装、までを一連のスラッシュコマンドで支援
- **6つの永続ドキュメント**: プロダクト要求定義書、機能設計書、アーキテクチャ設計書、リポジトリ構造定義書、開発ガイドライン、用語集
- **Skill によるガイド**: 各ドキュメントの作成手順とテンプレートを Skill として定義
- **サブエージェント**: ドキュメントレビューや実装検証を独立したコンテキストで実行
- **プロンプトログの保存**: `Stop` フックで会話ログを `docs/prompt/` 配下に自動記録するほか、`/save-prompt-log` で重要なやり取りをトピック単位で構造化して保存可能

## ディレクトリ構成

```text
.
├── .claude/
│   ├── agents/        # サブエージェント定義（doc-reviewer, implementation-validator）
│   ├── commands/      # スラッシュコマンド定義（setup-project, add-feature, review-docs）
│   ├── hooks/         # フックスクリプト（save_prompt_log.py）
│   ├── skills/        # Skill 定義（PRD作成、設計書作成など）
│   └── settings.json  # 権限設定・フック設定
├── .devcontainer/     # Dev Container 設定（VS Code + Docker でのコンテナ開発用）
├── .steering/         # /add-feature 実行時に作成される機能別の作業記録
├── docs/
│   ├── ideas/         # アイデアメモ（テンプレート + 記入例）
│   └── prompt/        # 会話ログの自動保存先（フックにより生成）
├── LICENSE
└── README.md
```

## 使い方

### 1. テンプレートの取得

```bash
git clone https://github.com/<your-account>/claude-code-template.git my-project
cd my-project
```

### 2. アイデアメモの作成

`/draft-idea` を実行すると、Claude が段階的に質問を投げかけ、その回答をもとに [docs/ideas/initial-requirements.md](docs/ideas/initial-requirements.md) を自動生成します。

```bash
claude
> /draft-idea
```

質問は以下の Phase に分かれています（任意フェーズはスキップ可）。

- Phase 1（必須）: プロダクト名・キャッチコピー・概要
- Phase 2（必須）: 解決したい課題
- Phase 3（必須）: ターゲットユーザー（ペルソナ）
- Phase 4（必須）: MVP の機能候補（P0/P1/P2）
- Phase 5〜7（任意）: 差別化ポイント / 技術スタック / 非機能要件・成功指標

**手動で書きたい場合**: テンプレート [docs/ideas/initial-requirements.md](docs/ideas/initial-requirements.md) の `{...}` プレースホルダーを直接置き換えてください。記入例は [docs/ideas/initial-requirements.example.md](docs/ideas/initial-requirements.example.md) を参照。

### 3. 永続ドキュメントの作成

Claude Code を起動し、`/setup-project` を実行します。

```bash
claude
> /setup-project
```

`docs/ideas/` の内容を元に、以下の6つのドキュメントを対話的に作成します。

- `docs/product-requirements.md` — プロダクト要求定義書（PRD）
- `docs/functional-design.md` — 機能設計書
- `docs/architecture.md` — アーキテクチャ設計書
- `docs/repository-structure.md` — リポジトリ構造定義書
- `docs/development-guidelines.md` — 開発ガイドライン
- `docs/glossary.md` — 用語集

### 4. ドキュメントレビュー

```bash
> /review-docs
```

`doc-reviewer` サブエージェントが完全性・具体性・一貫性・測定可能性の観点でレビューします。

### 5. ヘッドレスモードで MVP（Minimum Viable Product）を開発

`prompt.md` に実装指示を記述し、Claude Code をヘッドレスモード（`-p`）で実行して一括実装します。

```bash
cat prompt.md | claude -p --dangerously-skip-permissions \
    --output-format stream-json \
    --verbose \
    --model claude-sonnet-4-6 2>&1 | tee output.jsonl
```

- `--dangerously-skip-permissions`: 権限プロンプトを全てスキップ（自動実行用）
- `--output-format stream-json` + `--verbose`: 進捗を JSON ストリームで出力
- `tee output.jsonl`: 標準出力をファイルにも保存し、後から実行ログを確認可能

## 提供されるスラッシュコマンド

複数の Skill を順序立てて呼ぶワークフロー、または独自ロジックを持つコマンドのみを Command として定義しています。単機能の Skill は下表（提供される Skill）に集約し、ユーザーは `/<skill-name>` で直接起動できます。

| コマンド | 説明 |
| -------- | ---- |
| `/setup-project` | 初回セットアップ: 6つの永続ドキュメントを対話的に作成 |
| `/review-docs` | ドキュメントの詳細レビューをサブエージェントで実行 |
| `/add-feature [機能名]` | 新機能を既存パターンに従って、完全に無停止で実装 |

## 提供される Skill

Skill は `/<skill-name>` で直接起動できるほか、Claude が文脈から判断して自動的に呼び出すこともあります。

| Skill | 用途 |
| ----- | ---- |
| `draft-idea` | 対話形式でアイデアメモ (`docs/ideas/initial-requirements.md`) を作成 |
| `prd-writing` | プロダクト要求定義書の作成 |
| `functional-design` | 機能設計書の作成 |
| `architecture-design` | アーキテクチャ設計書の作成 |
| `repository-structure` | リポジトリ構造定義書の作成 |
| `development-guidelines` | 開発ガイドラインの作成 |
| `glossary-creation` | 用語集の作成 |
| `steering` | 作業計画・タスクリストの記録 |
| `save-prompt-log` | やり取りを `docs/prompt/YYYY-MM-DD-{トピック}.md` に構造化して保存 |

## サブエージェント

| エージェント | 用途 |
| ------------ | ---- |
| `doc-reviewer` | ドキュメントの品質レビューと改善提案 |
| `implementation-validator` | 実装コードの品質検証とスペック整合性確認 |

## 必要な環境

- [Claude Code](https://docs.claude.com/en/docs/claude-code) がインストール済みであること
- Python 3（`save_prompt_log.py` フックの実行に使用）

> Claude Code をローカルにインストールしたくない場合は、後述の **Dev Container** を利用するとコンテナ内に自動でセットアップされます。

## Dev Container での開発（任意）

ローカル環境を汚さずに開発したい場合は、Dev Container を使うことで Docker コンテナ内で Claude Code を実行できます。Claude Code・Node.js などの依存はコンテナ内に自動でインストールされるため、ホスト側にインストールする必要はありません。

### 必要なもの

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)（起動済みであること）
- VS Code 拡張機能: [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### 手順

1. VS Code でこのリポジトリを開く
2. コマンドパレット（`F1` または `Ctrl+Shift+P`）から **Dev Containers: Reopen in Container** を実行
3. 初回はイメージのビルドに数分かかります
4. コンテナ起動後、VS Code 内のターミナルで `claude` を実行すれば Claude Code が使えます

### コンテナに含まれるもの

[.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) で定義しています。

- Debian Bookworm ベースイメージ
- Node.js LTS
- Claude Code（Anthropic 公式の devcontainer feature 経由で自動インストール）

> プロジェクトに合わせて `devcontainer.json` の `name` および `workspaceFolder` を書き換えることを推奨します。

## ライセンス

本プロジェクトには、Generative Agents が公開している
「claude-code-book」の一部コードを利用・改変しています。

元リポジトリ：
<https://github.com/GenerativeAgents/claude-code-book>

当該コードは MIT License のもとで提供されています。
詳細は [LICENSE](LICENSE) ファイルをご参照ください。
