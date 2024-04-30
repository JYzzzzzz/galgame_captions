
# 基于视觉的Galgame文本识别翻译脚本

- 功能：对外语（主要针对日语）Galgame或RPG游戏的文本进行翻译。
- 流程：鼠标位置触发 -- 截图 -- OCR -- 翻译 -- pygame显示字幕

## 使用说明

### 1 启动脚本

打开命令行，输入
``` shell
python galgame_caption_main.py
```

- 其中，参数：

  - `--win`：设定OCR窗口范围。例如：`--win "[567,656,331,1032]"`，4个数分别代表窗口的`[top, button, left, right]`。默认值详见程序内，可改。
  
  - `--ocr`：设置OCR方案。目前可使用的方案包括：百度API`"api_baidu"`，OCRSpace API`"api_ocr_space"`，本地模型easyocr`"py_easyocr"`。其中，百度API效果最好，但需要账号，并申请，且有免费额度。OCRSpace API其次，连接不稳定。本地模型easyocr效果较差。

  - `--gamename`：指定游戏名称。用于指定将翻译后的文本存放在game_text_record中的哪个文本中。例如：`--gamename "example_game_name"`。

  - `--img_op`：设定OCR输入图片的格式。包括：灰度`"gray"`，黑白`"black_white"`。不同的OCR方案，输入不同的图片格式时精度会较高。


- 完整命令例子：
```shell
python galgame_caption_main.py \
  --gamename "MFSNXHZX-AR" \
  --ocr "api_baidu"
```
```shell
python galgame_caption_main.py \
  --gamename "YZDHN-ALA" \
  --ocr "api_baidu, py_easyocr, api_ocr_space" \
  --win "[567,656,331,1032]" \
  --img_op "gray"
```

### 2 触发OCR与翻译
- 鼠标移至“屏幕左上角”触发一次OCR识别翻译，OCR窗口为`--win`的值。
- 若鼠标移至“屏幕上方正中”，触发一次自定义窗口的OCR识别，会提示先后将鼠标放置到窗口的左上角和右下角。

### 3 屏幕下方会显示翻译后的字幕

- 字幕会显示在一个pygame的窗口中。
- 字幕窗口消失消失办法：1）焦点位于字幕窗口时，按 **ENTER** 或 **SPACE**。 2）**鼠标点击字幕窗口**。3）等120秒。

### 4 退出程序

- 鼠标移至左下角退出程序。

## 各 OCR 方案使用设置
### 百度OCR API使用设置

选择使用百度OCR API时，需要设置 `API_KEY` 与 `SECRET_KEY` ，这两个参数位于 `baiduOCRAPI.py` 中的 line 30 左右位置，可以通过到官网申请后获取。

### OCR SPACE API 使用设置

选择使用 OCR SPACE API 时，需要设置 `OCR_SPACE_API_KEY`，这个参数位于 `ocr_space_API.py` 中的开头位置，可以通过到官网申请后获取。

### 本地模型easyocr使用设置

需要安装easyocr库
```shell
pip install easyocr
```
并调整 `easyocr.Reader` 函数的模型路径参数，一般设为默认值即可。

## 代码特点

优点
- 具有可扩展性。可以添加更新、更优的OCR与翻译方式。

缺点
- 目前，参数、路径都在py代码中设置，未能整理到config文件中。
