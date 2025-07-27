// ソケットのクライアントを作成
const socket = require('net');
const client = new socket.Socket();

// コンソール入出力を使用するためのライブラリ
const readline = require('readline');

// ソケットのパスを指定
const socketPath = "./socket.txt";

// リクエストのテンプレート作成
const request = {
    jsonrpc: "2.0",
    method: "",
    params: [],
    params_type: [],
    id: 1
}

/**
 * ユーザーからの入力を待ち、入力された内容を返す
 * @param {string} question 質問文
 * @returns {Promise<string>} ユーザーの入力
 */
function readInput(question) {
    // プロンプトを表示してユーザーの入力を待つ
    return new Promise((resolve) => {
        const rl = readline.createInterface({
            // コンソールラインで入出力
            input: process.stdin,
            output: process.stdout
        });
        // ユーザーに質問を表示
        rl.question(question, (answer) => {
            // 入力された内容を解決し、リードラインを閉じる
            rl.close();
            resolve(answer);
        });
    });
}

// メイン関数を非同期で実行
// ユーザーからの入力を待ち、ソケットを通じてサーバーにリクエストを送信
// サーバーからの応答を受け取る
// エラー処理も含める
(async function main() {
    try {
        // ユーザーからメソッド名を取得
        const method = await readInput("メソッド名を入力してください: ");
        request.method = method;

        // ユーザーからパラメータを取得
        const params = await readInput("パラメータをカンマ区切りで入力してください: ");
        // パラメータを配列に変換
        request.params = params.split(',').map(param => param.trim());

        // パラメータの型を取得
        const params_type = await readInput("パラメータの型を入力してください: ");
        request.params_type = params_type.split(',').map(param_type => param_type.trim());

        // ソケットID設定
        request.id = Math.floor(Math.random() * 1000000);

        // ソケットを接続
        client.connect(socketPath, () => {
            console.log('サーバーに接続しました。');
            // リクエストをJSON文字列に変換して送信
            client.write(JSON.stringify(request), "utf-8");
        });

        // サーバーからのデータ受信処理
        client.on('data', (data) => {
            const response = JSON.parse(data.toString("utf-8"));
            console.log('サーバーからの応答:', response);
            client.destroy(); // データ受信後、ソケットを閉じる
        });

    } catch (error) {
        console.error('エラー:', error);
    }
})();
