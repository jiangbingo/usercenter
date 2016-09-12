
# Requirements

# Installation

#### ubuntu系统中python 常用支持库
>sudo apt-get install -y --no-install-recommends  autoconf  automake python-pip python-dev bzip2 file g++  gcc  imagemagick  libbz2-dev  libc6-dev  libcurl4-openssl-dev  libevent-dev  libffi-dev  libgeoip-dev  libglib2.0-dev  libjpeg-dev  liblzma-dev  libmagickcore-dev  libmagickwand-dev  libmysqlclient-dev  libncurses-dev  libpng-dev  libpq-dev  libreadline-dev  libsqlite3-dev  libssl-dev  libtool  libwebp-dev  libxml2-dev  libxslt-dev  libyaml-dev  make  patch  xz-utils  zlib1g-dev
    django-redis Pillow
#### 使用pip安装运行环境
所有项目需要的库文件都在requirements.txt中，使用pip命令安装：
> sudo pip install -r requirements.txt

# 运行
#### runserver
>python manage.py runserver 0.0.0.0:8000

#### gunicorn
gunicorn无法处理静态资源，需要配合其他服务器如nginx等使用。
>gunicorn Lejuadmin.wsgi


# 调试

调试工具有ipdb和django debug toolbar
#### 使用ipdb：
ipdb是后台中使用的断点调试工具
1. 在代码中添加import ipdb;ipdb.set_trace()打断点
2. 项目运行到断点时会停住
3. ipdb命令： n:下一行，遇到方法不会进入方法；s:下一行，遇到方法会进入方法；c:继续执行程序；q:停止执行该方法。

#### 使用debug toolbar
debug toolbar是页面上使用的项目性能分析工具，几个重点有：
1. SQL：显示这个request所执行的所有sql语句，可以辅助优化查询。
2. Static files：显示该页面所加载的静态资源。

# redis

项目使用redis缓存常用且不多变的对象
安装redis: 
> sudo apt-get install redis-server

使用：
1. from django.core.cache import cache
2. 存入: cache.set(key, value)
3. 取出：cache.get(key)
4. 删除：cache.delete(key)

# 代码规范

#### 文件
所有*.py文件需要在开头加上
> &#35; -*- encoding: utf-8 -*-

#### 导入
每个导入应该独占一行

    Yes: 
    import os
    import sys
    
    No:  
    import os, sys

导入总应该放在文件顶部, 位于模块注释和文档字符串之后, 模块全局变量和常量之前. 导入应该按照从最通用到最不通用的顺序分组:

1. 标准库导入
2. 第三方库导入
3. 应用程序指定导入

每种分组中, 应该根据每个模块的完整包路径按字典序排序, 忽略大小写.

    import foo
    from foo import bar
    from foo.bar import baz
    from foo.bar import Quux
    from Foob import ar
    
#### 缩进
缩进统一使用四个空格

#### 空行
顶级定义之间空两行, 比如函数或者类定义. 方法定义, 类定义与第一个方法之间, 都应该空一行. 函数或方法中, 某些地方要是你觉得合适, 就空一行。

#### 命名
1. 类名：使用大写字母开头的驼峰式，如：FooClass
2. 方法名：全小写字母，用下划线连接，如：foo_function
3. 静态变量和全局变量：全大写字母，用下划线连接，如：STATIC_PROPOTYPE
4. 自动变量和局部变量：全小写字母，用下划线连接，如：foo_propotype
5. 私有方法：以下划线开头，全小写字母，用下划线连接，如：_private_function
6. 私有变量：以下划线开头，全小写字母，用下划线连接，如：_private_propotype

#### 空格

###### 1. 括号内不要有空格.

    Yes: spam(ham[1], {eggs: 2}, [])
    No:  span( ham[ 1 ], { egg: 2 }, [ &nbsp;]  )
    
###### 2. 不要在逗号, 分号, 冒号前面加空格, 但应该在它们后面加(除了在行尾).

    Yes: 
    if x == 4:
        print x, y
    x, y = y, x

    No:  
    if x == 4 :
        print x , y
    x , y = y , x
    
###### 3. 参数列表, 索引或切片的左括号前不应加空格.

    Yes: spam(1)

    no: spam (1)

    Yes: dict['key'] = list[index]

    No:  dict ['key'] = list [index]
    
###### 4. 在二元操作符两边都加上一个空格, 比如赋值(=), 比较(==, <, >, !=, <>, <=, >=, in, not in, is, is not), 布尔(and, or, not). 至于算术操作符两边的空格该如何使用, 需要你自己好好判断. 不过两侧务必要保持一致.

    Yes: x == 1

    No:  x<1
    
###### 5. 当’=’用于指示关键字参数或默认参数值时, 不要在其两侧使用空格.

    Yes: def complex(real, imag=0.0): return magic(r=real, i=imag)

    No:  def complex(real, imag = 0.0): return magic(r = real, i = imag)
    
###### 6. 不要用空格来垂直对齐多行间的标记, 因为这会成为维护的负担(适用于:, #, =等):

    Yes:
    foo = 1000  # comment
    long_name = 2  # comment that should not be aligned
    
    dictionary = {
        "foo": 1,
        "long_name": 2,
        }

    No:
    foo       = 1000  # comment
    long_name = 2     # comment that should not be aligned
    
    dictionary = {
        "foo"      : 1,
        "long_name": 2,
        }


#### 注释

###### 1. 类

类应该在其定义下有一个用于描述该类的文档字符串. 如果你的类有公共属性(Attributes), 那么文档中应该有一个属性(Attributes)段. 并且应该遵守和函数参数相同的格式.
    
    class SampleClass(object):
        """Summary of class here.
    
        Longer class information....
        Longer class information....
    
        Attributes:
            likes_spam: A boolean indicating if we like SPAM or not.
            eggs: An integer count of the eggs we have laid.
        """
    
        def __init__(self, likes_spam=False):
            """Inits SampleClass with blah."""
            self.likes_spam = likes_spam
            self.eggs = 0
    
        def public_method(self):
            """Performs operation blah."""
###### 2. 函数和方法

Args:
列出每个参数的名字, 并在名字后使用一个冒号和一个空格, 分隔对该参数的描述. 描述应该包括所需的类型和含义. 如果一个函数接受*foo(可变长度参数列表)或者**bar (任意关键字参数), 应该详细列出*foo和**bar.
Returns: (或者 Yields: 用于生成器)
描述返回值的类型和语义. 如果函数返回None, 这一部分可以省略.
Raises:
列出与接口有关的所有异常.
    
    def fetch_bigtable_rows(big_table, keys, other_silly_variable=None):
        """Fetches rows from a Bigtable.
    
        Retrieves rows pertaining to the given keys from the Table instance
        represented by big_table.  Silly things may happen if
        other_silly_variable is not None.
    
        Args:
            big_table: An open Bigtable Table instance.
            keys: A sequence of strings representing the key of each table row
                to fetch.
            other_silly_variable: Another optional variable, that has a much
                longer name than the other args, and which does nothing.
    
        Returns:
            A dict mapping keys to the corresponding table row data
            fetched. Each row is represented as a tuple of strings. For
            example:
    
            {'Serak': ('Rigel VII', 'Preparer'),
             'Zim': ('Irk', 'Invader'),
             'Lrrr': ('Omicron Persei 8', 'Emperor')}
    
            If a key from the keys argument is missing from the dictionary,
            then that row was not found in the table.
    
        Raises:
            IOError: An error occurred accessing the bigtable.Table object.
        """
        pass
###### 3. 块注释和行注释

最需要写注释的是代码中那些技巧性的部分. 如果你在下次 代码审查 的时候必须解释一下, 那么你应该现在就给它写注释. 对于复杂的操作, 应该在其操作开始前写上若干行注释. 对于不是一目了然的代码, 应在其行尾添加注释.
    
    #  We use a weighted dictionary search to find out where i is in
    #  the array.  We extrapolate position based on the largest num
    #  in the array and the array size and then do binary search to
    #  get the exact number.
    
    if i & (i-1) == 0:        # true iff i is a power of 2



为了提高可读性, 注释应该至少离开代码2个空格.
另一方面, 绝不要描述代码. 假设阅读代码的人比你更懂Python, 他只是不知道你的代码要做什么.

    # BAD COMMENT: Now go through the b array and make sure whenever i occurs
    # the next element is i+1
