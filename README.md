# Are You OK? 你还好吗？
![](./logo.jpg)
  <div>
    <a href="https://github.com/xhdndmm/are-you-ok/stargazers"><img src="https://img.shields.io/github/stars/xhdndmm/are-you-ok" alt="Stars"></a>
    <a href="https://github.com/xhdndmm/are-you-ok/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://www.python.org/download"><img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python Version"></a>
  </div>

---

## 项目结构
```
.
├── app
│   ├── db.py
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   │       └── main.js
│   └── templates
│       ├── base.html
│       ├── calendar.html
│       ├── diary_detail.html
│       ├── diary.html
│       ├── index.html
│       ├── login.html
│       ├── profile.html
│       ├── register.html
│       └── stats.html
├── LICENSE
├── README.md
├── requirements.txt
└── run.py

6 directories, 20 files
```
## 部署方法
准备[Python3](https://www.python.org/downloads/release/python-31210/)环境  
克隆本仓库
```
git clone https://github.com/xhdndmm/are-you-ok
cd /path/to/are-you-ok
```
然后安装依赖
```
pip install -r requirements.txt
```
然后运行`run.py`即可
- 项目根目录下创建的`log/`是日志文件夹，app下的`diary.db`是数据库文件。
## 问题反馈以及代码贡献
程序不可避免会出现问题，你可以在[这里](https://github.com/xhdndmm/are-you-ok/issues)提交问题。  
如果你想为项目贡献代码，我们十分欢迎，但请遵守以下几点：
- 不要提交**未经测试**的代码
- 提交代码时，请提交到`dev`分支
## 使用协议
本程序使用[MIT](./LICENSE)许可证。

---
### 创作背景
最近（2026.1）有个软件很火，叫做“死了吗”。我了解了一下，虽然名字不是很好听，但觉得创意不错，于是乎就做了这个东西。考虑到现在年轻人压力比较大，或许一声问候也不错，或者让他们记录一下自己的生活，所以这个平台的主要功能就敲定了。  
所以它主要是用来记录自己的日记，并且给出当日的评价，创意应该不错。  
由于时间以及技术问题，大部分代码其实是AI生成的，这里我表示抱歉。  
原作者 [喜欢电脑的猫咪](https://xhdndmm.net)  
2026.1.18