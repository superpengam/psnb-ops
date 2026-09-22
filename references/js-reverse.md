# TRACK=JS-REVERSE

定位 sign/encrypt/token/hmac，不要喂整包混淆 JS。只切片核心函数+依赖。

反混淆：OB 字符串数组+平坦化；AAEncode/JSFuck 解码；VM 抽 bytecode+handler。

还原后 Python 复现，与浏览器签名逐字节对比。WASM 走 wasm2wat。小程序 wxapkg → app-service.js → wx.request。
