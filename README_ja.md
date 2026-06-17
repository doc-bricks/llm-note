# llm-note

**llm-note** は LLM エージェント向けのローカルファーストなノートエンジンです。SQLite の思考ログとプレーンテキストのノートブックを、外部サービスなしで使えます。

## 機能

- 構造化ノート、ログブック、カテゴリ、気分値、昇格マーカーを保存。
- 移植しやすいプレーンテキストのノートブックを利用。
- Python または CLI から検索。
- ブレインストーム項目を作成し、あとでタスク、wiki、issue に昇格。
- 6 言語のユーザーメッセージを同梱。

## クイックスタート

```bash
pip install -e .
llm-note --locale ja write "リリース前にプライバシーを確認" --cat release
llm-note --locale ja search プライバシー
```

## ライセンス

[MIT](LICENSE)
