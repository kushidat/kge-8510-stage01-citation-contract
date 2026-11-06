# 8510 isolated V10 + FIX1/FIX2A source-only prerelease

- Isolated 8510 V10 source: manual 8504 Evidence JSON intake, BYOK GPT-6 Luna provisional interpretation, and paired JSON/Markdown downloads.
- Includes FIX1 startup guard, FIX2A bounded post-restart readiness wait and temporary-storage owner recovery script.
- Based on byte-pinned 2026-11-06 V10 (SHA256 ac65a3205b69e9bdd703a96946fedc030192c51a8fb423c0086746dcf296496f), FIX1 (SHA256 a6daa4d6c9c6e5a7358b726e0d655fb514a9d7054b5e1138c5efe8c4d481f3c4), and FIX2A (SHA256 f760e1907da872bc57bfe33106e4dc719bdea0411525e818b96edbbfcd70a6d8).
- Tests 1–6: scoped technical PASS in existing ledger. FIX2 real Mac restart recovered after HTTP readiness, but single-command completion failed; FIX2A readiness wait passed offline checks 10/10; a new FIX2A Mac restart was deliberately not repeated.
- **Not** a formal 8510 v1.0 replacement, complete end-to-end user acceptance, scientific validation, or multi-user deployment. Existing 8501/8504/formal 8510 are unchanged.
- No API secrets, private input, actual LLM outputs, model weights, frozen TRAIN triples, validation/test/withheld or PRIMARY_TEST data.
- PRIMARY_TEST_EMBARGO=ACTIVE. No inference about ALS–RBRC10811 KGE ranking mechanism is established.
- Public source snapshot; original input ZIP archives remain private. License of this repository applies to materials lawfully licensable by the publisher; external resources and third-party dependencies are not relicensed.

Asset: `KGE_8510_ISOLATED_V10_FIX2A_SOURCE_20261106.zip`
SHA256: `649ecc8940798d5e084e88a1055a1b71276dec3bebe69f5e8cd17110c7e75958`
