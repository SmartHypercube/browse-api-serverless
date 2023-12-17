# browse-api-serverless

一些为 AI 提供打开 URL 的能力的 API，均设计为部署在 AWS Lambda 上的无服务器云函数。

## 部署

安装 [Serverless Framework](https://serverless.com/) 并配置 AWS 凭证，然后在项目根目录下执行 `make`。运行结束后会输出各 API 的 URL。

## 使用

每个 API 都应当使用 `POST` 方法调用，请求体类似如下格式：

```json
{
    "url": "https://example.com/"
}
```

每个 API 成功时都返回类似如下格式的 JSON。如果返回码不是 200，说明这个 API 无法打开指定的 URL。注意：某个 API 能打开某个 URL，并不意味着这个 API 是最佳选择。例如 `browse-text` API 可以打开 YouTube 视频的 URL，但是 `youtube` API 可能是更好的选择。

```json
{
    "truncated": false,
    "template": [
        {"field": "foo", "name": "Foo", "type": "inline"},
        {"field": "bar", "name": "Bar", "type": "inline"},
        {"field": "baz", "name": "Baz", "type": "block"},
        {"field": "qux", "name": "Qux", "type": "block"}
    ],
    "data": {
        "foo": "some text",
        "baz": "some text\nmore text",
        "qux": "some text\nmore text"
    }
}
```

其中 `truncated` 指示是否截断了部分数据以满足 AWS Lambda 的 6MB 返回值大小限制，`template` 列出了 `data` 中所有可能的字段，以及如何格式化以便提供给 AI 模型的建议。

用户可以忽略 `template` 部分，直接以 JSON 格式传递 `data` 给 AI 模型，也可以按 `template` 给出的建议，用类似如下格式拼接字符串：

```plain
Foo: some text

Baz:
some text
more text

Qux:
some text
more text
```
