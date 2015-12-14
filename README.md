# 30lol

[三十撸啊撸](http://www.30lol.com) 网站源码

## 安装
* 请确保当前环境已经安装python、pip

* 获得源码

    `git clone https://github.com/infinity1207/thirtylol.git`

* 进入src目录，假设代码放到 d:\thirtylol，打开windows命令行工具

    `d:`

    `cd thirtylol\src`

* 安装依赖库

    `pip install -r requirements.txt`

* 启动

    `python manage.py runserver`

* 打开浏览器，地址栏输入 127.0.0.1:8000 进行访问

* 源码中附带了一个包含了演示数据的数据库，默认添加了一个管理员账户，登录信息为

    `用户名: admin`

    `密码: 1234`

## 进阶设置

* 使用用户管理模块
    
    `python manage.py check_permissions`

* 全文检索

    `python manage.py rebuild_index`

* 新浪微博登录

    ```python
    #setting.py
    WEIBO_OAUTH_VERIFY = ...
    WEIBO_OAUTH_APP_KEY = ...
    WEIBO_OAUTH_APP_SECRET = ...
    ```

* 更新Presenter信息
    打开浏览器，访问http://127.0.0.1:8000/presenters/fetch, 请先在admin中配置每个Platform的Login param，如何获取Login param请查看presenters\views.py的相关注释及代码
