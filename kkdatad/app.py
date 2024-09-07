from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from routes.downloader import data_router
from routes.user import user_router
from routes.proxyer import proxy_router
from kkdatad.database import engine
import kkdatad.models as models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")

# Include the financial data routes
app.include_router(data_router)
# Include the user registration routes
app.include_router(user_router)
app.include_router(proxy_router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    intro_html = """
    <h2>主要目的</h2>
    <p>建立起属于kakiquant的数据分发服务，设计理念与rqdatad相一致，摆脱对昂贵数据服务商的依赖，同时单独对外服务以盈利。</p>

    <h2>技术栈</h2>
    <ul>
        <li><strong>SQLite / MySQL</strong>: 负责进行用户管理，API Key验证，数据用量追踪，日志记录。</li>
        <li><strong>Clickhouse</strong>: 是kakiquant的金融数据仓库，存放着大量的基本面、量价数据。</li>
        <li><strong>FastAPI</strong>: 是高效易用的Python后端服务器，提供外界API接入服务。</li>
        <li><strong>LZ4</strong>: 压缩库，效仿rqdatad，对分发数据进行压缩，用少许性能开销换取更小的带宽和更高的压缩比。</li>
    </ul>

    <h2>支持的功能</h2>
    <ul>
        <li>Tushare Pro, AKshare HTTP 代理服务，用户的HTTP请求从kkdatac发出，经过kkdatad代理，向Tushare Pro, AKshare发出请求，返回数据。</li>
        <li>SQL直接查询，用户的SQL执行命令从kkdatac发出，经过kkdatad代理，向数据库直接获取数据，压缩后返回。</li>
        <li>SQL执行需要保证不出现注入漏洞，应添加独立账户，限制写入权限，限制可查看的内容。这是参考了Bigquant量化平台的思路。</li>
    </ul>
    
    <h2>使用指南</h2>
    <p>请参考<a href="/docs">API文档</a>，了解如何使用kkdatad的API。</p>
    """

    return templates.TemplateResponse("intro.html", {"request": request, "content": intro_html})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)