# AbShutter class for python3

AB Shutter3をRaspberry Pi上で手軽に使うため作った
Python3用のモジュールです。

指定したデバイス(evdev)のキーボードイベントを監視して、
イベントが発生したら
コールバックルーチンを呼ぶようになってます。


## 「AB Shutter3」とは

自撮りするときにリモートでシャッターを押すボタンです。
スマホとはBluetoothで接続します。
見た目がまったく同じ類似品(バッタもん？)も多く出回っていて、
ダイソーやAmazonなどで安価で入手できます。

ホスト側からは、
HIDプロファイルの無線キーボード(VOLUME_UP、ENTERなど)として見えるので、
カメラのシャッターだけでなく、Bluetoothリモコン・ボタンとして、
いろんな応用ができます。


### 「AB Shutter3」の不良品・類似品に注意！

Amazonなどで検索すると、まったく同じ外見のものがたくさん見つかります。
(100円程度～1000円程度まで)
特に安いものは、信頼性が低く、不良率が高いです。

高価な信頼性の高い物を買ってもいいですが、
私は、安いものをいくつか買って、
1個使えればラッキーというノリで考えております（＾＾；

また、不良ではないですが、内部動作が異なるものがあります。
キーコードが違ったり、長押しに対応できたり、できなかったり…
(どれが正解なのかよくわかりません…www)

不良品でなければ、内部動作が異なっていても、
AbShutterクラスで扱うことはできます。


## tl;dr (極めて簡単な説明)

感覚をつかんでいただくために、
簡単な動作確認方法を以下に示します。
(下記は、環境設定、インストール、Bluetooth接続(後述)ができているという前提です。)

```bash
$ cd AbShutter
$ python3
:
>>> from AbShutter import AbShutter
>>> def f(d,c,v):
...   print(d,c,v)
...
>>> a = AbShutter(0, f)
>>> a.start()
>>> 
※ ここで、AB Shutterのボタンをいろいろ押すと…
※ 例えば、以下のように3つ数字が表示されます。
※ [evdev number, key code, value]
0 115 1
0 115 0
:
[Ctrl]-C
```


## Hardware

* Raspberry Pi (Zero WH etc.)

* AB Shutter3


## Software

* Raspbian Stretch

* Python 3.5.3～


## Install

```bash
$ sudo apt install -y bluetooth libbluetooth-dev build-essential evtest python3-pip
$ sudo python3 -m pip install -U pip
$ sudo hash -r 
$ sudo pip3 install -U evdev click
```


## Bluetooth pairing

```bash
$ sudo bluetoothctl
[...]# power on
[...]# scan on
[...]# connect FF:FF:C1:21:B3:FB
[...]# pair FF:FF:C1:21:B3:FB
[...]# trust FF:FF:C1:21:B3:FB
[...]# quit
```


## Test

```bash
$ ls /dev/input/event*
(check a number of device file)

$ sudo evtest
:
... (KEY_ENTER) ...
... (KEY_VOLUMEUP) ...
[Ctrl]-C

$ ./evdev-test1.py
devs: ['/dev/input/event0']
input_dev device /dev/input/event0, name "AB Shutter3       ", phys "B8:27:EB:73:30:CC"
---
Push buttons.. ([Ctrl]-C to end)
event at 1555345539.513055, code 04, type 04, val 786665
event at 1555345539.513055, code 115, type 01, val 01
event at 1555345539.513055, code 00, type 00, val 00
event at 1555345539.625007, code 04, type 04, val 786665
event at 1555345539.625007, code 115, type 01, val 00
event at 1555345539.625007, code 00, type 00, val 00
event at 1555345540.749932, code 04, type 04, val 786665
event at 1555345540.749932, code 115, type 01, val 01
event at 1555345540.749932, code 00, type 00, val 00
event at 1555345540.899922, code 04, type 04, val 786665
event at 1555345540.899922, code 115, type 01, val 00
event at 1555345540.899922, code 00, type 00, val 00

:

[Ctrl]-C


$ ./AbShutter.py -h
:
$ ./AbShutter.py 0 1
:

[Ctrl]-C
