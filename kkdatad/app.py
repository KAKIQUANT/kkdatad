from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from routes.sql import data_router
from routes.users import user_router
from kkdatad.utils.database import engine
import kkdatad.utils.models as models
from kkdatad.routes.api_keys import api_keys_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")

# Include the financial data routes
app.include_router(data_router)
# Include the user registration routes
app.include_router(user_router)

app.include_router(api_keys_router, prefix="/users", tags=["API Keys"])
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    content = """
    <h1>欢迎使用 KKDataD 数据分发服务</h1>

    <h2>主要目的</h2>
    <p>
        KKDataD 是专为 <strong>KakiQuant</strong> 社区建立的数据分发服务。我们的目标是创建一个自主的数据服务平台，
        设计理念与 <code>rqdatad</code> 相一致，旨在摆脱对昂贵数据服务商的依赖。同时，我们也对外提供服务，实现盈利。
    </p>

    <h2>技术栈</h2>
    <ul>
        <li>
            <strong>SQLite / MySQL</strong>：
            <p>用于用户管理、API Key 验证、数据用量追踪和日志记录。选择轻量级的 SQLite 或者功能更丰富的 MySQL，根据需求灵活使用。</p>
        </li>
        <li>
            <strong>ClickHouse</strong>：
            <p>KakiQuant 的金融数据仓库，存储大量的基本面和量价数据。ClickHouse 以其高性能的 OLAP 特性，满足快速查询的需求。</p>
        </li>
        <li>
            <strong>FastAPI</strong>：
            <p>高效易用的 Python 后端框架，提供对外的 API 接口服务，支持异步请求和自动生成文档。</p>
        </li>
        <li>
            <strong>LZ4 压缩</strong>：
            <p>效仿 <code>rqdatad</code>，对分发的数据进行 LZ4 压缩，以较小的性能开销换取更小的带宽占用和更高的压缩比。</p>
        </li>
    </ul>

    <h2>支持的功能</h2>
    <ul>
        <li>
            <strong>SQL 直接查询</strong>：
            <p>用户的 SQL 执行命令从 <code>kkdatac</code> 发出，经过 KKDataD 代理，直接向数据库获取数据，并在压缩后返回给用户。</p>
        </li>
        <li>
            <strong>安全的 SQL 执行</strong>：
            <p>为了防止 SQL 注入漏洞，我们添加了独立的数据库账户，限制写入权限和可查看的内容。这一设计参考了 BigQuant 量化平台的思路，确保数据安全。</p>
        </li>
        <li>
            <strong>API Key 认证</strong>：
            <p>通过分发 API Key，用户可以方便地访问我们的数据服务。每个 API Key 都有独立的权限和使用限额，方便追踪和管理。</p>
        </li>
        <li>
            <strong>数据用量追踪</strong>：
            <p>实时监控用户的数据使用情况，提供详细的日志记录，方便用户和管理员查看和管理。</p>
        </li>
    </ul>

    <h2>使用指南</h2>
    <p>
        欢迎查看我们的 <a href="/docs">API 文档</a>，了解如何使用 KKDataD 的 API 服务。
        文档中包含了详细的接口说明、参数解释和示例代码，帮助您快速上手。
    </p>
    <p>
        如有任何问题，欢迎加入我们的社区讨论，或通过邮件联系我们的支持团队。
    </p>

    <div class="note">
        <p><strong>提示：</strong>为了保证服务的稳定性和安全性，请妥善保管您的 API Key，不要泄露给他人。</p>
    </div>

    <h2>联系我们</h2>
    <p>
        如果您有任何疑问或需求，欢迎通过以下方式联系我们：
    </p>
    <ul>
        <li>官方网站：<a href="https://kakiquant.com" target="_blank">https://kakiquant.com</a></li>
        <li>电子邮件：<a href="mailto:support@kakiquant.com">support@kakiquant.com</a></li>
        <li>社区论坛：<a href="https://forum.kakiquant.com" target="_blank">https://forum.kakiquant.com</a></li>
    </ul>

    <div class="footer">
        &copy; 2023 KakiQuant. All rights reserved.
    </div>
    """

    return templates.TemplateResponse("intro.html", {"request": request, "content": content})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)