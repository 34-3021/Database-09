# API 文档

该文档介绍前后端交互接口

## RESTful API

### Verify Token （验证 Token）

| 方法 | URL                |
| ---- | ------------------ |
| POST | /login/verifyToken |

#### 请求体

| Field | 类型   | 详细 | 必须 |
| ----- | ------ | ---- | ---- |
| token | string |      | 必须 |

#### 响应 (200)

| Field   | 类型    | 详细             |
| ------- | ------- | ---------------- |
| success | boolean | 是否为有效 Token |

---

### Login With Tauth （使用 Tauth 登录）

| 方法 | URL          |
| ---- | ------------ |
| POST | /login/tauth |

#### 请求体

| Field | 类型   | 详细                            | 必须 |
| ----- | ------ | ------------------------------- | ---- |
| token | string | TAuth（第三方平台）提供的 Token | 必须 |

#### 响应 (200)

| Field   | 类型    | 详细               |
| ------- | ------- | ------------------ |
| success | boolean | 是否成功登录       |
| token   | string  | 登录后返回的 token |

---

### Register （注册）

| 方法 | URL              |
| ---- | ---------------- |
| POST | /register/native |

#### 参数

| Name | In  | 详细 | 必须 |
| ---- | --- | ---- | ---- |

#### 请求体

| Field    | 类型   | 详细                        | 必须 |
| -------- | ------ | --------------------------- | ---- |
| username | string | 用户名                      | 必须 |
| password | string | 密码（已经进行一次 sha256） | 必须 |

#### 响应 (200)

| Field   | 类型    | 详细         |
| ------- | ------- | ------------ |
| success | boolean | 是否成功注册 |
| token   | string  | 返回的 token |

---

### Login （登录）

| 方法 | URL           |
| ---- | ------------- |
| POST | /login/native |

#### 请求体

| Field    | 类型   | 详细   | 必须 |
| -------- | ------ | ------ | ---- |
| username | string | 用户名 | 必须 |
| password | string | 密码   | 必须 |

#### 响应 (200)

| Field   | 类型    | 详细         |
| ------- | ------- | ------------ |
| success | boolean | 是否成功登录 |
| token   | string  | 返回的 token |

---

### Convert File （转换文件）

| 方法 | URL      |
| ---- | -------- |
| POST | /convert |

#### 请求体

| Field    | 类型   | 详细                 | 必须 |
| -------- | ------ | -------------------- | ---- |
| markdown | string | 源文档 Markdown 格式 | 必须 |
| target   | string | 目标格式             | 必须 |

#### 响应 (200)

一个 Octet Stream，表示转换后的文件

---

### Upload File （上传文件）

| 方法 | URL     |
| ---- | ------- |
| POST | /upload |

#### 参数

| Name           | In     | 详细 | 必须 |
| -------------- | ------ | ---- | ---- |
| infiniDocToken | header |      | 必须 |

#### 请求体

| Field | 类型 | 详细       | 必须 |
| ----- | ---- | ---------- | ---- |
| file  | file | 上传的文件 | 必须 |

#### 响应 (200)

即表示上传成功

---

### File List （文件列表）

| 方法 | URL       |
| ---- | --------- |
| GET  | /fileList |

#### 参数

| Name           | In     | 详细             | 必须 |
| -------------- | ------ | ---------------- | ---- |
| limit          | query  | 最多返回的个数   | 必须 |
| offset         | query  | 从哪一个开始查询 | 必须 |
| infiniDocToken | header |                  | 必须 |

#### 响应 (200)

| Field      | 类型    | 详细     |
| ---------- | ------- | -------- |
| files      | array   | 文件列表 |
| totalfiles | integer | 文件总数 |

---

### Download File （下载文件）

| 方法 | URL       |
| ---- | --------- |
| GET  | /download |

#### 参数

| Name           | In     | 详细       | 必须 |
| -------------- | ------ | ---------- | ---- |
| seq            | query  | 哪一个文件 | 必须 |
| infiniDocToken | header |            | 必须 |

#### 响应 (200)

一个 Octet Stream，表示下载的文件

---

### Delete File （删除文件）

| 方法 | URL     |
| ---- | ------- |
| GET  | /delete |

#### 参数

| Name           | In     | 详细 | 必须 |
| -------------- | ------ | ---- | ---- |
| seq            | query  |      | 必须 |
| infiniDocToken | header |      | 必须 |

#### 响应 (200)

| Field   | 类型    | 详细         |
| ------- | ------- | ------------ |
| success | boolean | 是否成功删除 |

---

### Search In Files （在文件中搜索）

| 方法 | URL     |
| ---- | ------- |
| GET  | /search |

#### 参数

| Name           | In     | 详细   | 必须 |
| -------------- | ------ | ------ | ---- |
| keyword        | query  | 关键词 | 必须 |
| infiniDocToken | header |        | 必须 |

#### 响应 (200)

| Field  | 类型   | 详细     |
| ------ | ------ | -------- |
| result | object | 搜索结果 |

---

### Get Projects （获取项目列表）

| 方法 | URL          |
| ---- | ------------ |
| GET  | /project/get |

#### 参数

| Name           | In     | 详细 | 必须 |
| -------------- | ------ | ---- | ---- |
| infiniDocToken | header |      | 必须 |

#### 响应 (200)

| Field    | 类型  | 详细     |
| -------- | ----- | -------- |
| projects | array | 项目列表 |

---

### Create Project （创建项目）

| 方法 | URL             |
| ---- | --------------- |
| POST | /project/create |

#### 参数

| Name           | In     | 详细 | 必须 |
| -------------- | ------ | ---- | ---- |
| infiniDocToken | header |      | 必须 |

#### 请求体

| Field        | 类型   | 详细     | 必须 |
| ------------ | ------ | -------- | ---- |
| project_name | string | 项目名称 | 必须 |

#### 响应 (200)

| Field   | 类型    | 详细             |
| ------- | ------- | ---------------- |
| success | boolean | 是否成功创建项目 |
| id      | integer | 项目 ID          |

---

### Delete Project （删除项目）

| 方法 | URL             |
| ---- | --------------- |
| POST | /project/delete |

#### 参数

| Name           | In     | 详细 | 必须 |
| -------------- | ------ | ---- | ---- |
| infiniDocToken | header |      | 必须 |

#### 请求体

| Field      | 类型    | 详细    | 必须 |
| ---------- | ------- | ------- | ---- |
| project_id | integer | 项目 ID | 必须 |

#### 响应 (200)

| Field   | 类型    | 详细             |
| ------- | ------- | ---------------- |
| success | boolean | 是否成功删除项目 |

---

### Rename Project （重命名项目）

| 方法 | URL                          |
| ---- | ---------------------------- |
| POST | /project/rename/{project_id} |

#### 参数

| Name           | In     | 详细    | 必须 |
| -------------- | ------ | ------- | ---- |
| project_id     | path   | 项目 ID | 必须 |
| infiniDocToken | header |         | 必须 |

#### 请求体

| Field    | 类型   | 详细   | 必须 |
| -------- | ------ | ------ | ---- |
| new_name | string | 新名称 | 必须 |

#### 响应 (200)

| Field   | 类型    | 详细               |
| ------- | ------- | ------------------ |
| success | boolean | 是否成功重命名项目 |

---

### Get Paragraphs （获取项目段落）

| 方法 | URL                                 |
| ---- | ----------------------------------- |
| GET  | /project/getparagraphs/{project_id} |

#### 参数

| Name           | In     | 详细    | 必须 |
| -------------- | ------ | ------- | ---- |
| project_id     | path   | 项目 ID | 必须 |
| infiniDocToken | header |         | 必须 |

#### 响应 (200)

| Field      | 类型   | 详细      |
| ---------- | ------ | --------- |
| paragraphs | string | 段落 json |

---

### Get Project Name （获取项目名称）

| 方法 | URL                        |
| ---- | -------------------------- |
| GET  | /project/name/{project_id} |

#### 参数

| Name           | In     | 详细    | 必须 |
| -------------- | ------ | ------- | ---- |
| project_id     | path   | 项目 ID | 必须 |
| infiniDocToken | header |         | 必须 |

#### 响应 (200)

| Field        | 类型   | 详细     |
| ------------ | ------ | -------- |
| project_name | string | 项目名称 |

---

### Save Project

| 方法 | URL                        |
| ---- | -------------------------- |
| POST | /project/save/{project_id} |

#### 参数

| Name           | In     | 详细    | 必须 |
| -------------- | ------ | ------- | ---- |
| project_id     | path   | 项目 ID | 必须 |
| infiniDocToken | header |         | 必须 |

#### 请求体

| Field      | 类型   | 详细      | 必须 |
| ---------- | ------ | --------- | ---- |
| paragraphs | string | 段落 json | 必须 |

#### 响应 (200)

| Field   | 类型    | 详细             |
| ------- | ------- | ---------------- |
| success | boolean | 是否成功保存项目 |

---

### Get Unique Id （获取唯一 ID）

| 方法 | URL                   |
| ---- | --------------------- |
| POST | /settings/getUniqueID |

#### 参数

| Name | In  | 详细 | 必须 |
| ---- | --- | ---- | ---- |

#### 请求体

| Field | 类型   | 详细 | 必须 |
| ----- | ------ | ---- | ---- |
| token | string |      | 必须 |

#### 响应 (200)

| Field     | 类型   | 详细    |
| --------- | ------ | ------- |
| unique_id | string | 唯一 ID |

---

### Get User Settings （获取用户设置）

| 方法 | URL            |
| ---- | -------------- |
| GET  | /user/settings |

#### 参数

| Name           | In     | 详细 | 必须 |
| -------------- | ------ | ---- | ---- |
| infiniDocToken | header |      | 必须 |

#### 响应 (200)

| Field    | 类型    | 详细             |
| -------- | ------- | ---------------- |
| success  | boolean | 是否成功获取设置 |
| settings | object  | 用户设置         |

---

### Set User Settings （设置用户设置）

| 方法 | URL                |
| ---- | ------------------ |
| POST | /user/settings/set |

#### 参数

| Name           | In     | 详细 | 必须 |
| -------------- | ------ | ---- | ---- |
| infiniDocToken | header |      | 必须 |

#### 请求体

| Field   | 类型   | 详细     | 必须 |
| ------- | ------ | -------- | ---- |
| payload | object | 设置列表 | 必须 |

#### 响应 (200)

| Field   | 类型    | 详细         |
| ------- | ------- | ------------ |
| success | boolean | 是否成功设置 |

---

### Get Models （获取模型列表）

| 方法 | URL            |
| ---- | -------------- |
| POST | /llm/getModels |

#### 参数

| Name | In  | 详细 | 必须 |
| ---- | --- | ---- | ---- |

#### 请求体

| Field    | 类型   | 详细 | 必须 |
| -------- | ------ | ---- | ---- |
| endpoint | string |      | 必须 |
| api_key  | string |      | 必须 |

#### 响应 (200)

| Field  | 类型  | 详细     |
| ------ | ----- | -------- |
| （根） | array | 模型列表 |

## WebSocket API

### test （测试对话）

#### 请求体

| Field    | 类型   | 详细       | 必须 |
| -------- | ------ | ---------- | ---- |
| type     | string | 为 test    | 必须 |
| message  | string | 用户的信息 | 必须 |
| endpoint | string |            | 必须 |
| model    | string |            | 必须 |
| key      | string |            | 必须 |

### project （项目对话）

#### 请求体

| Field                     | 类型   | 详细         | 必须 |
| ------------------------- | ------ | ------------ | ---- |
| type                      | string | 为 project   | 必须 |
| project_name              | string | 项目名称     | 必须 |
| paragraph_title           | string | 段落标题     | 必须 |
| paragraph_current_content | string | 段落当前内容 | 必须 |
| user_prompt               | string | 用户要求     | 必须 |
