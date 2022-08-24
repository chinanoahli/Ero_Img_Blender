# [ImageMagick](https://imagemagick.org/script/index.php)

在使用*色图混淆器*之前，你应该先[下载ImageMagick](https://imagemagick.org/script/download.php#windows)的**portable**版可执行文件，解压后将其放置于本目录下

目录结构如下：

```
Ero_Img_Blender
├─ Run.py / Run.exe
├─ 程序相关的其他文件
├─ imagemagick
│      convert.exe
│      magick.exe
│      ... 省略其他文件 ...
├─ input_imgs
│      这里存放要处理的图片文件
└─ output_imgs
       这里存放处理后输出的图片文件
```

## ImageMagick 的[维基百科](https://zh.wikipedia.org/zh-cn/ImageMagick)页面

<sub>本段落全部文字在[知识共享 署名-相同方式共享 3.0协议](https://zh.wikipedia.org/wiki/Wikipedia:CC-BY-SA-3.0%E5%8D%8F%E8%AE%AE%E6%96%87%E6%9C%AC)之条款下提供，附加条款亦可能应用。</sub>

ImageMagick是一个用于查看、编辑位图文件以及进行图像格式转换的开放源代码软件套装。它可以读取、编辑超过100种图帧式。ImageMagick以ImageMagick许可证（一个类似BSD的许可证）发布。

### 功能及特点

ImageMagick主要由大量的命令行程序组成，而不提供像Adobe Photoshop、GIMP这样的图形界面。但是，ImageMagick也提供了一个基于X Window的简易GUI：IMDisplay。它还为很多程序语言提供了API库。Imagemagick使用特征签名识别文件类型。

很多程序使用ImageMagick创建缩略图，如MediaWiki、phpBB和vBulletin，还有其它一些程序如LyX使用ImageMagick转换图帧式。

在Perl语言中，ImageMagick还有一个API叫PerlMagick。

### 文件格式转换

ImageMagick最基本的一个功能是准确高效地转换超过68种图片的格式，包括众所周知的TIFF、JPEG、PNG、PDF、PhotoCD，以及GIF。请参考ImageMagick支持的格式列表。

### 特效

ImageMagick包括了大量用于特效的滤镜和扩展功能。
