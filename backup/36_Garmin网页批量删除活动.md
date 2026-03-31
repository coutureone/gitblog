# [Garmin网页批量删除活动](https://github.com/coutureone/gitblog/issues/36)



&ensp;在浏览器控制台里面粘贴进去，前提是已经登录好了connect网页版本。

```js
// v0.30 2025-11-18 (China CN Version Modified)
(function() {
    'use strict';

    window.connectActivities = function(deviceArg, operationArg) {
        window.localStorage.removeItem("_connect_activities_cancel");

        class ShowUsageError extends Error { constructor(message) { super(message); this.name = this.constructor.name; } }
        class CancellationError extends Error { constructor(message) { super(message); this.name = this.constructor.name; } }

        function replaceAll(str, find, replace) { return str.replace(new RegExp(find, 'g'), replace); }

        var virtualConsole = {
            lines: [], currentLine: 0, subs: {},
            setSub: function(key, value) { virtualConsole.subs[key] = value; },
            log: function (msg, appendToCurrentLine) {
                if (!appendToCurrentLine) virtualConsole.currentLine++;
                if (appendToCurrentLine && virtualConsole.lines[virtualConsole.currentLine]) {
                    virtualConsole.lines[virtualConsole.currentLine] += msg;
                } else {
                    virtualConsole.lines[virtualConsole.currentLine] = msg;
                }
                console.clear();
                virtualConsole.lines.forEach(function (line) {
                    for (const key in virtualConsole.subs) { line = replaceAll(line, key, virtualConsole.subs[key]); }
                    console.log(line);
                });
            }
        }

        async function fetchRequest(description, url, method, data, requestIsJson) {
            // 自动转换域名为国服 .cn
            url = url.replace('garmin.com', 'garmin.cn');
            
            const shouldCancel = window.localStorage.getItem("_connect_activities_cancel");
            if (shouldCancel) { throw new CancellationError('cancelled by user'); }

            const headers = new Headers();
            const token = document.querySelector('meta[name="csrf-token"]')
            if (token) {
                let csrf_token = token.content;
                url = url.replace("connect.garmin.cn/", "connect.garmin.cn/gc-api/");
                headers.append('connect-csrf-token', csrf_token);
            } else {
                let access_token;
                try {
                    const tokenStorage = window.localStorage.getItem("token");
                    access_token = JSON.parse(tokenStorage).access_token;
                } catch (e) { throw new Error(`请确保已登录佳明官网。`); }
                headers.append("Authorization", `Bearer ${access_token}`);
            }

            if (requestIsJson) { headers.append("Content-Type", "application/json"); }
            headers.append("NK", "NT");
            headers.append("Di-Backend", "connectapi.garmin.cn");

            let response = await fetch(url, { method: method || 'GET', headers: headers, body: data || null });
            if (!response.ok) { throw new Error(`${description} 失败: ${response.status}`); }
            return response;
        }

        const maxLimit = 10000;
        let operation = undefined;
        const options = { limit: maxLimit, device: undefined, ignoreMissingDevices: false, name: undefined, at: undefined, after: undefined, before: undefined, startingAt: undefined, endingAt: undefined, type: undefined, newType: undefined };

        async function main() {
            // 解析参数逻辑
            if (typeof operationArg === "string") {
                options.device = deviceArg; operation = operationArg;
            } else if (typeof deviceArg === "string") {
                operation = deviceArg;
                if (typeof operationArg === 'object') Object.assign(options, operationArg);
            }

            // 核心检查点：已修改为适配国服域名
            if (!window.location.href.includes('garmin.cn') && !window.location.href.includes('garmin.com')) {
                throw new Error('脚本必须在佳明官网运行');
            }

            console.log("⏳ 正在获取活动列表...");
            const activityListUrl = `https://connect.garmin.cn/activitylist-service/activities/search/activities?limit=${options.limit}&start=0`;
            const activities = await (await fetchRequest('获取活动列表', activityListUrl)).json();

            if (activities.length === 0) { console.log('未找到活动'); return; }

            const filteredActivities = activities.filter(activity => {
                const activityDate = activity.startTimeLocal.substring(0, 10);
                if (options.before && activityDate >= options.before) return false;
                return true;
            });

            console.log(`符合筛选条件的活动数量: ${filteredActivities.length}`);

            for (const a of filteredActivities) {
                console.log(`• 📅 ${a.startTimeLocal} | ID: ${a.activityId} | 链接: https://connect.garmin.cn/modern/activity/${a.activityId}`);
                if (operation === 'delete') {
                    if (confirm(`确定要删除活动 ${a.activityId} 吗？`)) {
                        await fetchRequest('删除活动', `https://connect.garmin.cn/activity-service/activity/${a.activityId}`, 'DELETE');
                        console.log(`✅ 已删除: ${a.activityId}`);
                    }
                }
            }
        }

        main().catch(e => console.error(e));
    };

    console.log("%c✅ 佳明国服专用版脚本加载完毕！", "color: #32CD32; font-size: 16px; font-weight: bold;");
    console.log("使用示例: connectActivities('show', { before: '2026-01-01' });");
})();
```



```js
window.confirm = function() { return true; }; // 自动确认删除
```



`````js
connectActivities("delete", { before: "2026-01-29" }); // 示例 2026年1月29日年之前的数据
`````

