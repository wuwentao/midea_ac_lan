## Summary

<!-- What changed, why is it needed, and which appliance type/model is affected? -->

## Change type

<!-- Select every type that applies. -->

- [ ] Bug fix
- [ ] New appliance or feature
- [ ] Home Assistant entity or UI change
- [ ] Documentation, translation, tooling, or maintenance

## Related issues and pull requests

- `midea_ac_lan` issue: <!-- Use "Fixes #123", or N/A with a short reason. -->
- [`midea-lan`](https://github.com/wuwentao/midea-lan) issue/PR: <!-- Link, or N/A with a short reason. -->

## Protocol source

- Lua protocol file(s): <!-- Link the exact file(s) in https://github.com/wuwentao/midea-lua, or N/A with a short reason. -->
- [`midea-lua`](https://github.com/wuwentao/midea-lua) PR: <!-- Link if the required Lua file was not already present; otherwise N/A. -->

<!--
Device-protocol work normally starts with a Lua source in midea-lua, is
implemented and tested in midea-lan, and is then exposed as Home Assistant
entities here. Open and cross-link the applicable PRs. Do not bump the
midea-lan requirement in a feature PR; maintainers update it after the library
release.
-->

## Appliance and App / Cloud impact

- Appliance type/model:
- App / Cloud: <!-- Preserve the exact name, such as 美的美居 or SmartHome. -->
- User-visible behavior:

## Tests and verification

- Commands run:
- Home Assistant version:
- Hardware/device verification:

## Documentation and translations

<!-- List updated docs/translations, or explain why none are required. Keep English and Simplified Chinese appliance docs aligned. -->

## Checklist

- [ ] I linked the exact `midea-lua` protocol source and related cross-repository PRs, or explained why they do not apply.
- [ ] I updated the applicable English and Simplified Chinese documentation or explained why no documentation change is needed.
- [ ] I will address actionable CodeRabbit comments, reply with test evidence, and resolve the conversations before merge.
- [ ] I linked the related `midea_ac_lan` issue, or explained why none applies.
- [ ] I linked the related `midea-lan` PR, or explained why none applies.
