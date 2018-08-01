# Pixnet Hackathon Demo

由 Pixnet 所提供的 Python demo 執行檔，可由[範例網頁](https://pixnethackathon2018-competition.events.pixnet.net/) request 問題內容與圖片，經過處理後上傳到 demo 網頁中。網頁中可看到上傳結果。正式比賽應該也是這樣的形式。 

[https://pixnethackathon2018-competition.events.pixnet.net/](https://pixnethackathon2018-competition.events.pixnet.net/)

## File

- [.secrets.env](.secrets.env) - 儲存 API Token 的檔案
- [api_test_0731.py](api_test_0731.py): 執行範例檔案，需修改中間的 inpainting funciton 將加入自己的演算法。

## 執行方式

可透過以下方執行圖片的截取上傳

```bash
bash -c "source .secrets.env; python api_test_0731.py --qid 1"
```

執行後 `api_test_0731.py` 會自動取得 demo 網頁中 **question 1** 的圖片並透過 `.secrets.env` 中的 Token 上傳至 Demo 網頁。可在網頁中檢視上傳結果。

> 新圖片會覆蓋舊圖片

## Link

- [Source](https://github.com/pixnet/2018-pixnet-hackathon/blob/master/demos/foodai/api_test_0731.py)
- [Demo 網頁- https://pixnethackathon2018-competition.events.pixnet.net/](https://pixnethackathon2018-competition.events.pixnet.net/)
- [API Spec](https://github.com/pixnet/2018-pixnet-hackathon/blob/master/opendata/food.competition.api.md)
