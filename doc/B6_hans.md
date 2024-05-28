# 油烟机

## 特性

- 支持风速调节
- 支持预设模式

## 自定义

- 自定义油烟机档位
- 设置开机默认档位

```json
{
  "speeds": {
    "0": "关闭",
    "1": "档位1",
    "2": "档位2",
    "3": "档位3",
    "22": "变频巡航"
  },
  "default_speed": 2
}
```

**_注意: 对于不同型号的油烟机，档位设置可能各不相同。有的4是爆炒档，有的4是巡航档，有的20是变频档，有的22是变频档，可以自己尝试不同设置适配你的油烟机。_**

## 生成实体

### 默认生成实体

| 实体ID              | 类型 | 描述     |
| ------------------- | ---- | -------- |
| fan.{DEVICEID}\_fan | fan  | 风扇实体 |

### 额外生成实体

| EntityID                                    | 类型   | 名称              | 描述         |
| ------------------------------------------- | ------ | ----------------- | ------------ |
| binary_sensor.{DEVICEID}\_cleaning_reminder | lock   | Cleaning Reminder | 清洁提示     |
| binary_sensor.{DEVICEID}\_oilcup_full       | select | Oil-cup Full      | 油杯满提示   |
| sensor.{DEVICEID}\_fan_level                | sensor | Current Fan Level | 当前风扇档位 |
| switch.{DEVICEID}\_light                    | switch | Light             | 灯开关       |
| switch.{DEVICEID}\_power                    | switch | Power             | 电源开关     |

## 服务

无服务
