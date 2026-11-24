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
entities here. Open and cross-link the applicable PRs.

While the related midea-lan PR is unmerged, this PR may point manifest.json at
that contributor fork/branch so integration CI and end-to-end testing can run.
CI and local setup install the runtime requirement directly from manifest.json;
`pyproject.toml` and `uv.lock` only manage the development and test environment.
Do not change either file to test unreleased midea-lan work. Once the midea-lan
PR is merged, change manifest.json to upstream main:
"midea-lan@git+https://github.com/wuwentao/midea-lan.git@main". You may also
use upstream main from the start and wait for the library PR to merge. Before
this PR is merged, manifest.json must reference either wuwentao/midea-lan main
or a released midea-lan version; a contributor fork/branch must never be merged.
The manual release workflow accepts an integration version and creates a PR
updating the version and changelog. After that PR merges, the release workflow
creates the tag, builds the zip, and uploads it to GitHub Releases. Before
publishing, maintainers set manifest.json to a released midea-lan version that
contains the required merged library changes.
-->

## Appliance and App / Cloud impact

- Appliance type/model:
- App / Cloud: <!-- Preserve the exact name, such as 美的美居 or SmartHome. -->
- User-visible behavior:

## Tests and verification

- Hardware/device verification:

## Documentation and translations

<!-- List updated docs/translations, or explain why none are required. Keep English and Simplified Chinese appliance docs aligned. -->

## Checklist

- [ ] I linked the exact `midea-lua` protocol source and related cross-repository PRs, or explained why they do not apply.
- [ ] I have updated the device attribute translations.
- [ ] I have added the new device attributes to the English and Chinese device documentation files.
- [ ] I will address actionable CodeRabbit comments, reply with test evidence, and resolve the conversations before merge.
- [ ] I linked the related `midea_ac_lan` issue, or explained why none applies.
- [ ] I linked the related `midea-lan` PR, or explained why none applies.
- [ ] Before merge, `manifest.json` references `wuwentao/midea-lan@main` or a released `midea-lan` version, not a contributor fork/branch.
