# Console Image Monitor

一个简单的控制台图片显示器

---

## 使用
通常，这里提供两种方式启动

### 第一种：
下载 [Sloves_Starter](https://github.com/qeggs-dev/Sloves_Starter)
放在根目录下运行 (它会自动使用根目录下的那个`run.json`启动，改名也可以，它只搜索后缀名)

### 第二种：
运行 `python -m venv .venv`
然后根据系统
Windows: `.venv\Scripts\activate.bat`
Linux: `source .venv/bin/activate`
然后运行 `pip install -r requirements.txt`
最后运行 `python console_image_monitor.py`

---

## 命令行参数：

``` bash
usage: console_image_monitor.py [-h] -s SOURCE [-rt RESIZE_TYPE] [-rm RESIZE_MODE] [-ac ALPHA_CHARSET] [-cr] [-w WORKERS] [-r]

Monitor a image in the console.

options:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        The source image path.
  -rt RESIZE_TYPE, --resize-type RESIZE_TYPE
                        The resize mode to use when displaying images in the console.
  -rm RESIZE_MODE, --resize-mode RESIZE_MODE
                        The resize mode to use when displaying images in the console.
  -ac ALPHA_CHARSET, --alpha-charset ALPHA_CHARSET
                        The charset to use for displaying alpha transparency.
  -cr, --color-reverse  Reverse the color of the image.
  -w WORKERS, --workers WORKERS
                        The number of workers to use for rending images.
  -r, --random-render   Render images randomly.
```

### 参数说明：
- `--source`：要显示的图片路径
- `--resize-type`：图片缩放方式
- `--resize-mode`：图片缩放模式
- `--alpha-charset`：透明字符集
- `--color-reverse`：是否反转颜色
- `--workers`：渲染图片的线程数(需要启用`--random-render`)
- `--random-render`：随机渲染图片

### 缩放方式：
- `nearest`：最近邻
- `bilinear`：双线性
- `bicubic`：三次样条
- `lanczos`：拉科松
- `box`：盒子
- `hamming`：汉明

### 缩放模式：
- `fill`：填充
- `width`：宽度
- `height`：高度

### 透明字符集：
- ` ░▒▓█`：默认透明字符集

### 反转颜色：
- `--color-reverse`：是否反转颜色

---

## 示例：
``` bash
python console_image_monitor.py -s /path/to/image.png -rt fill -rm bicubic -ac ░▒▓█ -cr
```

---

# License

License: [MIT](LICENSE.md)
Requirements Licenses: [Licenses](LICENSES.md)

---

# 相关仓库

- [Sloves_Starter](https://github.com/qeggs-dev/Sloves_Starter)