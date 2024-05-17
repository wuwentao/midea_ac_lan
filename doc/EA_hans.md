# 电饭煲

## 生成实体
### 默认实体
无默认实体

### 额外生成实体

| EntityID                             | 类型            | 名称                 | 描述   |
|--------------------------------------|---------------|--------------------|------|
| binary_sensor.{DEVICEID}_cooking     | binary_sensor | Cooking            | 烹饪中  |
| binary_sensor.{DEVICEID}_keep_warm   | binary_sensor | Keep Warm          | 保温中  |
| sensor.{DEVICEID}_bottom_temperature | sensor        | Bottom Temperature | 底部温度 |
| sensor.{DEVICEID}_keep_warm_time     | sensor        | Keep Warm Time     | 保温时间 |
| sensor.{DEVICEID}_mode               | sensor        | Mode               | 模式   |
| sensor.{DEVICEID}_progress           | sensor        | Progress           | 当前程序 |
| sensor.{DEVICEID}_time_remaining     | sensor        | Time Remaining     | 剩余时间 |
| sensor.{DEVICEID}_top_temperature    | sensor        | Top Temperature    | 顶部温度 |

## 服务
无服务