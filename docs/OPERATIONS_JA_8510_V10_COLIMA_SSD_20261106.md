# 8510 V10 操作マニュアル：起動・終了・Colima外付けSSD（2026-11-06）

公開版の必須同梱文書。既存の正式8510（port 8510）と隔離候補V10（port 18520）は別。**このファイル自体は正式版Releaseの承認を意味しない。** 既済Macテストの再実行は要求しない。

## 1. 対象原本（バイト無変更）

- V10 ZIP: SHA256 `ac65a3205b69e9bdd703a96946fedc030192c51a8fb423c0086746dcf296496f`, 328442 B
- FIX1 ZIP: SHA256 `a6daa4d6c9c6e5a7358b726e0d655fb514a9d7054b5e1138c5efe8c4d481f3c4`, 9083 B
- FIX2 ZIP: SHA256 `481fe059b98b7c07b1e3ba0545791a03fb318a03bd63f79057cc53563d719a0f`, 6926 B
- FIX2A ZIP: SHA256 `f760e1907da872bc57bfe33106e4dc719bdea0411525e818b96edbbfcd70a6d8`, 7455 B

Macの既存・無上書き配置先：`/Users/kushidatatsuya/projects/mondo_eval/release_records/8504_8510/isolated/` 以下の、各原本ZIPと同名ディレクトリ。保存済みの原本は上書きせず、SHA照合のみ実施。

## 2. Colima用SSDの接続・VM起動（運用再開時のみ）

SSD `COLIMA_SSD` をMacへ物理的に接続し、macOSでマウントされてから実行。**GitHub公開作業のためにはSSDを再接続しない。**

```sh
cd "$HOME"
diskutil info /Volumes/COLIMA_SSD
test -d /Volumes/COLIMA_SSD/colima_runtime/default || { echo HOLD_SSD_NOT_MOUNTED; return 1; }
export COLIMA_HOME=/Volumes/COLIMA_SSD/colima_runtime
export COLIMA_CACHE_HOME=/Volumes/COLIMA_SSD/colima_cache
export LIMA_HOME="$COLIMA_HOME/_lima"
colima list
```

既存profile `default` が Stopped のときのみ、次を1回実行。Runningなら起動コマンドを繰り返さない。Brokenなら停止して診断し、VM再生成・SSD強制解除はしない。

```sh
colima start --profile default
colima status
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

## 3. 8510 V10の状態と起動

```sh
docker inspect --format '{{.State.Status}}' kgllm-8510-generic-llm-biology-v10
```

- `running` の場合：新しいstart/restartをせず既存FIX2Aで読取り専用の確認をする。
- `exited`/`created` の場合：**FIX1 --startとFIX2A --restartを無条件に実行しない**。前者は同名コンテナ存在を拒否し、後者はRunning前提。既存コンテナを削除せず、正規の停止状態復旧手順が必要。
- `No such object` の場合：初回起動のみ、既存正式8510の稼働・原本SHA・ポート空きを確認し、FIX1 --check → FIX1 --startを1回行う。

実行状態の読取り専用確認とGUI:

```sh
FIX2A="$HOME/projects/mondo_eval/release_records/8504_8510/isolated/8510_V10_RESTART_OWNER_FIX2A_HTTP_WAIT_20261106"
python3 "$FIX2A/RESTART_8510_V10_SAFE_OWNER_FIX2A_20261106.py" --verify
open http://127.0.0.1:18520
```

初回構築・V10コンテナ未存在の場合のみ:

```sh
FIX1="$HOME/projects/mondo_eval/release_records/8504_8510/isolated/8510_V10_STARTUP_GUARD_FIX1_20261106"
python3 "$FIX1/START_8510_V10_LAUNCH_GUARD_FIX1_20261106.py" --check
python3 "$FIX1/START_8510_V10_LAUNCH_GUARD_FIX1_20261106.py" --start
python3 "$FIX1/START_8510_V10_LAUNCH_GUARD_FIX1_20261106.py" --verify-running
```

本人が明示的に同意しV10だけの再起動が必要なときは、V10がRunningの状態で `python3 "$FIX2A/RESTART_8510_V10_SAFE_OWNER_FIX2A_20261106.py" --restart --accept-ephemeral-reset`。BYOK tmpfsに置かれた一時キーと未保存セッションは消失し得る。**公開目的で再起動しない。** 既済FIX2実機停止/復旧とFIX2Aのreadiness修正は区別する。

## 4. Colima終了とSSDの安全な取り外し

8510出力Markdown/JSON等を取得済みと確認し、すべてのColima上アプリを停止してよい場合に限る。8504はMacホスト側の別Streamlitプロセスで、Docker一覧に出ないことがある。

```sh
cd "$HOME"
export COLIMA_HOME=/Volumes/COLIMA_SSD/colima_runtime
export COLIMA_CACHE_HOME=/Volumes/COLIMA_SSD/colima_cache
export LIMA_HOME="$COLIMA_HOME/_lima"
colima stop
colima list
```

`colima list`でdefaultが**Stopped**であることを確認し、SSDを参照する作業を終了した後だけ実行する。

```sh
sync
diskutil eject /Volumes/COLIMA_SSD
```

eject成功を確認してから物理的に取り外す。失敗時は**強制アンマウントやケーブル抜去をしない**。`docker rm` / `prune` / `colima delete` / `down -v`は禁止。Colima停止後、BYOK一時領域の復旧・キー再登録が必要な場合がある。

## 5. GitHub正式公開チェック

V10/FIX1/FIX2/FIX2Aの4原本、無上書き配置スクリプト、本運用マニュアル、SHA256とZIP検査、ライセンス・出典範囲を公開物に含め、公開URL・タグ・アセット数・サイズ・SHAを再取得して照合する。**Source-only Pre-releaseを完成した正式Releaseと称しない**。正式な版番号・採否・公開時刻は所有者が決定。現行工程①→④→②→③、管理正本V13、既存正式8501/8504/8510は変更しない。

科学的限界：技術的PASS・LLM文章・GO一致はKGE上位順位の形成理由や病態再現率を証明しない。PRIMARY_TEST/TEST/WITHHELDとBYOK秘密は公開しない。
