# 8510 Stage01 V02 — 公開後の独立技術監査（2026-11-05 JST）

## 公開原本の識別
- GitHub: https://github.com/kushidat/kge-8510-stage01-citation-contract/releases/tag/8510-stage01-v0.2.0
- 公開日時: 2026-11-05 01:17:53 JST（GitHub API: 2026-11-04T16:17:53Z）
- Git tag: `8510-stage01-v0.2.0`、GitHub Release `prerelease=true`
- Asset: `KGE_8510_STAGE01_V02_SOURCE_ONLY_20261105.zip`
- Asset size: 41,353 bytes
- SHA256: `bf68b4176dfb8c05295dab1c7636307ac775a872d7b660cfd4b22517ffad9f26`
- tag commit: `cf5974ee83a396ca0830bb66118ba03607393cc2`

## 公開前検証の不足
公開前には公開ZIP単体によるStreamlit画面コードの実行、正常終了、API/8504 G4の実際の全経路テストが実施されていなかった。以前の「隔離プレビュー GUI表示PASS」は別環境・無効化モードの記録であり、公開ZIP単体の実行可能性を保証していなかった。

## 今回の事後検証
### GitHub Actions: archive and HTTP-only smoke
- https://github.com/kushidat/kge-8510-stage01-citation-contract/actions/runs/41870484607
- Status: `success`。
- 公開ZIPを再ダウンロード、サイズ・SHA256・ZIP CRC・Python 9ファイル構文を検証、隔離環境でStreamlit HTTP /_stcore/health=200、停止確認。
- 限界：HTTPヘルスはStreamlit画面スクリプトの実行成功を意味しない。

### GitHub Actions: Streamlit AppTest
- https://github.com/kushidat/kge-8510-stage01-citation-contract/actions/runs/41870617179
- Status: `failure`。
- 公開ZIPの画面スクリプトをAppTestで実行し、`ModuleNotFoundError: No module named 'kge_v11_spool_bridge_v0_1'` を確認。
- `RELEASE_QA_STATUS=FAIL`。公開ZIPのみでは必要モジュールのimportを完了できない。

## 追加の原本追跡
引き継ぎZIP内に同梱された2026-11-04原本の子ZIP `KGE_STAGE01_REAL_PROVIDER_ONE_CANDIDATE_SOURCE_DELTA_20261104_V01.zip` には、欠落しているモジュール `kge_v11_spool_bridge_v0_1.py` が存在する（17,372 bytes、SHA256 `e7d89291ab6286b008d91ef0b50b2def4587e879a091de69e7b4222685be00d3`）。これは公開ZIPに存在すること、正式版で動作すること、公開可能であることを自動的に証明しない。

## 認定できないこと
- 新V02による実Provider通信と8504 G4受入
- 公開ZIPの完全な単独起動・操作・正常終了
- ユーザーMacおよび研究室内Docker環境での動作・安全境界
- test/validation/withheld/PRIMARY_TESTへのOSレベル非アクセス
- KGE候補の生物学的妥当性・科学的説明

## 公開判断の是正
- 既存公開タグ・assetは履歴・証拠として保全する。
- 新版公開には、機能一覧・全依存ファイルの出典とSHA、実際の画面コード/AppTest、起動停止、入力と例外処理、研究室内の既設環境、API/G4、安全境界、マニュアルを包含した試験証拠を要求する。
- 後日得られた結果を公開前に取得したものとして報告しない。
- 個別技術試験PASSを、科学的成果や総合受入PASSと読み替えない。

本資料は公開後の技術的検証報告であり、ユーザーの実Mac環境に接続していない。完全実機E2E受入証明ではない。