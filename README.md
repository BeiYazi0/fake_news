# 伪造群聊消息

基于HoshinoBot v2的伪造群聊消息插件

## 安装方法

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/BeiYazi0/fake_news`
2. 在 `config/__bot__.py`的模块列表里加入 `draw-card`
3. 重启HoshinoBot

## 指令

【伪造消息】 +@xx+文字/图片/#标记xx

示例：
伪造消息

@张三 哈哈哈+图片1

@李四 嘿嘿嘿+图片2

@王五 #标记xx

【标记消息xx(数字，1-{lmt})】

使用必须回复某条消息，主要标记文字图片消息

【标记特殊消息xx(数字，1-{lmt})】 

标记一些特殊消息，如小程序、视频、一起听

【测试标记消息xx(数字，1-{lmt})】 

测试标记消息能否发送

【查看标记消息】 

查看全部标记消息

【消息伪造帮助】 

一些伪造示例

## 备注

伪造消息时遇到多个"#标记xx"，若有多于一个特殊标记，只取第一个特殊标记，一般标记的文字、图片消息可叠加。

对于无法发送或已经失效的标记消息，使用标记指令覆盖即可。
