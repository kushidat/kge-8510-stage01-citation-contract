# 8510 Stage01 V02 citation-contract source-only development release


## 公開後の検証情報（2026-11-05）

**公開済みのv0.2.0 ZIPに必要な依存モジュールが欠落していることが判明しました。** 配布ZIPのみを用いたStreamlit AppTestは \`ModuleNotFoundError: No module named 'kge_v11_spool_bridge_v0_1'\` でFAILです。GitHub Release自体と元のZIPのバイト列・タグは変更していません。

- [元ZIP単体の実行失敗を記録したQA](https://github.com/kushidat/kge-8510-stage01-citation-contract/actions/runs/41870617179)
- [依存モジュールを復元した隔離候補の起動・停止・無効化GUI検証](https://github.com/kushidat/kge-8510-stage01-citation-contract/actions/runs/41872782019)
- [QA修復ブランチ（検査コード・日本語マニュアル入り候補の作成コード）](https://github.com/kushidat/kge-8510-stage01-citation-contract/tree/qa/8510-release-certification-20261105)
- [公開後の監査報告](https://github.com/kushidat/kge-8510-stage01-citation-contract/blob/qa/8510-release-certification-20261105/qa/INCIDENT_QA_REPORT_JA_20261105.md)

修復候補のPASSは**隔離・無効化プレビューの限定的な技術試験**です。実Provider送信、8504 G4受入、Mac実機、正式8510 v1.0との統合、科学的妥当性は未検証です。**公開済みv0.2.0を完成した単独動作アプリとして配備しないでください。**



- Version: `8510-stage01-v0.2.0` (independent pre-release label; NOT 8510 v1.0.1/v1.1/v1.2)
- Formal 8510 v1.0 is **not replaced, integrated or deployed**.
- Contents: source code copied read-only from pinned, already-existing Stage01 V02 isolated development archives only.
- No BYOK key/value, SQLite, logs, runtime state, training data, weights, test/validation/withheld/PRIMARY_TEST datasets, or frozen formal app code is included.
- Stage01 V01: one genuine Provider call succeeded; the 8504 G4 citation authorization gate held 4 of 13 citations.
- Stage01 V02: isolated preview and synthetic technical checks only; new live Provider response/G4 acceptance NOT verified.
- No re-send of the old V01 request is authorized; no scientific explanation or candidate validity is established by this release.
- Runtime, dependencies, scientific/clinical suitability, and external API permissions NOT guaranteed.
- PRIMARY_TEST_EMBARGO=ACTIVE. Formal research source and evaluation status remain unchanged.
- Copyright/licensing: this source publication does not assert a new license for third-party dependencies or research datasets.

## Pinned input snapshots

- `contract_v02`: `STAGE01_CONTRACT_FIRST_V02_SOURCE_ONLY_20261104.zip` SHA256 `86bee05278c142a4650d0d8b434bc5f1cde4c63eaac0350d222f425e60a51873` (read-only input, original ZIP not published)
- `gui_v02_fix1`: `STAGE01_V02_UI_WIRING_FIX1_SOURCE_ONLY_20261104.zip` SHA256 `e2888272f0c8b32b7c24109952725826680c32ba41587972cb75cdb83c551e6b` (read-only input, original ZIP not published)
- `input_bridge_v02`: `STAGE01_V02_INPUT_BRIDGE_20261104_V01.zip` SHA256 `aaa610cb340aa4416b2b39f49ee13ffab4cb2237a20df576221aa856bfbff893` (read-only input, original ZIP not published)

## Included source files

- `source/contract_v02/stage01_citation_contract_v02.py` — 17625 bytes, SHA256 `3d5134043bf8a6e96fd21008c6b1b7afa56a36aadf7d4fbf7a1c49180c3cefc5`
- `source/contract_v02/stage01_contract_bridge_v02.py` — 18314 bytes, SHA256 `425735a3986762c0f688cc645269108c55cd44bd9c764ccd74f2d2df097d8348`
- `source/contract_v02/stage01_contract_ui_v02.py` — 8933 bytes, SHA256 `8c8e6e8c740c622dbd46a34ff3106f5486204431fd493a9fae23ebda86affe08`
- `source/gui_v02_fix1/stage01_citation_contract_v02.py` — 18646 bytes, SHA256 `ab931c46a2df08f391bdb1ad65ed282f92dd9a84fbfae6e16901a0dc5c11e6a3`
- `source/gui_v02_fix1/stage01_contract_8504_compat_v02.py` — 1237 bytes, SHA256 `8155f58cd1ac9c9a0686b184f63fd5cfc688e999b4de83723d1b1157e3679f90`
- `source/gui_v02_fix1/stage01_contract_bridge_v02.py` — 18314 bytes, SHA256 `425735a3986762c0f688cc645269108c55cd44bd9c764ccd74f2d2df097d8348`
- `source/gui_v02_fix1/stage01_contract_ui_v02.py` — 8933 bytes, SHA256 `8c8e6e8c740c622dbd46a34ff3106f5486204431fd493a9fae23ebda86affe08`
- `source/gui_v02_fix1/streamlit_8510_stage01_v02_contract_review_20261104.py` — 10341 bytes, SHA256 `e8d025949d8115887269dc03e98d0aa6e5291fd9a7389ede09da9fe2d2be2306`
- `source/input_bridge_v02/STAGE01_V02_8504_TO_8510_APPROVED_INPUT_TRANSFER_20261104_V01.py` — 11208 bytes, SHA256 `1b4fde7a50e53065bb43eeb1249fe9c7fe40b1d3ba23cb90f485bd9141c23335`

## 操作ガイド / Operations (Japanese)

- [8510 Stage01 V02 操作ガイド（起動・停止・制限・テスト状態）](docs/OPERATIONS_JA_8510_STAGE01_V02.md)
- **Source-only pre-release**: Public ZIP alone is **not a tested runnable app**. Its standalone start/stop and real-provider end-to-end behavior are **NOT_TESTED**. Do not deploy or replace formal 8510 v1.0.
