# 8510 Stage01 V02（source-only開発版）操作ガイド

対象タグ：`8510-stage01-v0.2.0`（GitHub **pre-release**）

> **重要**：このReleaseは完成したアプリではなく、Pythonソースのみの開発用スナップショットです。公開ZIPには、一般環境向けインストーラー、依存環境一式、起動・終了スクリプト、実データ、APIキーは同梱されていません。**公開ZIP単体の起動・終了は未検証**です。正式8510 v1.0は変更・置換していません。

## 1. ダウンロードと真正性確認（読み取り専用）

GitHub Releaseの `KGE_8510_STAGE01_V02_SOURCE_ONLY_20261105.zip` をダウンロード後、macOSターミナルで次を実行します。

```bash
cd "$HOME/Downloads"
shasum -a 256 KGE_8510_STAGE01_V02_SOURCE_ONLY_20261105.zip
unzip -l KGE_8510_STAGE01_V02_SOURCE_ONLY_20261105.zip
```

期待するSHA256：`bf68b4176dfb8c05295dab1c7636307ac775a872d7b660cfd4b22517ffad9f26`。異なる場合は展開・実行しないでください。ZIPのPythonファイルを直接 `python` / `streamlit run` で起動しても、公開版としての動作は保証されません。

## 2. 何が利用できるか

- `source/contract_v02/`：引用識別子契約とBridge/UIの原本スナップショット。
- `source/gui_v02_fix1/`：隔離GUI用の修正版ソースと8510 Streamlit entrypoint。
- `source/input_bridge_v02/`：新しい8504 V02の承認済み入力を8510へ移すためのソース。
- いずれも**開発者向けソース**です。単独実行を保証する依存パッケージ、研究データ、KGE環境、運用コマンドは付属しません。

## 3. 研究室内の既設「無効化プレビュー」の確認・表示

ここからの操作は、2026年11月4日にMacで起動確認された**既設の隔離プレビュー専用**です。GitHubで公開されたZIPから直接起動する操作ではありません。既設コンテナ名は `kgllm-stage01-v02-contract-gui-preview-v01` です。

まずDocker/Colimaの接続先と対象コンテナ名を**読み取り専用**で確認します。

```bash
docker context show
docker ps -a --filter 'name=^/kgllm-stage01-v02-contract-gui-preview-v01$' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

- **既にRunningの場合**：再起動せず、`docker port kgllm-stage01-v02-contract-gui-preview-v01` で表示される localhostポートを確認してブラウザで開きます。2026年11月4日の記録では `http://127.0.0.1:32770` でしたが、このポートは固定ではありません。
- **Stoppedの場合**：既存のSHA固定済みコード・マウント・起動設定の照合が必要です。照合後に限り、対象名が一致する隔離コンテナだけを `docker start kgllm-stage01-v02-contract-gui-preview-v01` で再開する方法があります。ただし、この再開手順は**実機未検証**です。
- **コンテナが存在しない場合**：公開ZIPでは起動できません。以前の研究室内専用launcher `START_STAGE01_V02_GUI_SAFE_PREVIEW_NO_OVERWRITE_20261104_V01.sh` とSHA固定原本が必要です。既設正式8510コンテナをコピー・置換して代用しないでください。既済記録ではlauncherの `--check` → `--start` により隔離プレビューが起動していますが、公開ZIPではlauncherを配布していません。

GUIで確認可能だった内容：8510 Stage01 V02のタイトル、隔離BYOKの案内、未設定ユーザーID、`STAGE01_V02_RUNTIME_DISABLED`、既存V01要求を再送しない旨の警告。**ユーザー承認・Provider送信・科学的解釈の実行を保証する画面ではありません。**

## 4. 終了方法（既設隔離プレビューのみ）

ブラウザを閉じてもサーバーは終了しません。先に対象が正しいことを `docker ps` で確認し、**他の正式アプリが稼働しているコンテナは停止しない**でください。隔離プレビューの停止操作は次のとおりです。

```bash
docker stop kgllm-stage01-v02-contract-gui-preview-v01
docker inspect -f '{{.State.Running}}' kgllm-stage01-v02-contract-gui-preview-v01
```

停止後の期待表示は `false` です。この停止手順自体のMac実機確認は**未実施**です。正式8510、8504、8501、8502のコンテナには手を触れないでください。停止前に対象名が一致しない場合は実行しないでください。

## 5. 公開時点のテスト状況（2026年11月5日）

| 対象 | 検証状態 | 根拠・限界 |
|---|---|---|
| 公開assetの存在・SHA256 | PASS | GitHub Release API上の41,353 bytesとSHA256一致。Mac側の再ダウンロードSHA一致ログあり |
| Stage01 V02の既設隔離プレビュー起動 | PASS（過去の別環境） | 2026-11-04 Mac実行ログ。5/5ソースSHA照合、API呼出しなし |
| Stage01 V02の既設GUI表示 | PASS（過去の別環境） | 2026-11-04 Chrome画面確認。無効化表示のみ |
| 公開ZIP単体のインストール・起動 | **NOT_TESTED** | ランチャー・依存環境・実データ非同梱。単独動作を保証しない |
| 公開ZIPを使った正常終了・再起動 | **NOT_TESTED** | 実機での停止/再開記録なし |
| 新しいV02の実Provider→G4通過 | **NOT_TESTED / HOLD** | 旧V01は引用13件中4件不許可。旧要求の再送禁止 |
| 正式8510 v1.0への統合 | **NOT_PERFORMED** | 正式アプリ・Dockerは変更禁止 |
| PRIMARY_TEST等へのOSレベル非アクセス証明 | **NOT_ESTABLISHED** | `PRIMARY_TEST_EMBARGO=ACTIVE`、保護領域へのアクセス禁止 |

## 6. 禁止・注意事項

APIキー、秘密、SQLite、研究原本、model weights、test/validation/withheld/PRIMARY_TESTを公開リポジトリへ追加しないでください。実Provider送信、旧V01要求の再送、8504 G4の無断通過、正式8510への統合・置換、既存コンテナの再構築は行わないでください。実際の疾患–マウス候補の科学的妥当性は検証されていません。

**現在の配布形態は「ソース閲覧・静的参照用」です。** 起動・終了・基本操作を実機で検証し、依存環境・安全境界・実行手順を同梱した配布版については、別途検証済みのリリースが必要です。既存タグやassetを検証前の完成品として扱わないでください。
