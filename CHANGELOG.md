# Changelog

## [0.7.0](https://github.com/wuwentao/midea_ac_lan/compare/v0.6.12...v0.7.0) (2026-07-24)


### Features

* **ac:** add group 1, 2 and 7 diagnostic sensors ([#887](https://github.com/wuwentao/midea_ac_lan/issues/887)) ([cef2df6](https://github.com/wuwentao/midea_ac_lan/commit/cef2df69f1673e5f74b63e55bc233fe2aa83afb9))
* **ac:** add Power Rate Limit (rate_select / Gen mode) select entity ([#839](https://github.com/wuwentao/midea_ac_lan/issues/839)) ([ed59e6d](https://github.com/wuwentao/midea_ac_lan/commit/ed59e6d9b89e8fbed15b6343c7f4591d28f4fc80))
* **ac:** derive climate modes/fan/swing/presets from B5 capabilities ([#862](https://github.com/wuwentao/midea_ac_lan/issues/862)) ([6cc51ab](https://github.com/wuwentao/midea_ac_lan/commit/6cc51abe822fce9b02438134a305bae8588c166c))
* **ac:** expose model-reported diagnostics and airflow ([#883](https://github.com/wuwentao/midea_ac_lan/issues/883)) ([9af2be4](https://github.com/wuwentao/midea_ac_lan/commit/9af2be48f78727462a60b02908f4cf0b563e10de))
* **ac:** use device min/max temperature for climate bounds ([#857](https://github.com/wuwentao/midea_ac_lan/issues/857)) ([5566c67](https://github.com/wuwentao/midea_ac_lan/commit/5566c67be798cd60e18245671cff8af767de0c90))
* add French translations ([#718](https://github.com/wuwentao/midea_ac_lan/issues/718)) ([0b8fa8f](https://github.com/wuwentao/midea_ac_lan/commit/0b8fa8f2ad86ec2be1047c5ecda61c530abf9357))
* add MAC address/SN to device_info in midea_entity.py ([#868](https://github.com/wuwentao/midea_ac_lan/issues/868)) ([cb0d4f3](https://github.com/wuwentao/midea_ac_lan/commit/cb0d4f3789f5c505baf7fb5bea7b8527780fdd32))
* **e1:** add mode select and usage estimates ([#826](https://github.com/wuwentao/midea_ac_lan/issues/826)) ([57a4875](https://github.com/wuwentao/midea_ac_lan/commit/57a4875b6d267bd47fa25a6ebd8762fd5e30f3ed))
* **e2:** add memory (Memo U) and sterilization switches ([#849](https://github.com/wuwentao/midea_ac_lan/issues/849)) ([d1c09e3](https://github.com/wuwentao/midea_ac_lan/commit/d1c09e3f260d081a2ffe01824dd6ae3380661249))
* **ed:** support 0xED soft water machine new attrs ([#884](https://github.com/wuwentao/midea_ac_lan/issues/884)) ([0d65c02](https://github.com/wuwentao/midea_ac_lan/commit/0d65c02416e4725c4170d75253dd70a293af8864))


### Bug Fixes

* **entity:** guard update_state against closed event loop on shutdown ([#874](https://github.com/wuwentao/midea_ac_lan/issues/874)) ([f5222c1](https://github.com/wuwentao/midea_ac_lan/commit/f5222c1df10eb46f47d26cd17a5ee267fbc26ff6))
* **entity:** subscribe to device updates in async_added_to_hass ([#869](https://github.com/wuwentao/midea_ac_lan/issues/869)) ([d7f588a](https://github.com/wuwentao/midea_ac_lan/commit/d7f588aeb028efe975006ed2e0d8c88c310ff9dd))
* **i18n:** sync all locale translations with en.json base ([#889](https://github.com/wuwentao/midea_ac_lan/issues/889)) ([f312454](https://github.com/wuwentao/midea_ac_lan/commit/f312454f13dc07a0088fb35c20e645bd5b82b2e7))
* **migration:** honor IP override and guard discovery in mac/sn backfill ([#890](https://github.com/wuwentao/midea_ac_lan/issues/890)) ([6c00213](https://github.com/wuwentao/midea_ac_lan/commit/6c00213db2a13f38e23c546b00f0d74d53e57c90))
* set entity_id with correct domain ([#855](https://github.com/wuwentao/midea_ac_lan/issues/855)) ([0519e4a](https://github.com/wuwentao/midea_ac_lan/commit/0519e4a387809c25e85747b90d07c740de167170))
