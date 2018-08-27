# Pixnet Hackathon Demo

由 Pixnet 所提供的 Python demo 執行檔，可由[範例網頁](https://pixnethackathon2018-competition.events.pixnet.net/) request 問題內容與圖片，經過處理後上傳到 demo 網頁中。網頁中可看到上傳結果。正式比賽應該也是這樣的形式。 

[https://pixnethackathon2018-competition.events.pixnet.net/](https://pixnethackathon2018-competition.events.pixnet.net/)

## Structure

- [.secrets.env](.secrets.env) - 儲存 API Token 的檔案
- [api_test_0731.py](api_test_0731.py): Pixnet 的原始範例黨。
- [pixnet_inpainting.py](pixnet_inpainting.py): 修改後的執行範例檔案，使用 DeepFillv1 執行。
- [pixnet_inpainting.ipynb](pixnet-inpainting.ipynb): `pixnet_inpainting.py` 的 Jupyter notebook 版本。
- [generating_inpainting](generating_inpainting): DeepFillv1 程式的 folder。

## 套件安裝

因使用 DeepFillv1 Model 在做 inpainting 時需要 GPU 資源，因此 Nvidia GPU 硬體以及安裝 cuda 與 cuDNN 等。

> Tensorflow-gpu 1.9.0 只支援到 [Cuda 9.0](https://developer.nvidia.com/cuda-90-download-archive)，因此 cuda 與 cuDNN 都需選擇 cuda 9.0 版本安裝。

此外 `generating_inpainting` 會使用到作者自己建立的套件 [neuralgym](https://github.com/JiahuiYu/neuralgym)，因此需另外安裝。

```bash
# Install neuralgym
pip install git+https://github.com/JiahuiYu/neuralgym
```

> 需使用的相關 package 以放在 `requirements.txt` 中，可透過 `pip -r requirements.txt` 指令安裝相依套件。

## Model_logs

將 model checkpoint 的資料夾並放在 ./generating_inpainting/model_logs 下，目前使用

```
20180806124027737769_6c140319b0ee_pixfood20_NORMAL_wgan_gp_pixfood20
```

這個 checkpoint 來做 inpainting (可修改 Code 改變所使用的 checkpoint)

## 執行 Image inpainting 

```bash
bash -c "source .secrets.env; python pixnet_inpainting.py --qid 1"
```

執行後 `pixnet_inpainting.py` 會自動取得 demo 網頁中 **question 1** 的圖片並透過 `.secrets.env` 中的 Token 上傳至 Demo 網頁。可在網頁中檢視上傳結果。
此外原始圖片，Mask 圖片以及 inpainting 後的圖片都會放在 `output` 資料夾中。

> 新圖片會覆蓋舊圖片

## 整合 Code

新版執行方式，啟動 python 程式後讀入 Model 並建立交互式輸入方式選擇答題題號，確認後上傳結果至競賽網頁。

```bash
# Set variable
source .secrets.env

# Run inpainting
python ./generative_inpainting/uploader.py --checkpoint {CheckPointPath}
``` 

## Link

- [Source](https://github.com/pixnet/2018-pixnet-hackathon/blob/master/demos/foodai/api_test_0731.py)
- [Demo 網頁- https://pixnethackathon2018-competition.events.pixnet.net/](https://pixnethackathon2018-competition.events.pixnet.net/)
- [API Spec](https://github.com/pixnet/2018-pixnet-hackathon/blob/master/opendata/food.competition.api.md)
- [Github - generating_inpainting](https://github.com/JiahuiYu/generative_inpainting)
- [Github - neuralgym](https://github.com/JiahuiYu/neuralgym)
