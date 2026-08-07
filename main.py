import re
import json
import random
from typing import Optional

import aiohttp

from astrbot.api.star import Star, register
from astrbot.api.event import AstrMessageEvent
from astrbot.api.event.filter import command
from astrbot.api import llm_tool


LANZOU_DOMAINS = (
    "lanzouf.com",
    "lanzou.com",
    "lanzoui.com",
    "lanzous.com",
    "lanzouw.com",
    "lanzoe.com",
    "lanzouj.com",
    "wws.lanzous.com",
    "wwww.lanzouf.com",
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
)

IP_PREFIX = [
    "218", "218", "66", "66", "218", "218", "60", "60", "202", "204",
    "66", "66", "66", "59", "61", "60", "222", "221", "66", "59",
    "60", "60", "66", "218", "218", "62", "63", "64", "66", "66",
    "122", "211",
]


@register(
    "astrbot_plugin_lanzou",
    "雨下¹整晚²",
    "蓝奏云直链解析插件",
    "1.0.8",
    "https://github.com/YuxiaANight/astrbot_plugin_lanzou",
)
class LanzouPlugin(Star):
    def __init__(self, context):
        super().__init__(context)
        self.base = "https://www.lanzouf.com"
        self._session: Optional[aiohttp.ClientSession] = None
        self._cfg = self._load_config()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def terminate(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def _load_config(self) -> dict:
        defaults = {
            "enable_llm_tool": True,
            "request_timeout": 20,
        }
        cfg = None
        for src in (
            lambda: self.config if isinstance(getattr(self, "config", None), dict) else None,
            lambda: self.context.get_config() if hasattr(self, "context") else None,
        ):
            try:
                v = src()
                if isinstance(v, dict):
                    cfg = v
                    break
            except Exception:
                continue
        if isinstance(cfg, dict):
            for k in defaults:
                if k in cfg:
                    defaults[k] = cfg[k]
        return defaults

    def reload_config(self):
        self._cfg = self._load_config()

    @staticmethod
    def _rand_ip() -> str:
        ip2 = round(random.randint(600000, 2550000) / 10000)
        ip3 = round(random.randint(600000, 2550000) / 10000)
        ip4 = round(random.randint(600000, 2550000) / 10000)
        return f"{random.choice(IP_PREFIX)}.{ip2}.{ip3}.{ip4}"

    def _headers(self, cookie: str = "", referer: str = "") -> dict:
        ip = self._rand_ip()
        h = {
            "User-Agent": USER_AGENT,
            "X-Forwarded-For": ip,
            "Client-IP": ip,
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        if cookie:
            h["Cookie"] = cookie
        if referer:
            h["Referer"] = referer
        return h

    def _timeout(self) -> aiohttp.ClientTimeout:
        t = int(self._cfg.get("request_timeout", 20) or 20)
        return aiohttp.ClientTimeout(total=t)

    @staticmethod
    def _solve_acw_sc_v2(arg1: str) -> str:
        pos_list = [15,35,29,24,33,16,1,38,10,9,19,31,40,27,22,23,25,13,6,11,39,18,20,8,14,21,32,26,2,30,7,4,17,5,3,28,34,37,12,36]
        mask = '3000176000856006061501533003690027800375'
        output = [''] * 40
        for i in range(len(arg1)):
            char = arg1[i]
            for j, pos in enumerate(pos_list):
                if pos == i + 1:
                    output[j] = char
        arg2 = ''.join(output)
        result = ''
        length = min(len(arg2), len(mask))
        for i in range(0, length, 2):
            str_hex = arg2[i:i+2]
            mask_hex = mask[i:i+2]
            xor_result = int(str_hex, 16) ^ int(mask_hex, 16)
            result += format(xor_result, '02x')
        return result

    async def _http_get(self, url: str, cookie: str = "", referer: str = "") -> str:
        session = await self._get_session()
        async with session.get(
            url,
            headers=self._headers(cookie, referer),
            ssl=False,
            allow_redirects=True,
            timeout=self._timeout(),
        ) as resp:
            text = await resp.text()
        if "var arg1=" in text:
            m = re.search(r"var arg1='([A-Fa-f0-9]+)'", text)
            if m:
                solved = self._solve_acw_sc_v2(m.group(1))
                new_cookie = f"acw_sc__v2={solved}"
                if cookie:
                    new_cookie = cookie + "; " + new_cookie
                async with session.get(
                    url,
                    headers=self._headers(new_cookie, referer),
                    ssl=False,
                    allow_redirects=True,
                    timeout=self._timeout(),
                ) as resp2:
                    text = await resp2.text()
        return text

    async def _http_post(
        self, url: str, data: dict, referer: str = "", cookie: str = ""
    ) -> str:
        session = await self._get_session()
        async with session.post(
            url,
            data=data,
            headers=self._headers(cookie, referer),
            ssl=False,
            timeout=self._timeout(),
        ) as resp:
            text = await resp.text()
        if "var arg1=" in text:
            m = re.search(r"var arg1='([A-Fa-f0-9]+)'", text)
            if m:
                solved = self._solve_acw_sc_v2(m.group(1))
                new_cookie = f"acw_sc__v2={solved}"
                if cookie:
                    new_cookie = cookie + "; " + new_cookie
                async with session.post(
                    url,
                    data=data,
                    headers=self._headers(new_cookie, referer),
                    ssl=False,
                    timeout=self._timeout(),
                ) as resp2:
                    text = await resp2.text()
        return text

    async def _http_redirect(
        self, url: str, cookie: str = "", referer: str = ""
    ) -> str:
        session = await self._get_session()
        async with session.get(
            url,
            headers=self._headers(cookie, referer),
            ssl=False,
            allow_redirects=False,
            timeout=self._timeout(),
        ) as resp:
            return (
                resp.headers.get("Location", "")
                or resp.headers.get("location", "")
            )

    @staticmethod
    def _normalize(url: str) -> str:
        for d in LANZOU_DOMAINS:
            if d in url and ".com/" in url:
                return "https://www.lanzouf.com/" + url.split(".com/", 1)[1]
        return url

    @staticmethod
    def _extract(text: str):
        url = None
        for d in LANZOU_DOMAINS + ("lanzn.com",):
            m = re.search(
                rf"https?://[^\s]*?{re.escape(d)}[^\s]*", text, re.IGNORECASE
            )
            if m:
                url = m.group(0).rstrip("，。,.;；:：!！?？)）]}>")
                break
        if not url:
            m = re.search(r"https?://[^\s]+", text)
            if m:
                url = m.group(0).rstrip("，。,.;；:：!！?？)）]}>")
        pwd = None
        pm = re.search(r"密码[：: ]+([A-Za-z0-9]+)", text)
        if pm:
            pwd = pm.group(1)
        else:
            pm = re.search(r"pwd[=: ]+([A-Za-z0-9]+)", text, re.IGNORECASE)
            if pm:
                pwd = pm.group(1)
        if not pwd and url:
            parts = text.split()
            for i, p in enumerate(parts):
                if p == url and i + 1 < len(parts):
                    nxt = parts[i + 1]
                    if re.fullmatch(r"[A-Za-z0-9]{1,20}", nxt):
                        pwd = nxt
                    break
        return url, pwd

    @staticmethod
    def _name(html: str) -> str:
        patterns = [
            r'style="font-size:\s*30px;text-align:\s*center;padding:\s*56px 0px 20px 0px;">(.*?)</div>',
            r'<div class="n_box_3fn".*?>(.*?)</div>',
            r"var filename = '(.*?)';",
            r'<div class="b"><span>(.*?)</span></div>',
        ]
        for p in patterns:
            m = re.search(p, html, re.DOTALL)
            if m:
                return m.group(1).strip()
        return ""

    @staticmethod
    def _size(html: str) -> str:
        patterns = [
            r'<div class="n_filesize".*?>大小：(.*?)</div>',
            r'<span class="p7">文件大小：</span>(.*?)<br>',
        ]
        for p in patterns:
            m = re.search(p, html, re.DOTALL)
            if m:
                return m.group(1).strip()
        return ""

    async def parse(self, url: str, pwd: str = "") -> dict:
        result = {
            "code": 400,
            "msg": "解析失败",
            "name": "",
            "filesize": "",
            "downUrl": "",
        }
        if not url:
            result["msg"] = "请输入URL"
            return result

        url = self._normalize(url)
        webpage = ""
        if "?" in url:
            webpage = url.split("?", 1)[1]

        try:
            html = await self._http_get(url, cookie="acw_sc__v2=")
        except Exception as e:
            result["msg"] = f"请求失败: {e}"
            return result

        if "var arg1=" in html:
            result["msg"] = "被蓝奏云反爬虫拦截，请稍后重试"
            return result

        if "文件取消分享了" in html:
            result["msg"] = "文件取消分享了"
            return result

        name = self._name(html)
        size = self._size(html)

        need_pwd = "function down_p(){" in html and not webpage
        if need_pwd:
            if not pwd:
                result.update(
                    {"msg": "请输入分享密码", "name": name, "filesize": size}
                )
                return result
            seg = re.findall(r"'sign':'(.*?)',", html)
            ajaxm = re.findall(r"ajaxm\.php\?file=(\d+)", html)
            if not ajaxm:
                result["msg"] = "提取参数失败"
                return result
            post = {
                "action": "downprocess",
                "sign": seg[1] if len(seg) > 1 else (seg[0] if seg else ""),
                "p": pwd,
                "kd": 1,
            }
            try:
                resp = await self._http_post(
                    f"{self.base}/ajaxm.php?file={ajaxm[0]}",
                    post,
                    referer=url,
                    cookie="acw_sc__v2=",
                )
            except Exception as e:
                result["msg"] = f"请求失败: {e}"
                return result
            try:
                j = json.loads(resp)
                if j.get("inf"):
                    name = j.get("inf", name)
            except Exception:
                pass
        else:
            m = re.search(
                r'\n<iframe[^>]*name="[^"]*"\s+src="/(.*?)"',
                html,
                re.DOTALL,
            )
            if not m:
                m = re.search(
                    r'<iframe[^>]*name="[^"]*"\s+src="/(.*?)"',
                    html,
                    re.DOTALL,
                )
            if m:
                ifurl = f"{self.base}/{m.group(1)}"
            else:
                ifurl = url

            if webpage:
                seg = re.findall(r"'sign':'(.*?)'", html)
                ajaxm = re.findall(r"ajaxm\.php\?file=(\d+)", html)
                post = {
                    "action": "downprocess",
                    "websignkey": "Em2R",
                    "sign": seg[1] if len(seg) > 1 else (seg[0] if seg else ""),
                    "websign": 2,
                    "kd": 1,
                    "ves": 1,
                }
                ajaxm_path = (
                    f"ajaxm.php?file={ajaxm[1]}" if len(ajaxm) > 1
                    else (f"ajaxm.php?file={ajaxm[0]}" if ajaxm else "")
                )
            else:
                try:
                    sub_html = await self._http_get(ifurl, cookie="acw_sc__v2=")
                except Exception as e:
                    result["msg"] = f"请求失败: {e}"
                    return result
                seg = re.findall(r"wp_sign = '(.*?)'", sub_html)
                signs = re.findall(r"ajaxdata = '(.*?)'", sub_html)
                ajaxm = re.findall(r"ajaxm\.php\?file=(\d+)", sub_html)
                post = {
                    "action": "downprocess",
                    "websignkey": signs[0] if signs else "",
                    "signs": signs[0] if signs else "",
                    "sign": seg[0] if seg else "",
                    "websign": "",
                    "kd": 1,
                    "ves": 1,
                }
                ajaxm_path = (
                    f"ajaxm.php?file={ajaxm[1]}" if len(ajaxm) > 1
                    else (f"ajaxm.php?file={ajaxm[0]}" if ajaxm else "")
                )

            if not ajaxm_path:
                result["msg"] = "提取参数失败"
                return result
            try:
                resp = await self._http_post(
                    f"{self.base}/{ajaxm_path}",
                    post,
                    referer=ifurl,
                    cookie="acw_sc__v2=",
                )
            except Exception as e:
                result["msg"] = f"请求失败: {e}"
                return result

        try:
            info = json.loads(resp)
        except Exception:
            result["msg"] = "解析失败"
            return result

        if info.get("zt") != 1:
            return {
                "code": 400,
                "msg": info.get("inf", "解析失败"),
                "name": name,
                "filesize": size,
                "downUrl": "",
            }

        down1 = f"{info.get('dom','')}/file/{info.get('url','')}"
        try:
            await self._http_get(down1, cookie="acw_sc__v2=")
            down2 = await self._http_redirect(
                down1,
                cookie=(
                    "down_ip=1; expires=Sat, 16-Nov-2019 11:42:54 GMT; "
                    "path=/; domain=.baidupan.com;acw_sc__v2="
                ),
                referer="https://developer.lanzoug.com",
            )
        except Exception:
            down2 = ""

        down = down2 if "http" in down2 else down1
        down = re.sub(r"pid=[^&]*&", "", down)

        return {
            "code": 200,
            "msg": "解析成功",
            "name": name,
            "filesize": size,
            "downUrl": down,
        }

    def _format(self, r: dict) -> str:
        if r.get("code") == 200:
            return (
                "蓝奏云解析成功\n"
                f"文件名: {r.get('name','')}\n"
                f"大小: {r.get('filesize','')}\n"
                f"直链: {r.get('downUrl','')}"
            )
        return f"蓝奏云解析失败: {r.get('msg','未知错误')}"

    @command("lanzou", alias=["蓝奏", "蓝奏云", "lz"])
    async def lanzou_cmd(self, event: AstrMessageEvent):
        msg = event.message_str.strip()
        url, pwd = self._extract(msg)
        if not url:
            yield event.plain_result(
                "用法: /lanzou <蓝奏云链接> [密码]\n"
                "示例: /lanzou https://www.lanzouf.com/xxxxx\n"
                "      /lanzou https://www.lanzouf.com/xxxxx abcd"
            )
            return
        yield event.plain_result("正在解析蓝奏云链接，请稍候...")
        r = await self.parse(url, pwd or "")
        yield event.plain_result(self._format(r))

    @llm_tool(name="parse_lanzou")
    async def parse_lanzou(
        self, event: AstrMessageEvent, url: str, pwd: str = ""
    ) -> str:
        """解析蓝奏云链接，返回直链地址、文件名和文件大小。
        当用户给出蓝奏云链接（lanzou / lanzouf / lanzoui 等域名），且希望拿到直链、文件名、大小时调用。

        Args:
            url(string): 蓝奏云分享链接（完整 URL，如 https://www.lanzouf.com/xxxxx）
            pwd(string): 分享密码（无密码可省略或传空字符串）
        """
        if not self._cfg.get("enable_llm_tool", True):
            return "LLM 工具未启用"
        if not url:
            return "请提供蓝奏云链接"
        r = await self.parse(url, pwd or "")
        return self._format(r)
