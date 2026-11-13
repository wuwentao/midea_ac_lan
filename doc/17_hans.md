# 电动晾衣机

吸顶式电动晾衣机。

## 特性

- 支持开关
- 支持升降 (上升 / 下降 / 暂停)
- 支持照明
- 支持杀菌
- 支持烘干
- 支持烘烤
- 支持负离子

## 自定义

无自定义

## 实体

### 默认实体

| 实体ID                   | 类型   | 描述     |
| ------------------------ | ------ | -------- |
| switch.{DEVICEID}\_power | switch | 开关实体 |

### 扩展传感器

| 实体ID                        | 类型   | 描述     |
| ----------------------------- | ------ | -------- |
| select.{DEVICEID}\_updown     | select | 升降控制 |
| switch.{DEVICEID}\_light      | switch | 照明     |
| switch.{DEVICEID}\_sterilize  | switch | 杀菌     |
| switch.{DEVICEID}\_dry        | switch | 烘干     |
| switch.{DEVICEID}\_baking     | switch | 烘烤     |
| switch.{DEVICEID}\_anion      | switch | 负离子   |
| sensor.{DEVICEID}\_error_code | sensor | 错误代码 |

## 服务

无服务
