# Changelog

## [0.8.0](https://github.com/wuwentao/midea_ac_lan/compare/v0.7.1...v0.8.0) (2026-08-07)


### Features

* **ac:** add icons for silent and full mode ([#962](https://github.com/wuwentao/midea_ac_lan/issues/962)) ([7e9bb2e](https://github.com/wuwentao/midea_ac_lan/commit/7e9bb2e3e900a19e48107dd42778ae6afbfef4b0))
* **water_heater:** advertise ON_OFF for E3/E6/C3 ([#930](https://github.com/wuwentao/midea_ac_lan/issues/930)) ([94e18ac](https://github.com/wuwentao/midea_ac_lan/commit/94e18acd8c6b1f71fe010f04672b1a9151d40a22))


### Bug Fixes

* avoid deprecated CONCENTRATION_* constants on HA &gt;= 2026.7 ([#977](https://github.com/wuwentao/midea_ac_lan/issues/977)) ([ed760ee](https://github.com/wuwentao/midea_ac_lan/commit/ed760ee34675d873acfde3786830f6293c3b634a))
* **climate:** bounds-check device mode before indexing hvac list ([#919](https://github.com/wuwentao/midea_ac_lan/issues/919)) ([e982c8c](https://github.com/wuwentao/midea_ac_lan/commit/e982c8cdb3ee28896ed206c586eb849aa2588186))
* **config_flow:** avoid duplicate auth and blocking io ([#964](https://github.com/wuwentao/midea_ac_lan/issues/964)) ([0b9db57](https://github.com/wuwentao/midea_ac_lan/commit/0b9db57355472e55b7c22d9a4ccf314d9a5a43cd))
* **config_flow:** run blocking socket I/O in executor jobs ([#915](https://github.com/wuwentao/midea_ac_lan/issues/915)) ([3e1e101](https://github.com/wuwentao/midea_ac_lan/commit/3e1e1010876cccc0fffbb9180e56da7cd1d731a7))
* **config_flow:** stop mutating options list while iterating it ([#916](https://github.com/wuwentao/midea_ac_lan/issues/916)) ([8dde3da](https://github.com/wuwentao/midea_ac_lan/commit/8dde3da4175eab8b4d0b6286a499245cd61242cb))
* **da:** correct wash_level label duplicated as "Rinse count" ([#913](https://github.com/wuwentao/midea_ac_lan/issues/913)) ([97e6da3](https://github.com/wuwentao/midea_ac_lan/commit/97e6da3ce168a41ffbbe7198d0ab98b7d07479bf))
* **entity:** avoid doubled device name in the fallback entity name ([#927](https://github.com/wuwentao/midea_ac_lan/issues/927)) ([a8d9e63](https://github.com/wuwentao/midea_ac_lan/commit/a8d9e631861c614ce91ccc3e0f48a46159ab0067))
* **entity:** route sensor/select/button updates through shutdown guard ([#914](https://github.com/wuwentao/midea_ac_lan/issues/914)) ([4478757](https://github.com/wuwentao/midea_ac_lan/commit/4478757abacc96af42183e7dd62b4ffc7fb29d99))
* **fan:** stop capitalizing preset mode so CE "ECO mode" works ([#912](https://github.com/wuwentao/midea_ac_lan/issues/912)) ([04e3146](https://github.com/wuwentao/midea_ac_lan/commit/04e314619e1dc7f551be96e6a4337faf391c1147))
* **hacs:** raise advertised minimum Home Assistant to 2024.4.1 ([#923](https://github.com/wuwentao/midea_ac_lan/issues/923)) ([1ccc9fe](https://github.com/wuwentao/midea_ac_lan/commit/1ccc9feb7c553da9e67743f8632d2764386b92cc))
* **init:** make options reload robust and unload report real result ([#917](https://github.com/wuwentao/midea_ac_lan/issues/917)) ([dca4e8f](https://github.com/wuwentao/midea_ac_lan/commit/dca4e8f5087753848ddacfd9fdb082efa36d33f2))
* **light:** recompute color modes so dimmable lights are not stuck on/off ([#911](https://github.com/wuwentao/midea_ac_lan/issues/911)) ([ec3c939](https://github.com/wuwentao/midea_ac_lan/commit/ec3c9393700bb4f368fe6028d7d7edf01b2205da))
* **registry:** correct invalid and non-standard entity icons ([#918](https://github.com/wuwentao/midea_ac_lan/issues/918)) ([66fe75e](https://github.com/wuwentao/midea_ac_lan/commit/66fe75e3f98c3860520dadcbdc9b948d29bc8291))
* **vscode:** sync editor config with pre-commit/CI ([#955](https://github.com/wuwentao/midea_ac_lan/issues/955)) ([27da176](https://github.com/wuwentao/midea_ac_lan/commit/27da176955a92bd243d1e323328de740692b231e))

## [0.7.1](https://github.com/wuwentao/midea_ac_lan/compare/v0.7.0...v0.7.1) (2026-07-27)


### Bug Fixes

* **ac:** fan modes collapse to only "full" on stepless/inverter ACs ([#900](https://github.com/wuwentao/midea_ac_lan/issues/900)) ([f92a068](https://github.com/wuwentao/midea_ac_lan/commit/f92a068a4cba30aca0042a24605b325277bc74ff))

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
