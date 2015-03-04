# MQTT3.1数据包编解码工具

---

## 用法

```python

from mqtt import Packet

# 编码
packet = Packet("pingreq").encode()

# 解码
data = Packet.fromData(packet)

```
