import json
import math
import os
import socket
from typing import Any


# メソッドを集めたクラス
class Method:
    # 10 進数 x を最も近い整数に切り捨て、その結果を整数で返す
    @staticmethod
    def floor(args: list[str]) -> int:
        x: float = float(args[0])
        return math.floor(x)

    # 方程式 rn = x における、r の値を計算する。
    @staticmethod
    def nroot(args: list[str]) -> float:
        x: float = float(args[0])
        return x ** (1 / float(args[1]))

    # 文字列 s を入力として受け取り、入力文字列の逆である新しい文字列を返す。
    @staticmethod
    def reverse(args: list[str]) -> str:
        s: str = args[0]
        return s[::-1]

    # 2 つの文字列を入力として受け取り，2 つの入力文字列が互いにアナグラムであるかどうかを示すブール値を返す。
    @staticmethod
    def validAnagram(args: list[str]) -> bool:
        s1: str = args[0]
        s2: str = args[1]
        return sorted(s1) == sorted(s2)

    # 文字列の配列を入力として受け取り、その配列をソートして、ソート後の文字列の配列を返す。
    @staticmethod
    def sort(args: list[str]) -> list[str]:
        return sorted(args)


# 型変換関数
def convert_params(params: list[str], params_type: list[str]) -> list[Any]:
    # 戻り値の初期化
    converted_params: list[Any] = []
    # パラメータの型に応じて変換
    for param, param_type in zip(params, params_type):
        # int型
        if param_type == "int":
            converted_params.append(int(param))
        # float型
        elif param_type == "float":
            converted_params.append(float(param))
        # bool型
        # 真偽値の場合は、小文字に変換して "true" と一致するかどうかをチェック
        # 一致する場合は True を返す 一致しない場合は False を返す
        elif param_type == "bool":
            converted_params.append(param.lower() == "true")
        # str型
        else:
            converted_params.append(param)
    return converted_params


# 関数集を辞書に格納
methods: dict[str, Any] = {
    "floor": Method.floor,
    "nroot": Method.nroot,
    "reverse": Method.reverse,
    "validAnagram": Method.validAnagram,
    "sort": Method.sort,
}

# デバッグモードの設定
# DEBUG_MODE: bool = True
DEBUG_MODE: bool = False

# 同一コンピューター内通信 AF_UNIX採用
sock: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# ソケットファイルのパス
sock_path: str = "./socket.txt"

# 前回のソケット接続が残っている場合は削除
try:
    os.unlink(sock_path)
except FileNotFoundError:
    pass

# ソケットをバインド
sock.bind(sock_path)

# 接続待ち
sock.listen()

# クライアントからの接続受入（デバッグモードでは無効化）
if not DEBUG_MODE:
    connection, client_address = sock.accept()
else:
    connection = None


def main() -> None:
    try:
        # デバッグ用のテストデータ
        test_requests = [
            {
                "method": "floor",
                "params": ["3.7"],
                "params_type": ["float"],
                "id": 999,
            }
        ]
        request_index: int = 0

        while True:
            if DEBUG_MODE:
                # デバッグモード：テストデータを順番に処理
                if request_index >= len(test_requests):
                    print("全てのテストケースを処理しました")
                    break

                request = test_requests[request_index]
                print(f"テストケース {request_index + 1} を処理中: {request}")
                request_index += 1

                # ここでブレークポイントを設定できます
                print("ブレークポイント: リクエスト処理開始")
            else:
                # データを受信
                data: bytes = connection.recv(1024)

                if not data:
                    print("データがありません")
                    break  # データがない場合はループを抜ける

                # jsonデータをデコード
                request: dict = json.loads(data.decode("utf-8"))

            # 各データを抽出
            method: str | None = request.get("method")
            params: list[str] | None = request.get("params")
            params_type: list[str] | None = request.get("params_type")
            id: int | None = request.get("id")

            # None の場合はループを抜ける
            if method is None or params is None or params_type is None or id is None:
                break

            # クライアントに返すデータ用の辞書
            response: dict = {}

            # メソッドが存在するか確認
            if method not in methods:
                response = {
                    "id": id,
                    "result": "メソッドが存在しません",
                }
            else:
                try:
                    result_params: list[Any] = []
                    # パラメータの型変換
                    if params_type and len(params_type) == len(params):
                        result_params = convert_params(params, params_type)
                    else:
                        result_params = params

                    # メソッドを実行
                    result = methods[method](result_params)
                    response = {
                        "id": id,
                        "result": result,
                    }
                except (ValueError, TypeError) as e:
                    response = {
                        "id": id,
                        "error": f"パラメータの型変換エラー: {str(e)}",
                    }

            if DEBUG_MODE:
                # デバッグモード：テストデータを順番に処理
                print(f"テストケース {request_index} の応答: {response}")
            else:
                # クライアントに応答
                connection.sendall(json.dumps(response).encode("utf-8"))

            # ループを抜ける
            break

    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        # 接続を閉じる
        connection.close()
        sock.close()
        # ソケットファイルを削除
        if os.path.exists(sock_path):
            os.unlink(sock_path)
        print("サーバーを終了しました")


if __name__ == "__main__":
    main()
