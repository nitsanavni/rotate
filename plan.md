- [x] default rotation file is `.rotate/rotation`
- [x] stop shouldn't trigger the hook
- [x] support `$ROTATION_FILE` env var in hooks
- [x] `rotate rotate` command

- [ ] hook per person
- [ ] hook library
  - [ ] ding
  - [ ] say the names
  - [ ] `open $ROTATION_FILE`
    - other vars: $TALKING, $POSITON<N>, $NAME<N>, $TURN_DURATION, $TEAM_SIZE, $NAMES, $POSITIONS
- [ ] `rotate watch` cmd
- [ ] `rotate cat` cmd
- [ ] `rotate randomize` command
- [ ] `rotate PROMPT` command: prompts an llm to modify the rotation file
  - `--dry-run` option
- [ ] `stop` should reset the timer
- [ ] `reset` cmd
- [ ] rewrite TDD
  - [ ] inject time?
- [ ] add CI
- [x] publish to pipy
  - [ ] try to build with uv

# terminology

| term     | meaning                                                                                                   |
| -------- | --------------------------------------------------------------------------------------------------------- |
| hook     | executable script under `.rotate/hooks/`<br>triggered when event occurs<br>events include `expire`        |
| rotation | a collaboration pattern where people go through (rotate) predefeined positions (aka roles)                |
| rotate   | the team rotates positions, e.g. Bob was Typing now he's Talking                                          |
| team     | current people taking part in the rotation                                                                |
| name     | a person's name                                                                                           |
| position | a predefined role or responsibility in a collaborating team<br>e.g. many teams have the 'Typing' position |
| turn     |                                                                                                           |
| timer    | an automatic clock counting down the turn duration (e.g. 4 minutes)                                       |
