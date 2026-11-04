# 8510 Stage01 V02 公開後品質監査・是正検証報告（2026-11-05 JST）

## 1. 公開原本と変更禁止範囲

- 既存Release: https://github.com/kushidat/kge-8510-stage01-citation-contract/releases/tag/8510-stage01-v0.2.0
- 公開日時: 2026-11-05 01:17:53 JST
- 既存公開ZIP: `KGE_8510_STAGE01_V02_SOURCE_ONLY_20261105.zip`
- 既存ZIP: 41,353 bytes / SHA256 `bf68b4176dfb8c05295dab1c7636307ac775a872d7b660cfd4b22517ffad9f26`
- 既存tag commit: `cf5974ee83a396ca0830bb66118ba03607393cc2`
- 旧タグとassetは**同一バイトのまま保全**。正式8510 v1.0、8504、8501などの既存アプリ、データ、Dockerを変更しない。

## 2. 公開前の必須試験不備と実測された欠陥

公開時点で公開ZIPを単体で実行する試験と終了試験が実施されていなかったことは、品質管理上の重大な不備である。これを事後試験で公開前のPASSと書き換えない。

- https://github.com/kushidat/kge-8510-stage01-citation-contract/actions/runs/41870484607 — 原本ZIP取得・ハッシュ・構文・HTTP healthのみPASS。ただしHTTP healthはStreamlit画面コードの実行成功を示さない。
- https://github.com/kushidat/kge-8510-stage01-citation-contract/actions/runs/41870617179 — 原本ZIP単独でStreamlit AppTestを実行し、`ModuleNotFoundError: No module named 'kge_v11_spool_bridge_v0_1'` により**FAIL**。公開ZIPは単体実行に必要な依存ファイルが欠落。
- 欠落モジュールは2026-11-04引き継ぎ原本内で追跡し、17,372 bytes / SHA256 `e7d89291ab6286b008d91ef0b50b2def4587e879a091de69e7b4222685be00d3` と照合。

## 3. 原本を改変しない隔離修復候補の事後技術試験

GitHub branch: [qa/8510-release-certification-20261105](../tree/qa/8510-release-certification-20261105)

**最終PASS run:** [GitHub Actions #41875010391](https://github.com/kushidat/kge-8510-stage01-citation-contract/actions/runs/41875010391)

- run head commit `90743692fb161b80fb5a1c4d2d477ecc55f77045`
- Linux `archive-and-preview`: success
- macOS `macos-smoke`: success
- QA候補名 `8510_STAGE01_V02_DISABLED_PREVIEW_QA_CANDIDATE.zip` （**GitHub Actions artifact**。Release公開ではない）
- 候補ZIP: **28,731 bytes**, SHA256 `fc57cc08ee11e5b5e68102744d2442c8f24d79389dc0e9b5d78b90e97227f9bd`
- 内部対象: 5つのStage01 V02 GUI Pythonモジュール、SHA追跡したspool module、実行スクリプト、日本語利用・起動・終了ガイド、依存バージョン固定テキスト、SHA256/サイズ/CRC manifest
- 候補ZIPの全メンバー許可リスト・manifest、構文、既知形状の秘密文字列スクリーニング: PASS（全秘密不存在の証明ではない）
- AppTestによる画面スクリプトの実行・画面要素生成: PASS
- `STAGE01_V02_RUNTIME_DISABLED`表示: PASS
- 有効なSEND/APPROVE操作の不存在: PASS
- Python subprocessでStreamlit起動、HTTP health応答、停止: PASS
- ZIPに同梱した起動スクリプトのLinux実行・停止: PASS
- Chromiumによる実ブラウザ画面描画・安全制限・スクリーンショット取得・停止: PASS
- macOS runner (Python 3.12)でのGUI AppTest、起動スクリプトHTTP起動・停止: PASS
- 過去のGitHub CI失敗も隠さず保全しており、合格runの機能範囲は**無効化プレビュー**のみ。

## 4. 未実施・合格を宣言できない必須項目

| 試験項目 | 検証状態 |
|---|---|
| ユーザー研究室Macの実際の最終導入・起動/停止 | NOT_TESTED |
| 8510 V02の実Provider API呼出し | NOT_TESTED |
| 8504の真正新規承認要求→8510→8504 G4返送・受入 | NOT_TESTED / HOLD |
| 旧V01のG4拒否（13引用のうち4不許可）を解消した実測 | NOT_ESTABLISHED |
| `PRIMARY_TEST`、validation/test/withheld非アクセスのOSレベル実証 | NOT_ESTABLISHED |
| 正式8510 v1.0への統合・置換 | NOT_PERFORMED（禁止条件を維持） |
| KGE候補の生物学的根拠と科学的妥当性 | NOT_ASSESSED |

**結論**: 2026-11-05の事後検証により、公開原本の単独動作欠陥を再現し、限定的なLinux/macOS無効化プレビュー修復候補の起動・画面・停止を技術的に検証した。**完全機能の8510最新版が受入検証を通過したという結論ではない。** 新しい正式なフル機能Releaseを自動公開しない。技術的PASSを科学的成果とは呼ばない。

## 5. 利用方法・証拠

- QAブランチ: https://github.com/kushidat/kge-8510-stage01-citation-contract/tree/qa/8510-release-certification-20261105
- 最終Linux/macOS CIのrun: https://github.com/kushidat/kge-8510-stage01-citation-contract/actions/runs/41875010391
- runのArtifacts欄から `8510-stage01-v02-disabled-preview-qa-candidate` と `8510-stage01-v02-browser-evidence`、各QAログを取得可能（GitHub認証が必要な場合あり）。
- 上記候補ZIPに含まれる `README_FIRST_JA.md` に隔離フォルダへの導入・起動・Control-C終了、操作範囲、障害時の禁止事項を記載。
- 旧Releaseを新ZIPに置換しない。事後のQAと公開当時の安全性を混同しない。
