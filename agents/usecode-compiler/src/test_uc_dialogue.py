#!/usr/bin/env python3
"""
test_uc_dialogue.py — Headless verification of the quest steps 5-7
dialogue flag flow, driven through the conversation simulator against
the BUILT shared/build/EUSECODE.FLX.

Encodes the 2026-07-04 quest-path survey: the LIVE recognition/blame
flows must work (flags set in order, menus contain what the design
says), and the known-dead paths must stay dead until deliberately
fixed — each dead assertion names its defect, so fixing one flips a
test and forces the suite to be updated alongside.

STEP-7 REPAIR (2026-07-04, lv-patched/RAGNAR.UNK): the Ragnar defects
D8/D11 used to guard are now FIXED, so those tests assert the repaired
behavior — met-branch persistence (the 1994 `ragnarMet = false;` debug
reset is gone) and the full bag chain (the crush/stone `Yes, I do.`
case shadowing is gone; `stone.pop(bag.referent)` now compiles to the
popToContainer overload) plus the restored `I have no fight with you.`
handler.

NPC dispatch: npcnum + 1024, pinned in lv_manifest.json npc_classes.
"""

import json
import os
import struct
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8c_sim import UCSim, SimWorld, SimError, BUILD_FLX  # noqa: E402
from u8c_symbols import TYPE_SHAPES  # noqa: E402  (bag/key shape ids)
from u8_flex import UsecodeFlexArchive  # noqa: E402
sys.path.insert(0, os.path.join(BASE_DIR, 'agents', 'usecode-disasm', 'src'))
from u8_usecode_disasm import UsecodeDisassembler  # noqa: E402

MANIFEST = os.path.join(BASE_DIR, 'shared', 'build', 'lv_manifest.json')
_m = json.load(open(MANIFEST))
NPC = _m['npc_classes']
FLAG = {k: v['bit'] for k, v in _m['global_flags'].items()}

NPCNUM = {'RAGNAR': 105, 'THORDIS': 106, 'ATLI': 107, 'INGJALD': 112,
          'HRODNY': 113, 'TYORVI': 115, 'EZREKAL': 116}

passed = 0
failed = 0
# Every menu any conversation in this file is offered, checked at the end
# for an option listed twice (docs/playtest-2026-10-10-full-run-part5.md
# finding 2: `askList+=` appends without the dedupe `^=` does, so an add
# of an option already on the menu shows it twice).
DUP_MENUS = []


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


class Village:
    """One persistent world + globals across many conversations."""

    def __init__(self):
        self.world = SimWorld()
        self.world.add(1, objid=1, x=19200, y=6400, z=0)  # Avatar
        self.npcs = {}
        for name, num in NPCNUM.items():
            self.npcs[name] = self.world.add(
                402, objid=num, x=19300 + num, y=6400, z=0, npcnum=num)
        self.sim = UCSim(world=self.world)
        self.sim.follow_spawns = True

    def talk(self, name, answers, max_steps=800000):
        """One conversation; returns (completed, menus_seen)."""
        self.sim.answer_script = list(answers)
        n0 = len(self.sim.asks)
        try:
            self.sim.run_event(NPC[name], None, self.npcs[name].objid,
                               max_steps=max_steps, event=1)
            err = None
        except SimError as e:
            err = str(e)
        for opts, _a in self.sim.asks[n0:]:
            if len(set(opts)) != len(opts):
                DUP_MENUS.append((name, list(opts)))
        return err, self.sim.asks[n0:]

    def schedule(self, name, avatar_at=None, avatar_map=10):
        """Drive one NPC schedule event the way SchedulerProcess::run does —
        event 8, once per actor slot, once per in-game hour, with no
        conversation involved. avatar_at/avatar_map move the Avatar first,
        because the plantScene self-heal keys on where he is standing."""
        av = self.world.items[1]
        if avatar_at is not None:
            av.x, av.y = avatar_at
        av.mapnum = avatar_map
        try:
            self.sim.run_event(NPC[name], None, self.npcs[name].objid,
                               max_steps=200000, event=8)
            return None
        except SimError as e:
            return str(e)

    def flag(self, name):
        return self.sim.get_global(FLAG[name], 1)

    def setflag(self, name, v=1):
        self.sim.set_global(FLAG[name], 1, v)

    def additem(self, shape, frame=0, quality=0):
        """Place an item in the Avatar's (objid 1) container."""
        it = self.world.add(shape, frame=frame, quality=quality)
        self.world.put_in_container(it, self.world.items[1])
        return it

    def inv(self, shape, frame=None):
        """Live (non-destroyed) inventory items of shape [and frame]."""
        av = self.world.items[1]
        out = []
        for oid in av.contents:
            it = self.world.items[oid]
            if it.destroyed or it.shape != shape:
                continue
            if frame is not None and it.frame != frame:
                continue
            out.append(it)
        return out


def menus_str(menus):
    return ' | '.join('[' + ', '.join(m) + ']->' + repr(a)
                      for m, a in menus[-3:])


def walk(v, name, answers, must_offer=(), label=None):
    """Organic-navigation harness for the dialogue tree. Drives `answers`
    through ONE conversation, then bakes in the anti-force-drive rule that
    let both shipped bugs hide (the old sim tests set dead flags and drove
    look-alike strings the in-game menu never offers). Three guards:
    (1) the sim itself raises 'scripted answer X not among ask options' the
    instant a pick is not on the menu the class actually built — surfaced
    here as `err` and asserted away; (2) we re-assert per step that every
    answer taken WAS in its offered menu (sim.asks records (options, answer));
    (3) every `must_offer` target must have appeared in some offered menu.
    A path that cannot be walked with real menu options fails loudly here
    instead of passing on a force-driven string. Returns (err, menus)."""
    label = label or name
    err, menus = v.talk(name, answers)
    if err is not None:
        check(f'{label}: walked using only offered options (no force-drive)',
              False, str(err) + '  ' + menus_str(menus))
        return err, menus
    bad = [(i, a, opts) for i, (opts, a) in enumerate(menus) if a not in opts]
    check(f'{label}: every pick came from the offered menu', not bad,
          str(bad[:2]))
    if must_offer:
        offered = {o for opts, _a in menus for o in opts}
        missing = [t for t in must_offer if t not in offered]
        check(f'{label}: menu offered target option(s) {list(must_offer)}',
              not missing, f'missing={missing}; offered={sorted(offered)[:14]}')
    return err, menus


print('=' * 70)
print('D1: Thordis first contact — met/name flags')
v = Village()
err, menus = v.talk('THORDIS', ['How are you called?', 'bye'])
check('conversation completes', err is None, err)
check('thordisMet set', v.flag('thordisMet') == 1)
check('thordisName set', v.flag('thordisName') == 1)

print()
print('D2: Atli first contact through the Rite intro (testFromAtli)')
v = Village()
err, menus = v.talk('ATLI', ['May I speak with you?',
                             'What is your name?',
                             'What do you do?',
                             'bye'])
check('first-contact conversation completes', err is None,
      (err or '') + '  ' + menus_str(menus))
check('atliMet set', v.flag('atliMet') == 1)
check('atliName set', v.flag('atliName') == 1)
check('atliJob set', v.flag('atliJob') == 1)

# Second conversation: the stay/Zealan/Rite chain, then — menu adds are
# conversation-local — the stone ask and lake story IN the same convo.
err, menus = v.talk('ATLI', ['Is there some way I may stay?',
                             'Then I will become a Zealan.',
                             'Rite of Passage?',
                             'I wish to take the test.',
                             'Where is the Passage Stone?',
                             'Took the Stone?',
                             'I will speak to the Hoskulds.'])
check('Rite chain + lake story completes', err is None,
      (err or '') + '  ' + menus_str(menus))
check('testFromAtli set', v.flag('testFromAtli') == 1)

print()
print('D3: Atli blame beat — the lake story set gunnarSpokeStone')
check('gunnarSpokeStone set', v.flag('gunnarSpokeStone') == 1)

print()
print('D4: Thordis Test tier + the gated confrontation (Hoskuld blame)')
err, menus = v.talk('THORDIS', ['How are you called?', 'bye'])
check('Thordis first contact completes', err is None, err)
# With testFromAtli AND gunnarSpokeStone both set, the menu REPLACES
# the plain stone ask with the confrontation line (survey: the
# gunnarSpokeStone ternary in the Test tier).
err, menus = v.talk('THORDIS',
                    ["The Gunnar's say you have the Stone.", 'bye'])
check('confrontation completes', err is None,
      (err or '') + '  ' + menus_str(menus))
check('hoskuldSpokeStone set by the confrontation',
      v.flag('hoskuldSpokeStone') == 1)

print()
print('D5: menu gating proof — confrontation replaced the plain ask')
opts = menus[0][0] if menus else []
check("menu offered \"The Gunnar's say you have the Stone.\"",
      "The Gunnar's say you have the Stone." in opts, str(opts))
check('menu did NOT offer the plain "Where is the Passage Stone?"',
      'Where is the Passage Stone?' not in opts, str(opts))
check('Test tier present (testFromAtli respected)',
      'Tell me of the Test.' in opts, str(opts))

print()
print('D6: Ingjald first contact — Pagan rant, spokeOnce/spokeOfVale')
v2 = Village()
err, menus = v2.talk('INGJALD', ['What is your name?', 'bye'])
check('name convo completes', err is None, err)
check('ingyaldMet set', v2.flag('ingyaldMet') == 1)
err, menus = v2.talk('INGJALD', ['What place is this?', 'Zealans?',
                                 'Gunnar?', 'bye'])
check('vale intro completes', err is None,
      (err or '') + '  ' + menus_str(menus))
check('spokeOnce set', v2.flag('spokeOnce') == 1)
check('spokeOfVale set', v2.flag('spokeOfVale') == 1)

print()
print('D7: shared spokeOnce redirects Hrodny to "see Atli"')
err, menus = v2.talk('HRODNY', ['What is your name?', 'bye'])
check('Hrodny name convo completes', err is None, err)
err, menus = v2.talk('HRODNY', ["I'd like to speak to you.",
                                'Who is Atli?',
                                'What is Clan Gunnar?', 'bye'])
check('redirect + clan lore completes', err is None,
      (err or '') + '  ' + menus_str(menus))

print()
print('D8: Ragnar — met-branch persists (step-7 repair, lv-patched '
      'change 1: the RAGNAR.UNK:118 debug reset is gone)')
v3 = Village()
err, menus = v3.talk('RAGNAR', ['What is your name?', 'Farewell.'])
check('first convo completes', err is None,
      (err or '') + '  ' + menus_str(menus))
check('first convo offered the fresh menu',
      menus and 'What is your name?' in menus[0][0],
      menus_str(menus))
check('ragnarMet set after convo', v3.flag('ragnarMet') == 1)
check('ragnarName set', v3.flag('ragnarName') == 1)
err, menus = v3.talk('RAGNAR', ['Farewell.'])
check('second convo completes on the MET menu', err is None,
      (err or '') + '  ' + menus_str(menus))
met_opts = menus[0][0] if menus else []
check('MET menu: fresh options gone',
      'What is your name?' not in met_opts
      and 'What do you do here?' not in met_opts, str(met_opts))
check('ragnarMet still set after second convo',
      v3.flag('ragnarMet') == 1)

print()
print('D9: Tyorvi pre-Mark wall — only name/job, drunk rant')
v4 = Village()
err, menus = v4.talk('TYORVI', ['What is your name?'])
check('drunk rant exits on its own', err is None,
      (err or '') + '  ' + menus_str(menus))
check('tyorviMet set', v4.flag('tyorviMet') == 1)
if menus:
    first_menu = menus[0][0]
    check('pre-Mark menu contains no quest options',
          all(o in ('What is your name?', 'What do you do?', 'bye', '')
              for o in first_menu), str(first_menu))

print()
print('D10: Ezrekal conversation RESTORED (parser truncation fixed '
      '2026-07-04: typed-arg casts + scoped block recovery)')
v5 = Village()
v5.setflag('haveMark')
err, menus = v5.talk('EZREKAL', ['May I know your name?', 'bye'])
check('recognized greeting reaches a real menu and completes',
      err is None and len(menus) >= 2,
      (err or '') + f'  asks={len(menus)}')
check('ezrekalMet set', v5.flag('ezrekalMet') == 1)
# The unrecognized wall still stands: no Mark = rant, no menu (5 of 6
# rants exit; the sixth random slot leaks to the menu — 1994 bug, so
# only assert the flag, not the menu count).
v5b = Village()
err, menus = v5b.talk('EZREKAL', ['May I know your name?', 'bye'])
check('no-Mark visit completes (rant or the 1-in-6 menu leak)',
      err is None or 'empty answer script' not in (err or ''),
      err)

print()
print('D11: BUG 1 REPAIR — Ragnar bag beat reachable ORGANICALLY, no dead flag')
# The whole tale-and-bag beat used to hang off "Atli sent me to you.",
# gated on sentToRagnar (bit 0x449) which NOTHING in the build writes — so
# in natural play the option never appeared and the beat was dead. The old
# D11 hid this by force-SETTING sentToRagnar (a dead flag) so the look-alike
# option surfaced in the sim. lv-patched/RAGNAR change 9 re-gates the
# top-menu add on atliMet (the durable "you have met Atli" flag) and uses
# `+=` (append) so it isn't dropped on the empty menu. This test reaches
# atliMet the NATURAL way (meet Atli), meets Ragnar (ragnarMet), then RETURNS
# and walks the tale subtree to the bag — every pick taken only from the
# menu the class offered (walk() asserts it; a force-drive would raise).
v6 = Village()
# 1) Meet Atli — his first-contact conversation is what sets atliMet.
walk(v6, 'ATLI', ['May I speak with you?', 'What is your name?',
                  'What do you do?', 'bye'])
check('atliMet set by meeting Atli (organic, not force-set)',
      v6.flag('atliMet') == 1)
check('sentToRagnar still 0 — the dead flag is NEVER written',
      v6.flag('sentToRagnar') == 0)
# 2) First Ragnar conversation: only the fresh menu is offered; it sets
#    ragnarMet. (This also proves change 10: the fresh greeting shows.)
walk(v6, 'RAGNAR', ['What is your name?', 'Farewell.'],
     must_offer=('What is your name?',))
check('ragnarMet set by meeting Ragnar (organic)', v6.flag('ragnarMet') == 1)
# 3) Return to Ragnar: the re-gated top menu now offers the referral off
#    atliMet. Walk the tale subtree to the bag, only offered options.
err, menus = walk(v6, 'RAGNAR',
                  ['Atli sent me to you.', 'Atli admires you.',
                   'I believe that he is sincere.',
                   'He said you know many things.',
                   'Do you know of the Passage Stone?', 'Yes, I do.',
                   'Why do you not go there?', 'Farewell.'],
                  must_offer=('Atli sent me to you.',
                              'Do you know of the Passage Stone?',
                              'Why do you not go there?'))
check('ragnarToldStone set by the lake-ruins beat (organic reach)',
      v6.flag('ragnarToldStone') == 1)
# The bag drop: TypeBag popped at the lake ruins with a TypeBushKey inside.
# Shapes via TYPE_SHAPES (the compiler's TypeXXX table) — no hardcoded ids.
bag_shape = TYPE_SHAPES['TypeBag']
key_shape = TYPE_SHAPES['TypeBushKey']
bags = [v6.world.items[o] for o in v6.sim.created
        if v6.world.items[o].shape == bag_shape]
check('TypeBag created and popped at (16447,25727,64)',
      any((b.x, b.y, b.z) == (16447, 25727, 64) and not b.ethereal
          and not b.destroyed for b in bags),
      str([(b.x, b.y, b.z, b.ethereal) for b in bags]))
keys_in_bag = [oid for b in bags for oid in b.contents
               if v6.world.items[oid].shape == key_shape]
check('TypeBushKey (the stone) inside the bag', len(keys_in_bag) == 1,
      f'keys in bag: {keys_in_bag}; created: '
      f'{[(o, v6.world.items[o].shape) for o in v6.sim.created]}')

print()
print('D11b: restored no-fight handler reachable ORGANICALLY (fresh convo)')
# The 'I have no fight with you.' handler (lv-patched change 8) sits on the
# peaceful chain off a FRESH Ragnar convo (thordisMet clear). Reach it with
# only offered options; it must bark once and CONTINUE the menu loop.
v6b = Village()
_err, menus = walk(v6b, 'RAGNAR',
                   ['What is your name?', 'From very far away.',
                    "Yes, I'm peaceful.", 'I have no fight with you.',
                    'I am peaceful with all.', 'Farewell.'],
                   must_offer=('I have no fight with you.',))
check('no-fight handler barked the in-voice reply',
      any('no quarrel between us' in t for _o, t in v6b.sim.barks),
      str([t for _o, t in v6b.sim.barks][-6:]))
check('menu loop continued after the no-fight pick (next pick landed)',
      any(a == 'I am peaceful with all.' for _m, a in menus))

print()
print('D12: POISON-CURE ARC (steps 9-12) — repaired end to end')
print('     (shape sweep: TypeBottle 340->395->868, TypeCliffKey 641->82,')
print('      TypeWeedz 126->399->869 f0; lv-patched/EZREKAL.UNK: root . / elixir \\g')
print('      / hasTea writer). Execution-pinned dead pre-repair — see the')
print('      step 9-12 report.')

# Shapes the arc give()/foreach filters push — assert the sweep landed.
# TypeBottle is the elixir's own custom shape since 2026-10-09
# (docs/art-track.md contract 11; lv-patched EZREKAL/TYORVI V3). Before it,
# 395 frame 5 was the Blood reagent: the elixir read "1 vial of blood",
# merged with carried blood, and Tyorvi's drink destroyed carried blood.
ELIXIR_SHAPE = 868
BLOOD = 395          # the necromancy reagent vial; frames 0-5 are Blood
check('TypeBottle is the elixir\'s own shape 868 (off the 340 door-shape '
      'trap and the 395 Blood reagent)',
      TYPE_SHAPES['TypeBottle'] == ELIXIR_SHAPE, str(TYPE_SHAPES['TypeBottle']))
check('TypeCliffKey swept off the 641 SI_FIXED-skull trap',
      TYPE_SHAPES['TypeCliffKey'] == 82, str(TYPE_SHAPES['TypeCliffKey']))
check('TypeWeedz is the special root\'s own shape 869 (off the 126 '
      'SI_FIXED-vegetation trap and the 399 "eye of newt"; contract 12)',
      TYPE_SHAPES['TypeWeedz'] == 869, str(TYPE_SHAPES['TypeWeedz']))

# R2: the filters read frame 0 of 869, so a carried "eye of newt" (399
# frame 9, the old stand-in) is not the root any more.
vd = Village()
for f in ('haveMark', 'avatarPoisoned', 'ezrekalMet', 'ezrekalName',
          'tyorviDreams'):
    vd.setflag(f)
newt = vd.additem(399, frame=9)
_err, _menus = vd.talk('EZREKAL', ['bye'])
check('R2: a carried 399 frame 9 does not offer "I have found the root."',
      _err is None and 'I have found the root.' not in menus_str(_menus),
      (_err or '') + '  ' + menus_str(_menus))
check('R2: and it is not destroyed', not newt.destroyed)

# D12a — Ezrekal sends the Avatar to Tyorvi. The poison->heal->cliffs
# menu chain (discovered by execution) ends at "Perhaps I will try the
# Cliffs.", which sets sentToTyorvi. This path was already live once
# Ezrekal compiled; it gates the whole arc, so pin it.
print()
print('  D12a: sentToTyorvi via the poison->heal->cliffs chain')
va = Village()
for f in ('haveMark', 'avatarPoisoned', 'ezrekalMet', 'ezrekalName'):
    va.setflag(f)
CLIFFS_CHAIN = [
    'Can you help me?', 'I have been poisoned.', "But I'm dying!",
    'Prepare my funeral?!', 'I want to be healed!', "I don't want a funeral!",
    'You said the Ancient Ones were gone!', 'What kind of eternal peace?',
    'Where will I be until then?', 'When will they return?',
    'A city in the clouds?', "I don't want to be an undead!", 'Cloud City?',
    'How?! How can I be healed?', 'Where is the Cloud City?',
    'Tell me more of the Cloud City.', 'Are the Ancient Ones still there?',
    'Perhaps I will try the Cliffs.', 'bye']
err, menus = va.talk('EZREKAL', CLIFFS_CHAIN)
check('cliffs chain completes', err is None,
      (err or '') + '  ' + menus_str(menus))
check('sentToTyorvi set by "Perhaps I will try the Cliffs."',
      va.flag('sentToTyorvi') == 1)

# D12b — the root hand-in. lv-patched change 1 (root period): the offered
# "I have found the root." now dispatches its case. Pre-repair the case
# was "...root!" so the pick was silently dropped (givenRoot never set,
# the root never consumed) — execution-confirmed dead in the report.
print()
print('  D12b: root hand-in dispatches (lv-patched: case . matches menu .)')
vb = Village()
for f in ('haveMark', 'avatarPoisoned', 'ezrekalMet', 'ezrekalName',
          'tyorviDreams'):
    vb.setflag(f)
root = vb.additem(TYPE_SHAPES['TypeWeedz'], frame=0)
err, menus = vb.talk('EZREKAL', ['I have found the root.', 'bye'])
check('root convo completes', err is None,
      (err or '') + '  ' + menus_str(menus))
check('givenRoot set by the root hand-in (defect A repaired)',
      vb.flag('givenRoot') == 1)
check('justGotRoot set by the root hand-in', vb.flag('justGotRoot') == 1)
check('the TypeWeedz(869) frame-0 root was consumed (destroyed)',
      root.destroyed and len(vb.inv(TYPE_SHAPES['TypeWeedz'], 0)) == 0)

# D12c — the elixir hand-off, reached ORGANICALLY end to end, with the 1994
# brewing wait (lv-patched/EZREKAL W1-W3, 2026-10-08). After the root,
# Ezrekal offers only "Is Tyorvi's elixir ready yet?" (W1 respelled its
# add to match its case; W3 offers it in the root's own menu) and answers
# with patience; "Have you made the elixir?" is offered once justGotRoot is
# clear (W2, the 1994 gate), which her leaveFastArea does when the Avatar
# walks away. E3 keeps the replay guard live so a repeat visit cannot dupe
# the vial.
#
# UPDATED 2026-07-19 (undeclared-globalflag repair): givenElixir is now a
# REAL allocated flag (declared in lv-patched/FLAGS.UNK, pinned at bit 1827),
# so E3's guard is back to the literal 1994 `if givenElixir = true` instead of
# the hasTea stand-in. Step 5 below asserts the dupe path is closed and, in
# particular, that it is closed BY givenElixir: it clears hasTea before the
# third visit, which under the old hasTea-keyed guard would have re-run the
# give branch and handed out a second vial.
print()
print('  D12c: elixir hand-off ORGANIC — patience while justGotRoot=1, '
      'hand-over after leaveFastArea')
vc = Village()
for f in ('haveMark', 'avatarPoisoned', 'tyorviDreams'):
    vc.setflag(f)   # legit prior state: Passage Test + Tyorvi's dream gate
# 1) First recognized visit sets ezrekalMet/ezrekalName (organic).
walk(vc, 'EZREKAL', ['May I know your name?', 'bye'],
     must_offer=('May I know your name?',))
check('ezrekalMet set by meeting Ezrekal (organic)', vc.flag('ezrekalMet') == 1)
# 2) Root (TypeWeedz frame 0) in inventory; hand it in -> givenRoot (organic).
READY = "Is Tyorvi's elixir ready yet?"
MADE = 'Have you made the elixir?'
root = vc.additem(TYPE_SHAPES['TypeWeedz'], frame=0)
_err, menus = walk(vc, 'EZREKAL', ['I have found the root.', 'bye'],
                   must_offer=('I have found the root.',))
check('givenRoot set by the root hand-in (organic)', vc.flag('givenRoot') == 1)
check('justGotRoot set by the root hand-in', vc.flag('justGotRoot') == 1)
check('the TypeWeedz(869) frame-0 root was consumed',
      root.destroyed and len(vc.inv(TYPE_SHAPES['TypeWeedz'], 0)) == 0)
check('W3: the root menu swaps to the patience question at once',
      len(menus) == 2 and READY in menus[1][0]
      and 'I have found the root.' not in menus[1][0], menus_str(menus))
# 3) Still beside her (justGotRoot=1): only the patience question. Picking
#    it must DISPATCH — the case exits the conversation, so exactly one
#    menu is shown. Before W1 the add read "...ready?" against a
#    "...ready yet?" case and the pick re-asked forever.
_err, menus = walk(vc, 'EZREKAL', [READY, 'bye'], must_offer=(READY,))
check('W2: no hand-over while justGotRoot=1 (she is still brewing)',
      not any(MADE in m for m, _a in menus), menus_str(menus))
check('W1: the patience pick dispatched (conversation ended on it)',
      len(menus) == 1, menus_str(menus))
check('patience pick handed nothing over', vc.flag('givenElixir') == 0)
# 3b) R1 (lv-patched/EZREKAL.UNK, 2026-10-09): the patience answer ALWAYS
#     barks. The case barks for ran = 1, 2 or 3, and the engine's urandom(n)
#     is 0..n-1 (UCMachine::I_urandom), so the 1994 `urandom(4)` said
#     nothing one pick in four. Drive every value the roll can take and
#     require exactly one patience line each time, and all three lines over
#     the sweep. The case's roll is the conversation's LAST urandom (the
#     greeting may roll first), so one unscripted probe finds its index and
#     its range, and each scripted run pins that index alone.
PATIENCE = ('Patience, my friend', 'Not so quickly', 'always in a hurry')
vc.sim.urandom_script = []
_r0 = len(vc.sim.urandom_rolls)
walk(vc, 'EZREKAL', [READY, 'bye'], must_offer=(READY,))
_rolls = vc.sim.urandom_rolls[_r0:]
check('the patience case rolls urandom', bool(_rolls), str(_rolls))
_k, _n = len(_rolls) - 1, (_rolls[-1][0] if _rolls else 0)
_said = set()
for _v in range(_n):
    vc.sim.urandom_script = [None] * _k + [_v]
    _r0, n0 = len(vc.sim.urandom_rolls), len(vc.sim.barks)
    walk(vc, 'EZREKAL', [READY, 'bye'], must_offer=(READY,))
    _lines = [p for _o, t in vc.sim.barks[n0:] for p in PATIENCE if p in t]
    check(f'R1: patience roll urandom({_n}) = {_v} barks one patience line',
          len(_lines) == 1 and vc.sim.urandom_rolls[_r0:][-1:] == [(_n, _v)],
          f'lines={_lines} rolls={vc.sim.urandom_rolls[_r0:]}')
    _said.update(_lines)
vc.sim.urandom_script = []
check('R1: all three patience lines are reachable', len(_said) == 3,
      str(sorted(_said)))
check('patience sweep handed nothing over', vc.flag('givenElixir') == 0)
# 4) The Avatar walks away: her leaveFastArea (event 0x10) clears the flag.
_lerr = None
try:
    vc.sim.run_event(NPC['EZREKAL'], None, vc.npcs['EZREKAL'].objid,
                     max_steps=200000, event=0x10)
except SimError as e:
    _lerr = str(e)
check('Ezrekal leaveFastArea ran', _lerr is None, str(_lerr))
check('leaveFastArea cleared justGotRoot', vc.flag('justGotRoot') == 0)
# 5) Back with her: the hand-over is offered and the patience question gone.
n0 = len(vc.sim.barks)
_err, menus = walk(vc, 'EZREKAL', [MADE, 'bye'], must_offer=(MADE,))
check('patience question NOT offered once justGotRoot is clear',
      not any(READY in m for m, _a in menus), menus_str(menus))
check('elixir case dispatched — "Take it to him" bark',
      any('Take it to him' in t for _o, t in vc.sim.barks[n0:]),
      str([t for _o, t in vc.sim.barks[n0:]][-4:]))
check('hasTea set by the elixir hand-off', vc.flag('hasTea') == 1)
# givenElixir is now a live allocated flag, so the 1994 writer in this same
# branch actually lands. Pre-repair (undeclared) this read back 0 — this is
# the assertion that would have caught the dead flag.
check('givenElixir set by the elixir hand-off (flag is live, not push-0)',
      vc.flag('givenElixir') == 1)
# 6) The vial itself: give()/createNear() are cross-class FREE calls the sim
#    stubs (return 0, no item created) — so, exactly as D12d does for
#    Tyorvi's key, the vial creation is verified STATICALLY. Both calls push
#    (quan, qual, frame, shape) and then their first argument, so the frame
#    is the push three before each call whose shape push is the elixir's
#    and the quantity the push five before. The frame must be ELIXIR_FRAME
#    (V3, 2026-10-09: 868 has one frame, 0) and equal the frame TYORVI's two
#    drink filters search for (D12d). The quantity must be 1 (V2): 868 is
#    SF_GENERIC, and FREE::give does `quan--; while quan` for a
#    non-quantity family, so a 0 would create items until the pack fills.
ELIXIR_FRAME = 0
_ezflx = UsecodeFlexArchive(BUILD_FLX)
_ezins = UsecodeDisassembler().disassemble_bytecode(
    _ezflx.get_class_data(NPC['EZREKAL']), start_offset=0x80)
_ezcalls = [i for i, ins in enumerate(_ezins)
            if ins.opcode == 0x11 and i >= 5
            and _ezins[i - 2].opcode == 0x0B
            and _ezins[i - 2].operands[0][1] == ELIXIR_SHAPE]
_ezframes = [_ezins[i - 3].operands[0][1] for i in _ezcalls]
_ezquans = [_ezins[i - 5].operands[0][1] for i in _ezcalls]
check(f'compiled EZREKAL give()+createNear() make the {ELIXIR_SHAPE} elixir '
      f'at frame {ELIXIR_FRAME}', _ezframes == [ELIXIR_FRAME, ELIXIR_FRAME],
      f'frames pushed before the two elixir calls: {_ezframes}')
check('and with quantity 1 (V2; one item of a non-quantity family)',
      _ezquans == [1, 1], f'quantities: {_ezquans}')
# 7) DUP GUARD (the givenElixir repair). The give-elixir option stays offered
#    for as long as givenTea is clear (the hand-over cleared justGotRoot, so
#    W2's gate holds open), so the Avatar can
#    walk back to Ezrekal any number of times between receiving the elixir and
#    delivering it to Tyorvi. Every one of those repeat visits must hit the
#    "already gave it" guard and must NOT re-run the give branch.
#
#    give()/createNear() are cross-class FREE calls the sim stubs (no item is
#    ever created), so "how many bottles exist" is counted the way the rest of
#    this harness counts it: by how many times the give branch EXECUTED. The
#    branch's "Take it to him" bark fires exactly once per execution and
#    immediately precedes the give()/createNear() pair, so its count over the
#    whole session IS the number of vials handed out.
n1 = len(vc.sim.barks)
_err, menus = walk(vc, 'EZREKAL', ['Have you made the elixir?', 'bye'],
                   must_offer=('Have you made the elixir?',))
check('2nd attempt hits the "already gave it" guard (E3, live givenElixir)',
      any('gave it to you already' in t for _o, t in vc.sim.barks[n1:]),
      str([t for _o, t in vc.sim.barks[n1:]][-4:]))
check('2nd attempt did NOT re-run give() (no second "Take it to him")',
      not any('Take it to him' in t for _o, t in vc.sim.barks[n1:]))
check('hasTea still set after the guarded repeat (no dupe)',
      vc.flag('hasTea') == 1)
#    A THIRD visit with hasTea forcibly cleared. This is the discriminating
#    case: it is the state the OLD hasTea-keyed guard could not defend, and it
#    is defended now only because givenElixir is a real allocated flag. If
#    givenElixir were still undeclared (push-0/pop-0) this visit would fall
#    through to the else branch and hand out a SECOND vial.
vc.setflag('hasTea', 0)
check('givenElixir survives independently of hasTea', vc.flag('givenElixir') == 1)
n2 = len(vc.sim.barks)
_err, menus = walk(vc, 'EZREKAL', ['Have you made the elixir?', 'bye'],
                   must_offer=('Have you made the elixir?',))
check('3rd attempt (hasTea cleared) still hits the guard — givenElixir holds it',
      any('gave it to you already' in t for _o, t in vc.sim.barks[n2:]),
      str([t for _o, t in vc.sim.barks[n2:]][-4:]))
check('3rd attempt did NOT re-run give() (no third "Take it to him")',
      not any('Take it to him' in t for _o, t in vc.sim.barks[n2:]))
# The bottom line: across THREE visits after receiving the elixir and before
# givenTea, the give branch ran exactly ONCE — exactly one vial exists.
_gives = sum(1 for _o, t in vc.sim.barks if 'Take it to him' in t)
check('EXACTLY ONE elixir vial handed out across 3 visits (dupe path closed)',
      _gives == 1, f'give-branch executions = {_gives}, expected 1')
vc.setflag('hasTea', 1)   # restore the real post-hand-off state

# D12d — Tyorvi's delivery, gated by hasTea (TYORVI.UNK:351). With hasTea
# set (D12c) Tyorvi offers "I have something for you from Ezrekal.";
# driving the drink chain consumes the TypeBottle (868) elixir and
# hands over the Key to the Clouds, setting givenTea. iAmDrunk is now a REAL
# allocated flag (bit 1828, declared in lv-patched/FLAGS.UNK) rather than the
# push-0 no-op it used to be, so it must be left CLEAR here for the sober
# path to run — keep both it and tyorviDrunk clear.
print()
print('  D12d: Tyorvi delivery — drink chain consumes the elixir, reaches')
print('        the Key-to-the-Clouds handover')
# Both drink paths, each with the elixir AND two vials of Blood in the pack:
# frame 5, which the drink filters searched for until V3 (2026-10-09) and so
# destroyed along with the elixir, and frame 0, the Bag of Reagents' stock.
# The drink must take the elixir and leave every vial of blood.
DRINK_PATHS = (
    ('sober "Just try it, please."', 0,
     ['I have something for you from Ezrekal.', 'It is an elixar.',
      'It will heal your dreams.', 'Just try it, please.', 'bye']),
    ('drunk "Shut up and drink it!"', 1,
     ['I have something for you from Ezrekal.', 'It is an elixar.',
      'It is a potion.', 'It will heal your dreams.',
      'Shut up and drink it!', 'bye']),
)
for _path, _drunk, _answers in DRINK_PATHS:
    vd = Village()
    for f in ('haveMark', 'tyorviMet', 'hasTea'):
        vd.setflag(f)
    vd.setflag('tyorviDrunk', _drunk)
    bottle = vd.additem(ELIXIR_SHAPE, frame=ELIXIR_FRAME)
    blood = [vd.additem(BLOOD, frame=_f) for _f in (5, 0)]
    # Drive the drink chain up to (but not through) the give()-containing
    # Key case: give()/createNear() are FREE routines that, on the quan>=1
    # path, descend into retail METHOD bytecode the sim does not model — so
    # the key CREATION + givenTea-set at TYORVI.UNK:2132-2143 are NOT
    # sim-observable. The consumption IS: the elixir foreach.destroy() runs
    # under the drink pick, which then offers the Key request.
    err, menus = vd.talk('TYORVI', _answers)
    check(f'{_path}: drink chain completes', err is None,
          (err or '') + '  ' + menus_str(menus))
    check(f'{_path}: hasTea gate offered the delivery entry',
          any('something for you from Ezrekal' in o
              for m, _a in menus for o in m))
    check(f'{_path}: the {ELIXIR_SHAPE} frame-{ELIXIR_FRAME} elixir is '
          f'consumed', bottle.destroyed
          and len(vd.inv(ELIXIR_SHAPE, ELIXIR_FRAME)) == 0)
    check(f'{_path}: both vials of blood ({BLOOD} frames 5 and 0) survive',
          not any(b.destroyed for b in blood),
          f'destroyed frames: {[b.frame for b in blood if b.destroyed]}')
    check(f'{_path}: drink chain reached the Key-to-the-Clouds handover',
          any('May I have the Key to the Clouds?' in o
              for m, _a in menus for o in m))
    # TYORVI T9: the pause before "Hmmm, taste too bad..." is a wait() in
    # 60 Hz ticks (FREE 0581:1C19 polls getCurrentTimerTick, which is
    # Kernel::getTickNum). The 1994 wait (1000) was 16.7 s of a silent
    # conversation (docs/playtest-2026-10-11-full-run-part6.md finding 1);
    # retail's own conversation pause is TORWIN's wait(30).
    _waits = [int.from_bytes(_sp['args'][:2], 'little')
              for _sp in vd.sim.spawns
              if _sp['class'] == 0x581 and _sp['offset'] == 0x1C19]
    check(f'{_path}: the drink pause is at most 2 s (wait <= 120 ticks)',
          bool(_waits) and max(_waits) <= 120, f'wait ticks: {_waits}')
    check(f'{_path}: the follow-up bark "Hmmm, taste too bad..." is '
          f'spoken', any('taste too bad' in t for _o, t in vd.sim.barks),
          str([t[:40] for _o, t in vd.sim.barks][-4:]))
check('the drunk drink sobers Tyorvi (tyorviDrunk cleared)',
      vd.flag('tyorviDrunk') == 0)
# Both drink filters (sober "Give it to me" and "Shut up and drink it!",
# TYORVI.UNK V3) must search for the shape and frame EZREKAL creates. A
# foreach compiles to loopscr bytes; `(type = S) and (frame = F)` emits
# F_hi F_lo 'a' S_hi S_lo 'A'. Read every elixir-shape frame back out.
_tyall = UsecodeDisassembler().disassemble_bytecode(
    UsecodeFlexArchive(BUILD_FLX).get_class_data(NPC['TYORVI']),
    start_offset=0x80)
_tyframes, _tytypes, _run = [], [], []
_shape_ls = [0x61, ELIXIR_SHAPE >> 8, ELIXIR_SHAPE & 0xFF, 0x41]
for _idx, _ins in enumerate(_tyall + [None]):
    if _ins is not None and _ins.opcode == 0x74:
        _run.append(_ins.operands[0][1])
        continue
    for _k in range(5, len(_run)):
        if _run[_k - 3:_k + 1] == _shape_ls:
            _tyframes.append(_run[_k - 5] << 8 | _run[_k - 4])
            # The `loop` (0x70) that consumes this script: its last operand
            # is the search type, 0x04 container, 0x05 container+recursive.
            _lp = next((i for i in _tyall[_idx:] if i.opcode == 0x70), None)
            _tytypes.append(_lp.operands[-1][1] if _lp else None)
    _run = []
check(f'compiled TYORVI drink filters both search {ELIXIR_SHAPE} frame '
      f'{ELIXIR_FRAME}', _tyframes == [ELIXIR_FRAME, ELIXIR_FRAME],
      f'{ELIXIR_SHAPE} frames in TYORVI loop scripts: {_tyframes}')
# TYORVI V2: both drink filters search recursively, so the vial is found in
# the backpack. The sober path's non-recursive foreach left it there while
# the Key was handed over (docs/playtest-2026-10-08-batch-a.md finding 2).
check('compiled TYORVI drink filters are both recursive (search type 5)',
      _tytypes == [0x05, 0x05], f'search types: {_tytypes}')

# Static verification of the final handover (not sim-observable, see above):
# the COMPILED Tyorvi class must give the swept key shape and set givenTea.
_flx = UsecodeFlexArchive(BUILD_FLX)
_ty = _flx.get_class_data(NPC['TYORVI'])
_instrs = UsecodeDisassembler().disassemble_bytecode(_ty, start_offset=0x80)
_pushed = {v for ins in _instrs for _t, v in ins.operands if isinstance(v, int)}
_popglobals = {ins.operands[0][1] for ins in _instrs if ins.opcode == 0x4F}
check('compiled TYORVI pushes the swept TypeCliffKey shape for give() '
      f'(={TYPE_SHAPES["TypeCliffKey"]})',
      TYPE_SHAPES['TypeCliffKey'] in _pushed)
check('compiled TYORVI writes givenTea (pop-global) — Key handover sets it',
      FLAG['givenTea'] in _popglobals)
# TYORVI T7: give() and createNear() take (type, frame, quality, quantity),
# pushed last argument first: 1, quality, 0, 82. Both must stamp the Key
# with quality 170, the only one lv-new/CLCLIMB.UNK's handholds accept
# (test_uc_eggs.py P1-P1d); at 0 it was a retail "key blank".
_kq = [_instrs[i + 1].operands[0][1] for i in range(len(_instrs) - 3)
       if all(_instrs[i + k].opcode in (0x0A, 0x0B) for k in range(4))
       and [_instrs[i + k].operands[0][1] for k in (0, 2, 3)]
       == [1, 0, TYPE_SHAPES['TypeCliffKey']]]
check('compiled TYORVI makes the Key at quality 170 in give() and '
      'createNear()', _kq == [170, 170], f'qualities pushed: {_kq}')

# D12e — after the handover (givenTea set) the delivery is no longer
# offered, on either of its two menu adds (lv-patched/TYORVI.UNK T2,
# original lines 351 and 2213). hasTea is never cleared, so before T2 every
# later talk re-offered it and the chain handed out a second Key to the
# Clouds (playtest 2026-10-07 wave 2 B).
print()
print('  D12e: Tyorvi does not re-offer the delivery once givenTea is set')
DELIVERY = 'something for you from Ezrekal'
for path, setup, answers in (
        ('greeting menu (original line 351)', (), ['bye']),
        ('apology menu (original line 2213)', ('tyorviPissed',),
         ['Calm down, Tyorvi.', 'I wish to apologize for my rudeness.',
          'bye'])):
    for given in (0, 1):
        ve = Village()
        for f in ('haveMark', 'tyorviMet', 'hasTea') + setup:
            ve.setflag(f)
        ve.setflag('tyorviDrunk', 0)
        ve.setflag('givenTea', given)
        _err, menus = ve.talk('TYORVI', answers)
        offered = any(DELIVERY in o for m, _a in menus for o in m)
        check(f'{path}, givenTea={given}: delivery '
              f'{"not " if given else ""}offered',
              offered != bool(given), menus_str(menus))

print()
print('D13: PASSAGE TEST AFTERMATH restored to Atli (orphan triage decision H,')
print('     lv-patched/ATLI.UNK) — TESTPLAN.UNK:163-193, the ~30 lines the')
print('     PLNTST scene merge dropped without a note. They are Atli\'s own')
print('     lines (TESTPLAN branches on thordisToldTest and teleports HIM in),')
print('     and they carry the only pointer to quest step 9.')

# The three 1994 lines that carry the beat: the poison, the verdict, and the
# routing. If any of these stops firing, the player is told nothing again.
KEY_LINES = ('No antidote there is',
             'afraid you are doomed I am',
             'speak to Ezrekal you can')


def said_since(v, n):
    return [t for _o, t in v.sim.barks[n:]]


# D13a — it fires on the first conversation after the Test, and it is a
# SCENE not a menu pick: the whole exchange runs and exits without ever
# calling ask() (the empty answer script would raise if it did).
print()
print('  D13a: fires once after the Test, as a scene (no menu)')
v7 = Village()
v7.setflag('haveMark')          # set by lv-patched/PLNTST.UNK:186 at scene end
v7.setflag('thordisToldTest')   # TESTPLAN's own discriminator for the Atli half
v7.setflag('plantScene')        # taken out by lv-patched/PLNTST.UNK:82
check('endOfPlantScene clear before the aftermath', v7.flag('endOfPlantScene') == 0)
err, menus = v7.talk('ATLI', [])
check('aftermath completes without asking anything',
      err is None and not menus, (err or '') + f'  menus={menus}')
said = said_since(v7, 0)
for _line in KEY_LINES:
    check(f'1994 line restored: "...{_line}..."',
          any(_line in t for t in said), str(said[-3:]))
check('the Avatar\'s scripted half restored ("No antidote?!")',
      any('No antidote?!' in t for t in said), str(said[-3:]))
check('opens on the 1994 first line ("Heard Thordis sent you here, I had")',
      any('Heard Thordis sent you here' in t for t in said), str(said[:2]))

# D13b — the one-shot latch. endOfPlantScene is a 1994-declared globalflag
# (bit 1050) that had ZERO readers and ZERO writers in the whole corpus; the
# restored block is its first of each. Poison-independent by design: the
# guard keys on haveMark, NOT avatarPoisoned, which decision A left with no
# writer at all — so this branch works with the poison off AND back on.
print()
print('  D13b: one-shot — endOfPlantScene latches, aftermath never repeats')
check('endOfPlantScene latched by the exchange', v7.flag('endOfPlantScene') == 1)
check('avatarPoisoned still unwritten (guard does NOT depend on it — dec. A)',
      v7.flag('avatarPoisoned') == 0)
check('plantScene CLEARED by the exchange — the elders are unfrozen '
      '(lv-patched/ATLI.UNK change 3, site 1)', v7.flag('plantScene') == 0)
_n = len(v7.sim.barks)
err, menus = v7.talk('ATLI', ['bye'])
check('second conversation reaches the normal menu', err is None and menus,
      (err or '') + '  ' + menus_str(menus))
_again = said_since(v7, _n)
check('aftermath does NOT replay on the second conversation',
      not any(_l in t for _l in KEY_LINES for t in _again), str(_again[:3]))

# D13c — both other guard terms are load-bearing.
print()
print('  D13c: guard terms are load-bearing (haveMark, thordisToldTest)')
v8 = Village()
v8.setflag('thordisToldTest')   # told of the Rite, but never took the Test
err, _m = v8.talk('ATLI', ['bye'])
check('no aftermath without haveMark (the Test was never taken)',
      err is None and not any(_l in t for _l in KEY_LINES
                              for _o, t in v8.sim.barks), (err or ''))
v9 = Village()
v9.setflag('haveMark')
v9.setflag('atliToldTest')      # mirror branch — TESTPLAN gives these to Thordis
err, _m = v9.talk('ATLI', ['bye'])
check('no aftermath on the atliToldTest branch (there they are Thordis\' lines)',
      err is None and not any(_l in t for _l in KEY_LINES
                              for _o, t in v9.sim.barks), (err or ''))

# D13d — lv-patched/ATLI.UNK change 2, the same defect class as the EZREKAL
# root-period bug: the menu-add at line 193 said "I have been poisoned."
# while its case (2331) and its own removal (2346) said "...poisoned!", so
# the offered option matched no case and could not even remove itself. The
# lexer collapses whitespace and truncates at \f, so punctuation was the ONLY
# surviving difference. walk() raises if a pick is not on the offered menu,
# so this test fails loudly if the add and the case ever drift apart again.
# (endOfPlantScene is pre-set here so D13a's block is skipped and this drives
# the pre-existing thread underneath it.)
print()
print('  D13d: "I have been poisoned!" add now matches its case (change 2)')
v10 = Village()
for _f in ('atliMet', 'avatarPoisoned', 'thordisToldTest', 'endOfPlantScene'):
    v10.setflag(_f)
_n = len(v10.sim.barks)
err, menus = walk(v10, 'ATLI', ['I have been poisoned!', 'bye'],
                  must_offer=('I have been poisoned!',),
                  label='ATLI poison thread')
check('the pick dispatched its case (1994 "taking effect already" bark)',
      any('taking effect already the poison is' in t
          for t in said_since(v10, _n)),
      str(said_since(v10, _n)[-3:]))
check('...and the case opened its follow-up "Where did you say she is?"',
      any('Where did you say she is?' in o for _m, _a in menus for o in _m),
      menus_str(menus))

print()
print('D14: plantScene SCENE-END (lv-patched/ATLI.UNK change 3). PLNTST.UNK:82')
print('     sets plantScene as the Passage Test begins and NOTHING in the 1994')
print('     corpus ever cleared it; Atli::schedule and Thordis::schedule both')
print('     return early while it is set, so from quest step 8 onward BOTH clan')
print('     elders stopped moving forever. Site 1 is the aftermath exchange')
print('     above (D13b). Site 2 is the self-heal driven here.')

# D14a — the freeze still HOLDS while the Avatar is on stage. The plateau is
# build_map_10.py's TESTGROUNDS_ORIGIN (12288,29184) 2x2-chunk grid, i.e.
# x [12288,13312) y [29184,30208) on map 10 (MapLostVale), which covers every
# 1994 scene coordinate. This is the assertion that would catch a self-heal
# firing mid-scene and teleporting the elder out from under the Avatar.
print()
print('  D14a: freeze HOLDS while the Avatar is still on the Test Grounds')
v11 = Village()
v11.setflag('plantScene')
_e = v11.schedule('ATLI', avatar_at=(13055, 30079))   # the 1994 arrival cell
check('Atli::schedule runs clean', _e is None, _e or '')
check('plantScene still set at the arrival cell', v11.flag('plantScene') == 1)
_e = v11.schedule('ATLI', avatar_at=(12639, 29567))   # the far whirlwind pop
check('plantScene still set at the far scene coordinate',
      v11.flag('plantScene') == 1, _e or '')

# D14b — and RELEASES once he has left. Three ways off the plateau, each of
# which ends the scene: walking north up the ramp corridor, leaving the map,
# and simply being back in the village.
print()
print('  D14b: freeze RELEASES once the Avatar has left the plateau')
for _label, _at, _map in (('walked north off the plateau', (12800, 28900), 10),
                          ('left the vale entirely', (12800, 29500), 3),
                          ('back in the village', (19200, 6400), 10)):
    v12 = Village()
    v12.setflag('plantScene')
    _e = v12.schedule('ATLI', avatar_at=_at, avatar_map=_map)
    check(f'plantScene cleared — {_label}', v12.flag('plantScene') == 0,
          _e or '')

# D14c — ONE scheduler pass releases BOTH elders. SchedulerProcess::run
# (scheduler_process.cpp) runs one actor's schedule() per tick, slots 1..255
# ascending, waiting on each, once per game hour. Thordis is slot 106 and
# Atli 107, so when only Atli's schedule cleared plantScene she had already
# returned at her own guard and sat on the z 64 plateau one more hour
# (docs/playtest-2026-10-09-final.md finding 2). Her schedule now carries the
# same self-heal (lv-patched/THORDIS.UNK change 6); Atli's stays as the
# backstop. Asserted in the COMPILED bytecode (both schedules read and write
# bit 1049) and by driving a whole pass in slot order to her home teleport.
print()
print('  D14c: one scheduler pass (106, then 107) frees both elders')


def _event_body(class_id, event):
    """Instructions of ONE event handler. disassemble_bytecode runs to the
    end of the class blob, so it is bounded here by the next event entry in
    the 32x4 table — without that, a read from the schedule offset also sees
    use(), which in BOTH elders now writes plantScene, and the assertions
    below would pass or fail for the wrong function."""
    blob = _flx.get_class_data(class_id)[12:]
    offs = sorted({struct.unpack_from('<I', blob, e * 4)[0]
                   for e in range(32)} - {0})
    start = struct.unpack_from('<I', blob, event * 4)[0]
    end = next((o for o in offs if o > start), len(blob))
    return [ins for ins in
            UsecodeDisassembler().disassemble_bytecode(blob, start_offset=start)
            if ins.offset < end]


for _cls in ('THORDIS', 'ATLI'):
    _ins = _event_body(NPC[_cls], 8)
    check(f'compiled {_cls.title()}::schedule READS plantScene (bit '
          f'{FLAG["plantScene"]}) — the freeze it obeys',
          any(ins.opcode == 0x4E and ins.operands[0][1] == FLAG['plantScene']
              for ins in _ins))
    check('...and WRITES it — the self-heal, in its own slot',
          any(ins.opcode == 0x4F and ins.operands[0][1] == FLAG['plantScene']
              for ins in _ins))

# Retail METHOD canSafeTeleport (0x57C 143A) measures both 700-unit gaps with
# FREE 0x581 1CE3, a cross-class call the sim stubs (0 by default, which
# would read "too close"). Every gap in this fixture is over 10000 units, so
# the stub answers 8192. Thordis stands where cp10-test-done.sav has her.
THORDIS_PLATEAU = (13283, 29579, 72)
THORDIS_HOME = (4415, 7423, 0)     # her "at home" point; the sim's hour is 0


def _pass(v, avatar_at):
    """One SchedulerProcess run over the two elders, in slot order. Returns
    Thordis's teleports made during HER slot, before Atli's runs."""
    v.sim.call_returns[(0x581, 0x1CE3)] = 8192
    t = v.npcs['THORDIS']
    t.x, t.y, t.z = THORDIS_PLATEAU
    t.mapnum = v.npcs['ATLI'].mapnum = 10
    n0 = len(v.sim.teleports)
    errs = [v.schedule('THORDIS', avatar_at=avatar_at)]
    hers = [(tp['x'], tp['y'], tp['z'], tp['map'])
            for tp in v.sim.teleports[n0:] if tp['obj'] == NPCNUM['THORDIS']]
    errs.append(v.schedule('ATLI', avatar_at=avatar_at))
    return hers, [e for e in errs if e]


v13 = Village()
v13.setflag('plantScene')
_hers, _errs = _pass(v13, (13055, 30079))   # Avatar still on the plateau
check('on the plateau: both schedules run clean', not _errs, str(_errs))
check('...the flag stays set', v13.flag('plantScene') == 1)
check('...and Thordis stays where the scene put her', not _hers, str(_hers))

v13 = Village()
v13.setflag('plantScene')
_hers, _errs = _pass(v13, (15500, 8000))    # the talk skipped, Avatar gone
check('off the plateau: both schedules run clean', not _errs, str(_errs))
check('...one pass clears plantScene', v13.flag('plantScene') == 0)
check('...and in THAT pass, in her own slot, Thordis teleports home '
      f'{THORDIS_HOME} on map 10 (finding 2: she used to wait an hour)',
      _hers == [THORDIS_HOME + (10,)], str(_hers))

# The scene-end talk path is unchanged: the talk cleared the flag already,
# so her slot goes straight to the home teleport, as it always has.
v13 = Village()
_hers, _errs = _pass(v13, (15500, 8000))
check('talk path (flag already clear): Thordis teleports home as before',
      _hers == [THORDIS_HOME + (10,)] and not _errs, f'{_hers} {_errs}')

print()
print('D15: THORDIS\'S HALF of the Passage Test aftermath (lv-patched/')
print('     THORDIS.UNK). TESTPLAN.UNK:195-224 is the mirror of the block D13')
print('     covers: when Thordis is the elder the hatch teleported in, the')
print('     speech is hers. The PLNTST merge dropped BOTH; D13 restored his,')
print('     this restores hers, and the Test no longer ends in silence on')
print('     either branch.')

# Her three load-bearing 1994 lines: who to blame, the verdict, the routing.
HER_LINES = ('So cruel those Gunnar\'s are',
             'afraid you are doomed I am',
             'speak to Ezrekal you can')
# The two speeches END IDENTICALLY — TESTPLAN gives both elders "afraid you
# are doomed I am" and "speak to Ezrekal you can" word for word — so an
# absence check must use lines only SHE says, or Atli's speech trips it.
HER_ONLY = ('Oh my, terrible this is', 'So cruel those Gunnar\'s are')

# D15a — fires on the first conversation after the Test, as a scene. The
# guard is `thordisToldTest = FALSE`, not `atliToldTest = true`: atliToldTest
# has zero writers in the whole corpus, so a block keyed on it would be born
# dead. The negation is also what lv-patched/PLNTST.UNK:83 itself dispatches
# on, so it means exactly "Thordis is the elder standing here".
print()
print('  D15a: fires once after the Test on the mirror path, as a scene')
v14 = Village()
v14.setflag('haveMark')         # set by lv-patched/PLNTST.UNK:186 at scene end
v14.setflag('plantScene')       # taken out by lv-patched/PLNTST.UNK:82
check('thordisToldTest is clear — the hatch teleported HER in',
      v14.flag('thordisToldTest') == 0)
err, menus = v14.talk('THORDIS', [])
check('aftermath completes without asking anything',
      err is None and not menus, (err or '') + f'  menus={menus}')
said = said_since(v14, 0)
for _line in HER_LINES:
    check(f'1994 line restored: "...{_line}..."',
          any(_line in t for t in said), str(said[-3:]))
check('opens on her own 1994 first line ("Oh my, terrible this is")',
      any('Oh my, terrible this is' in t for t in said), str(said[:3]))
check('the Avatar\'s scripted half restored ("This can not be!")',
      any('This can not be!' in t for t in said), str(said[-3:]))

# D15b — the shared one-shot latch and the shared scene-end.
print()
print('  D15b: latches endOfPlantScene, clears plantScene, never repeats')
check('endOfPlantScene latched by her exchange',
      v14.flag('endOfPlantScene') == 1)
check('plantScene CLEARED — the mirror path now ends its own scene',
      v14.flag('plantScene') == 0)
_n = len(v14.sim.barks)
v14.setflag('avatarPoisoned')   # PLNTST.UNK:194, re-enabled 2026-07-27
v14.setflag('thordisMet')       # her whole ask tree hangs off this
err, menus = v14.talk('THORDIS', ['bye'])
check('second conversation reaches the normal menu', err is None and menus,
      (err or '') + '  ' + menus_str(menus))
check('aftermath does NOT replay',
      not any(_l in t for _l in HER_ONLY for t in said_since(v14, _n)),
      str(said_since(v14, _n)[:3]))
# The 1994 follow-up thread authored for exactly this player — which is why
# the block must NOT set zealanMark (that flag is the discriminator for her
# whole poisoned ask tree, and setting it would route straight past this).
check('...and offers the 1994 mirror-path follow-up ("Help me, I\'ve been '
      'poisoned.")',
      any("Help me, I've been poisoned." in o for _m, _a in menus for o in _m),
      menus_str(menus))
check('zealanMark still unset (deliberate — see the patch header)',
      v14.flag('zealanMark') == 0)

# D15c — both other guard terms are load-bearing.
print()
print('  D15c: guard terms are load-bearing (haveMark, thordisToldTest)')
v15 = Village()
err, _m = v15.talk('THORDIS', ['bye'])
check('no aftermath without haveMark (the Test was never taken)',
      err is None and not any(_l in t for _l in HER_ONLY
                              for _o, t in v15.sim.barks), (err or ''))
v16 = Village()
v16.setflag('haveMark')
v16.setflag('thordisToldTest')  # SHE sent them, so ATLI was teleported in
err, _m = v16.talk('THORDIS', ['bye'])
check('no aftermath on the thordisToldTest branch (there they are Atli\'s)',
      err is None and not any(_l in t for _l in HER_ONLY
                              for _o, t in v16.sim.barks), (err or ''))

# D15d — the two blocks are exact complements: on any given save exactly one
# elder speaks. This is what makes it safe for both to write the shared
# endOfPlantScene latch, and it is the assertion that fails loudly if either
# guard is ever edited alone.
print()
print('  D15d: exactly one elder speaks — the guards are complements')
v17 = Village()
v17.setflag('haveMark')
v17.setflag('thordisToldTest')
v17.talk('ATLI', [])
v17.talk('THORDIS', ['bye'])
_said = [t for _o, t in v17.sim.barks]
check('thordisToldTest save: Atli speaks, Thordis does not',
      any('No antidote there is' in t for t in _said)
      and not any(_l in t for _l in HER_ONLY for t in _said))
v18 = Village()
v18.setflag('haveMark')
v18.talk('THORDIS', [])
v18.talk('ATLI', ['bye'])
_said = [t for _o, t in v18.sim.barks]
check('mirror save: Thordis speaks, Atli does not',
      any('So cruel those Gunnar\'s are' in t for t in _said)
      and not any('No antidote there is' in t for t in _said))
check('...and the shared latch was written exactly once',
      v18.flag('endOfPlantScene') == 1)

# lv-patched/HRODNY.UNK fix 3 (2026-10-07): the menu entry read "Cliffs"
# and its case "cliffs", so picking it matched no case and she said
# nothing (TODO "Found 2026-10-02").
print()
print('  D16: Hrodny answers "Tell me more of the cliffs."')
v19 = Village()
for _f in ('hrodnyMet', 'avatarPoisoned', 'haveMark', 'toldCliffs'):
    v19.setflag(_f)
err, menus = v19.talk('HRODNY', ['Tell me more of the cliffs.', 'bye'])
check('cliffs convo completes', err is None,
      (err or '') + '  ' + menus_str(menus))
check('she answers it',
      any('Dangerous, they are' in t for _o, t in v19.sim.barks),
      str([t for _o, t in v19.sim.barks][-4:]))

# lv-patched/ATLI.UNK change 5 (2026-10-09, Douglas): the first-meeting
# "I have this shield!" is for Pagan's own 828 (quality 0), which Atli takes
# for a look-alike of the Shield-Which-Was-Broken, and not for the restored
# Shield. The option is built in the "Prove it!" case, four picks into his
# first conversation. Since 2026-10-17 the restored Shield is 879
# (TypeSacredShield, quality 83), which the TypeAOArtifact (828) search
# cannot match; the 828-at-quality-83 row keeps the redundant guard honest.
print()
print('D17: Atli\'s "I have this shield!" — Pagan\'s 828, not the restored one')
ATLI_PROVE_IT = ['May I speak with you?', 'I am from Brittania.',
                 'That is not important.', 'I -am- from Brittania!']
AO_ARTIFACT = TYPE_SHAPES['TypeAOArtifact']      # 828
SACRED_SHIELD = TYPE_SHAPES['TypeSacredShield']  # 879
for desc, shape, quality, offered in (
        ("Pagan's own 828 (quality 0)", AO_ARTIFACT, 0, True),
        ('an 828 at quality 83 (the guard)', AO_ARTIFACT, 83, False),
        ('the restored Shield (879, quality 83)', SACRED_SHIELD, 83, False)):
    v20 = Village()
    v20.additem(shape, frame=0, quality=quality)
    err, menus = walk(v20, 'ATLI', ATLI_PROVE_IT + ['bye'],
                      label=f'ATLI prove-it with {desc}')
    last = menus[-1][0] if menus else []
    check(f'{desc}: "I have this shield!" '
          f'{"offered" if offered else "NOT offered"}',
          ('I have this shield!' in last) == offered, f'{last}')
    check(f'{desc}: the walk reached the prove-it menu', bool(menus) and
          'You will have to trust me.' in last, f'{last}')

# 2026-10-09: enterConvo()/exitConvo() spawn retail METHOD 0x57C (0BCF /
# 1090), whose bracket sets and clears somebodyTalking (our codegen used to
# set activity 0 instead, which replaced Aramina's route with a loiter:
# docs/playtest-2026-10-09-final.md finding 3). METHOD 1090 restarts the NPC
# through the Item::enterFastArea intrinsic (the fork's I_enterFastArea
# fires her own handler; this simulator leaves it a stub), so the compiled
# exitConvo spawns nothing after it: the own-handler spawn 7cc1051 added
# was a second activity once the fork fixed the intrinsic.
print()
print('  D18: the conversation bracket is retail METHOD\'s')
v21 = Village()
_talking = []
_set_global = v21.sim.set_global


def _log_talking(off, bits, val):
    if off == FLAG['somebodyTalking']:
        _talking.append(val)
    return _set_global(off, bits, val)


v21.sim.set_global = _log_talking
err, menus = v21.talk('THORDIS', ['How are you called?', 'bye'])
check('conversation completes', err is None, err)
check('somebodyTalking is set by enterConvo and cleared by exitConvo',
      _talking == [1, 0], str(_talking))
_spawned = [(s['class'], s['offset']) for s in v21.sim.spawns]
_efa = struct.unpack_from(
    '<I', v21.sim.flx.get_object(NPC['THORDIS'] + 2), 12 + 15 * 4)[0]
check('METHOD enterConvo, then METHOD exitConvo, and no spawn of her own '
      'enterFastArea',
      [p for p in _spawned if p in ((0x57C, 0x0BCF), (0x57C, 0x1090),
                                    (NPC['THORDIS'], _efa))]
      == [(0x57C, 0x0BCF), (0x57C, 0x1090)], str(_spawned))


# lv-patched/ATLI.UNK change 6 (2026-10-10): after "How do you know it is
# treacherous?" the 1994 menu offered "I am from Brittania!" (original line
# 584) but the only case is "I am from Brittania." (608), so the pick matched
# nothing and re-showed the menu (docs/playtest-2026-10-10-leftovers.md
# finding 2). D19a walks that menu and picks every option on it: a dead one
# shows up as a pick that makes Atli say nothing.
print()
print('  D19a: every option on Atli\'s "Hoskuld spy" menu is answered')
ATLI_SPY = ['May I speak with you?', 'I am not a Pagan.',
            'How do you know it is treacherous?']
v22 = Village()
err, menus = walk(v22, 'ATLI', ATLI_SPY + ['bye'], label='ATLI spy menu')
spy_menu = menus[-1][0] if menus else []
check('the spy menu offers the plain "I am from Brittania."',
      'I am from Brittania.' in spy_menu, str(spy_menu))
_quiet = len(v22.sim.barks)
for _opt in [o for o in spy_menu if o != 'bye']:
    v23 = Village()
    err, menus = walk(v23, 'ATLI', ATLI_SPY + [_opt, 'bye'],
                      label=f'ATLI spy menu -> {_opt!r}')
    check(f'{_opt!r} gets an answer (not a dead option)',
          err is None and len(v23.sim.barks) > _quiet,
          str([t for _o, t in v23.sim.barks][-2:]))
v24 = Village()
err, menus = walk(v24, 'ATLI', ATLI_SPY + ['I am from Brittania.', 'bye'],
                  label='ATLI spy menu -> Brittania')
check('he answers "Know of this Brittania I do not"',
      any('Know of this Brittania I do not' in t for _o, t in v24.sim.barks),
      str([t for _o, t in v24.sim.barks][-2:]))
# The case's own removal is misspelt "Iam from Brittania." (original 615)
# and matches nothing, which is harmless: the next statement assigns the
# whole list, so the answered option is gone all the same.
check('...and the next menu is exactly the three follow-ups',
      bool(menus) and menus[-1][0] == [
          'On the other side of the barrier.', 'In another world.',
          'That is not important.', 'bye'],
      str(menus[-1][0] if menus else None))

# D19b, static and exhaustive: every option a menu offers is answered,
# every removal names an option some add offers, and no case label is
# shadowed. The near-miss form of the first two (a case or punctuation slip)
# is the defect class behind ATLI changes 2, 4, 6 and 7, HRODNY fixes 3 and
# 6, RAGNAR changes 2-7 and 14 and the first 2026-10-10 fixes in INGYALD,
# TYORVI, THORDIS and EZREKAL; until 2026-10-10 the scan flagged only near
# misses, and so missed RAGNAR's `-= "What do you do?"` in case "What do
# you do here?" (docs/playtest-2026-10-10-dialogue.md finding 1), whose
# answered option never left the menu. Now any miss is a finding:
#   remove  a removal no add in the class offers
#   add     an option no case label, `= "..."` compare or final `else`
#           answers
#   shadow  a case label no add offers that is a near-miss of an option
#           another case answers (RAGNAR's stone "No, I don't." went to
#           the Thordis case's "No, I don't."), or a label repeated in one
#           switch
#   sibling a case with several labels that removes one of them but not
#           another some add offers, so picking that one leaves it on the
#           menu (TYORVI's `case "Yes.", "I am going there."` removed
#           "Yes." only, docs/playtest-2026-10-11-fix7.md finding 4; the
#           same slip in ATLI, EZREKAL and RAGNAR). A body that assigns the
#           whole list or ends the conversation is exempt. That finding
#           blamed the removal in case "No reason, really." (TYORVI 1207,
#           `"No reason, really. \f J'y vais."`, `"I am going there."`), but
#           both strings ARE the adds at 1193 once the lexer cuts the
#           French, and D19c's "TYORVI 1207" walk shows that pick clears
#           both: the leftover came from the other option's case, which
#           the `remove` class cannot see because nothing it removes is
#           wrong - one label is just missing.
# Strings are compared as the lexer leaves them (u8c_lexer._read_string:
# cut at the first \f/\g, whitespace collapsed), which is what the case
# compare and slist subtraction see. Only lists some ask(...) shows count.
# Scanned: every source the build compiles (build_eusecode tiers:
# lv-patched/ > LOST VALE/ > UNK files/UNK/ > lv-new/ by basename, minus the
# dev files it does not ship). The pins are the findings deliberately left,
# each with why; a new finding fails the test, and so does fixing a pinned
# one until its pin goes too.
print()
print('  D19b: every menu option answered, every removal offered, no shadow,')
print('        every label of a removing case removed')
import glob  # noqa: E402
import re  # noqa: E402
from u8c_lexer import tokenize, TokenType as TT  # noqa: E402
from build_eusecode import (DEV_ALLOWLIST, DEV_NOT_SHIPPED,  # noqa: E402
                            PROVIDER_CLASS_NAMES, UNSAFE_TO_REPLACE)

_UNREACHED_TOLD_TEST = 'unreached: atliToldTest has no writer'
_INERT_EXIT = 'inert: the case ends the conversation'
# The nine "no reply exists" pins (an option no case in the class answers)
# went on 2026-10-10: each now has a reply written for the restoration
# (lv-patched ATLI 8, EZREKAL M4, RAGNAR 16, TYORVI T4), walked in D19c.
MENU_PINS = {
    # ATLI
    ('ATLI.UNK', 'add', "The Hoskulds don't have the Stone."):
        _UNREACHED_TOLD_TEST,
    ('ATLI.UNK', 'remove', "The Hoskuld's don't have the Stone."):
        'unreached: in the case for the same string, which no add offers',
    ('ATLI.UNK', 'add', 'Where was the body found?'):
        'unreached: same dead case ("The Hoskuld\'s ...")',
    ('ATLI.UNK', 'add', 'When did this happen?'):
        'unreached: same dead case ("The Hoskuld\'s ...")',
    ('ATLI.UNK', 'remove', 'Tell me again of the Rite of Passage.'):
        _UNREACHED_TOLD_TEST,
    ('ATLI.UNK', 'shadow', 'Tell me again of the Rite of Passage.'):
        _UNREACHED_TOLD_TEST + ' (the "Rite Of" add is gated on it)',
    ('ATLI.UNK', 'remove', 'Iam from Brittania.'):
        'inert: the next statement assigns the whole list (D19a)',
    # EZREKAL
    ('EZREKAL.UNK', 'add', 'Prepare my funeral!?'):
        'unreached: case "Thordis sent me to you." is always overwritten '
        '(atliToldTest\'s else)',
    ('EZREKAL.UNK', 'remove', 'I climbed the cliffs.'):
        'inert: the next statement assigns the whole list',
    ('EZREKAL.UNK', 'remove', 'Have you made the tea?'): _INERT_EXIT,
    # FREE: in second(), spawned only by makeAgent(), which nothing calls.
    ('FREE.UNK', 'remove', 'Explain this shifting balace!'):
        'unreached: makeAgent() has no caller',
    # HRODNY / INGJALD: the stone add is inside a 1994 block comment.
    ('HRODNY.UNK', 'remove', 'Do you have the Passage Stone?'):
        'unreached: its only add is commented out',
    ('INGYALD.UNK', 'remove', 'Do you have the Passage Stone?'):
        'unreached: its only add is commented out',
    ('INGYALD.UNK', 'remove', "But I'm not a Pagan!"): _INERT_EXIT,
    ('INGYALD.UNK', 'remove', 'She told me of the poison.'): _INERT_EXIT,
    # RAGNAR
    ('RAGNAR.UNK', 'remove', 'Now do you believe me?'):
        'unreached: in the case for the same string, which no add offers',
    # TYORVI
    ('TYORVI.UNK', 'remove', 'What place is this?'):
        'inert: its only add is commented out; the same removal takes '
        '"I\'d like to speak to you." correctly',
}

def _block_end(toks, i):
    """Index of the RBRACE closing the LBRACE at toks[i]."""
    depth = 0
    for j in range(i, len(toks)):
        if toks[j].type == TT.LBRACE:
            depth += 1
        elif toks[j].type == TT.RBRACE:
            depth -= 1
            if depth == 0:
                return j
    raise ValueError('unbalanced braces')


def _if_chain_has_else(toks, i, var):
    """toks[i] is the first token after `var = ask(...);`. True when the
    next statement is an if-chain on `var` (`if var = "..." {...} else
    if ... else {...}`) that ends in a bare else, which answers whatever
    option the earlier tests did not name."""
    if toks[i].type != TT.IF or toks[i + 1].value != var:
        return False
    while True:
        while toks[i].type != TT.LBRACE:
            i += 1
        i = _block_end(toks, i) + 1
        if toks[i].type != TT.ELSE:
            return False
        if toks[i + 1].type != TT.IF:
            return True
        i += 1


_LIST_OPS = {TT.ASSIGN: 'add', TT.PLUS_ASSIGN: 'add', TT.CARET_ASSIGN: 'add',
             TT.MINUS_ASSIGN: 'remove', TT.PLUS: 'add', TT.MINUS: 'remove'}


def _menu_strings(path):
    """Every menu string op in one source, as the lexer leaves the strings.
    Returns (adds, removes, handled, cases): adds/removes are (string,
    line) for each literal in a `<<...>>` list applied to a list some
    `ask(...)` shows (removes: `-=` or `-`); handled is every string a
    pick can match - case labels, literals after `=`/`!=`, and the
    options a final `else` answers (an ask whose if-chain ends in a bare
    else answers every option added to that list since its previous ask);
    cases is (label, line, switch) per case label, switch numbering the
    enclosing `switch` block."""
    src = open(path, encoding='latin-1').read()
    toks = [t for t in tokenize(src, path) if t.type != TT.NEWLINE]
    asked = {toks[i + 2].value for i, t in enumerate(toks)
             if t.type == TT.ASK and toks[i + 1].type == TT.LPAREN}
    ops, handled, cases = [], set(), []
    switches, pending, depth, nswitch = [], False, 0, 0
    pending_adds = {}          # list var -> adds since its last ask
    i = 0
    while i < len(toks):
        t = toks[i]
        if t.type == TT.SWITCH:
            pending = True
        elif t.type == TT.LBRACE:
            depth += 1
            if pending:
                nswitch += 1
                switches.append((depth, nswitch))
                pending = False
        elif t.type == TT.RBRACE:
            if switches and switches[-1][0] == depth:
                switches.pop()
            depth -= 1
        elif t.type == TT.LSHIFT:
            j = i + 1
            while toks[j].type != TT.RSHIFT:
                j += 1
            k = i - 2
            if toks[i - 1].type == TT.ASSIGN and toks[k].type == TT.LIST:
                while toks[k].type != TT.COLON:      # `v : String List = <<`
                    k -= 1
                k -= 1
            var, kind = toks[k].value, _LIST_OPS.get(toks[i - 1].type)
            if var in asked and kind:
                strs = [(s.value, s.line) for s in toks[i + 1:j]
                        if s.type == TT.STRING_LIT]
                ops.append((kind, strs))
                if kind == 'add':
                    pending_adds.setdefault(var, []).extend(strs)
            i = j
        elif (t.type == TT.ASK and toks[i + 1].type == TT.LPAREN
              and toks[i - 1].type == TT.ASSIGN):
            var = toks[i + 2].value
            j = i
            while toks[j].type != TT.SEMICOLON:
                j += 1
            if _if_chain_has_else(toks, j + 1, toks[i - 2].value):
                handled.update(s for s, _l in pending_adds.get(var, []))
            pending_adds[var] = []
        elif t.type == TT.CASE:
            j = i + 1
            while toks[j].type in (TT.STRING_LIT, TT.COMMA):
                if toks[j].type == TT.STRING_LIT:
                    handled.add(toks[j].value)
                    cases.append((toks[j].value, toks[j].line,
                                  switches[-1][1] if switches else 0))
                j += 1
            i = j
            continue
        elif (t.type == TT.STRING_LIT
              and toks[i - 1].type in (TT.ASSIGN, TT.EQ, TT.NE)):
            handled.add(t.value)
        i += 1
    adds = [x for kind, strs in ops if kind == 'add' for x in strs]
    removes = [x for kind, strs in ops if kind == 'remove' for x in strs]
    return adds, removes, handled, cases


def _squash(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def _near(a, b):
    """Equal once squashed, or (for strings long enough that it means a
    typo) within two edits of each other."""
    a, b = _squash(a), _squash(b)
    if a == b:
        return True
    if min(len(a), len(b)) < 8 or abs(len(a) - len(b)) > 2:
        return False
    prev = list(range(len(b) + 1))
    for x, ca in enumerate(a, 1):
        cur = [x]
        for y, cb in enumerate(b, 1):
            cur.append(min(prev[y] + 1, cur[y - 1] + 1,
                           prev[y - 1] + (ca != cb)))
        prev = cur
    return prev[-1] <= 2


def _multi_label_cases(path):
    """Every case with two or more labels whose body neither assigns a
    whole asked list (`v = <<...>>`) nor ends the conversation (exitConvo,
    return): ([(label, line)], set of strings the body removes)."""
    src = open(path, encoding='latin-1').read()
    toks = [t for t in tokenize(src, path) if t.type != TT.NEWLINE]
    asked = {toks[i + 2].value for i, t in enumerate(toks)
             if t.type == TT.ASK and toks[i + 1].type == TT.LPAREN}
    out = []
    for i, t in enumerate(toks):
        if t.type != TT.CASE:
            continue
        j, labels = i + 1, []
        while toks[j].type in (TT.STRING_LIT, TT.COMMA):
            if toks[j].type == TT.STRING_LIT:
                labels.append((toks[j].value, toks[j].line))
            j += 1
        if len(labels) < 2 or toks[j].type != TT.LBRACE:
            continue
        body = toks[j:_block_end(toks, j) + 1]
        removed, clears = set(), False
        for k, b in enumerate(body):
            if b.type in (TT.EXITCONVO, TT.RETURN):
                clears = True
            elif b.type == TT.LSHIFT and body[k - 2].value in asked:
                if body[k - 1].type == TT.ASSIGN:
                    clears = True
                elif body[k - 1].type in (TT.MINUS_ASSIGN, TT.MINUS):
                    m = k + 1
                    while body[m].type != TT.RSHIFT:
                        m += 1
                    removed.update(s.value for s in body[k + 1:m]
                                   if s.type == TT.STRING_LIT)
        if not clears:
            out.append((labels, removed))
    return out


def _menu_findings(path):
    """{(kind, string): first line} for one source. Kinds: 'remove' (a
    removal no add in the class offers), 'add' (an option nothing
    answers), 'shadow' (a case label no add offers that is a near-miss of
    an option another case already answers - the pick reaches the wrong
    reply - or a label repeated in one switch, whose later case never
    runs), 'sibling' (a label some add offers, left on the menu by its
    own case, which removes another of its labels)."""
    adds, removes, handled, cases = _menu_strings(path)
    added = {s for s, _l in adds}
    found = {}
    for s, line in removes:
        if s not in added:
            found.setdefault(('remove', s), line)
    for s, line in adds:
        if s not in handled:
            found.setdefault(('add', s), line)
    seen = set()
    for s, line, sw in cases:
        if (sw, s) in seen:
            found.setdefault(('shadow', s), line)
        seen.add((sw, s))
        if s and s not in added and any(_near(s, a) for a in added
                                        if a in handled):
            found.setdefault(('shadow', s), line)
    for labels, removed in _multi_label_cases(path):
        if any(s in removed for s, _l in labels):
            for s, line in labels:
                if s in added and s not in removed:
                    found.setdefault(('sibling', s), line)
    return found


_lvu = os.path.join(BASE_DIR, 'shared', 'data', 'lv-usecode')
_dev_skip = (set(DEV_ALLOWLIST) | DEV_NOT_SHIPPED
             | (UNSAFE_TO_REPLACE - set(PROVIDER_CLASS_NAMES)))
_sources = {}
for _tier in (os.path.join(SRC_DIR, 'lv-new', '*.UNK'),
              os.path.join(_lvu, 'UNK files', 'UNK', '*.UNK'),
              os.path.join(_lvu, 'LOST VALE', '*.UNK'),
              os.path.join(SRC_DIR, 'lv-patched', '*.UNK')):
    for _p in glob.glob(_tier):
        _b = os.path.basename(_p).upper()
        if '/UNK files/' in _p and _b[:-4] in _dev_skip:
            continue
        _sources[_b] = _p   # later (higher) tier wins
check('scanned the compiled LV sources, ATLI, RAGNAR and ARAMINA among them',
      {'ATLI.UNK', 'RAGNAR.UNK', 'ARAMINA.UNK'} <= set(_sources)
      and 'lv-patched' in _sources['RAGNAR.UNK'] and len(_sources) > 40,
      str(sorted(_sources)))
_found = {}
for _base, _p in sorted(_sources.items()):
    for (_kind, _s), _line in _menu_findings(_p).items():
        _found[(_base, _kind, _s)] = _line
_new = {k: v for k, v in _found.items() if k not in MENU_PINS}
_stale = set(MENU_PINS) - set(_found)
check('no unpinned menu finding (an option nothing answers, a removal no '
      'add offers, a shadowed case, a sibling label left)', not _new,
      '; '.join(f'{b}:{ln} {k} {s!r}'
                for (b, k, s), ln in sorted(_new.items())))
check('every pinned finding is still present (drop the pin once fixed)',
      not _stale, str(sorted(_stale)))


# D19c: the findings D19b made on branches a player reaches, each fixed at
# the side the author evidently meant, walked here through real menus.
BYE = {'RAGNAR': 'Farewell.'}   # every other NPC's menu ends in "bye"


def _flagged(flags):
    v = Village()
    for _f in flags:
        v.setflag(_f)
    return v


def picked(label, name, flags, path, pick, said, rolls=(), gone=()):
    """Walk `path` then `pick` in one conversation on a Village with `flags`
    set (and `rolls` queued as the urandom results); check the pick was
    answered with `said` and that the answered option, and each option in
    `gone`, is not on the next menu (if the case ends the conversation,
    there is none, and the option goes with it)."""
    v = _flagged(flags)
    v.sim.urandom_script = list(rolls)
    err, menus = walk(v, name, path + [pick, BYE.get(name, 'bye')],
                      label=label)
    check(f'{label}: {pick!r} is answered',
          err is None and any(said in t for _o, t in v.sim.barks),
          str([t[:60] for _o, t in v.sim.barks][-2:]))
    after = menus[len(path) + 1][0] if len(menus) > len(path) + 1 else []
    check(f'{label}: ...and leaves the menu', pick not in after, str(after))
    for opt in gone:
        check(f'{label}: ...and takes {opt!r} with it', opt not in after,
              str(after))


def all_answered(label, name, flags, path, expect):
    """The menu `path` leads to offers `expect`, and each of those options
    makes the NPC say something the plain bye run does not (a dead option
    says nothing new)."""
    v = _flagged(flags)
    err, menus = walk(v, name, path + [BYE.get(name, 'bye')], label=label)
    menu = menus[-1][0] if menus else []
    check(f'{label}: the menu offers {expect}',
          all(o in menu for o in expect), str(menu))
    quiet = {t for _o, t in v.sim.barks}
    for opt in [o for o in menu if o in expect]:
        v = _flagged(flags)
        err, _m = walk(v, name, path + [opt, BYE.get(name, 'bye')],
                       label=f'{label} -> {opt!r}')
        check(f'{label}: {opt!r} gets an answer',
              err is None and any(t not in quiet for _o, t in v.sim.barks),
              str([t[:60] for _o, t in v.sim.barks][-2:]))


print()
print('  D19c: reachable menu findings, fixed')
picked('ATLI 7a', 'ATLI', ('atliMet', 'hrodnyMet'), [],
       'Hrodny sent me to you.', 'a meddling')
ATLI_EZ_THREAD = ['I have spoken with Ezrekal.',
                  'Why does she send them to the cliffs?', 'Her dirty work?',
                  'Do you think this is true?']
picked('ATLI 7b', 'ATLI', ('atliMet', 'avatarPoisoned', 'ezrekalMet'),
       ATLI_EZ_THREAD, 'Who is Hrodny?', 'That strange, twisted individual')
picked('ATLI 7c', 'ATLI',
       ('atliMet', 'avatarPoisoned', 'ezrekalMet', 'hrodnyMet'),
       ATLI_EZ_THREAD + ['Hrodny change her ways?', 'Blasphemous actions?',
                         'Kill her?', 'Who is Ragnar?', 'A Hoskuld?!',
                         'Fresh meat?'],
       'Crazy contraptions?', 'Always working on Ancients-be-damned')
# lv-patched/HRODNY.UNK change 6: the healed Avatar's temple/gods menus.
HEALED = ('hrodnyMet', 'haveMark', 'templeOpen')
all_answered('HRODNY 6, temple open', 'HRODNY', HEALED, [],
             ['I have opened the temple.', 'I have found the Ancient Ones.'])
picked('HRODNY 6', 'HRODNY', HEALED, [], 'I have opened the temple.',
       'So? Wrong, was I.')
all_answered('HRODNY 6, gods free', 'HRODNY', HEALED + ('godsFree',), [],
             ['I have freed the Ancient Ones.'])
# lv-patched/INGYALD.UNK change 1 (class Ingjald).
picked('INGJALD 1a', 'INGJALD',
       ('ingyaldMet', 'avatarPoisoned', 'haveMark', 'toldCliffs'), [],
       'Tell me more of the cliffs.', 'What I know, from Tyorvi, came.')
all_answered('INGJALD 1b, temple open', 'INGJALD',
             ('ingyaldMet', 'haveMark', 'templeOpen'), [],
             ['I have opened the temple.', 'I have found the Ancient Ones.'])
all_answered('INGJALD 1b, gods free', 'INGJALD',
             ('ingyaldMet', 'haveMark', 'templeOpen', 'godsFree'), [],
             ['I have freed the Ancient Ones.'])
picked('INGJALD 1c', 'INGJALD',
       ('ingyaldMet', 'avatarPoisoned', 'haveMark', 'toldOfPoison'),
       ['I have the Mark.'], 'How can I find a cure?',
       'Once, when walked the Vale')
# lv-patched/TYORVI.UNK T3.
all_answered('TYORVI T3a, temple open', 'TYORVI',
             ('tyorviMet', 'haveMark', 'templeOpen'), [],
             ['I have opened the temple.', 'I have found the Ancient Ones.'])
all_answered('TYORVI T3a, gods free', 'TYORVI',
             ('tyorviMet', 'haveMark', 'templeOpen', 'godsFree'), [],
             ['I have freed the Ancient Ones.'])
TYORVI_CLIFFS = (('tyorviMet', 'haveMark', 'avatarPoisoned', 'ezrekalMet',
                  'toldCliffs', 'tyorviPissed'),
                 ['Calm down, Tyorvi.', 'I wish to apologize for my rudeness.',
                  'I have spoken to Ezrekal.', 'She told me of the cliffs.'])
all_answered('TYORVI T3b, attempt the cliffs?', 'TYORVI', *TYORVI_CLIFFS,
             ['Yes.', 'No.'])
picked('TYORVI T3b', 'TYORVI', *TYORVI_CLIFFS, 'No.', 'A wise man you are.')
picked('TYORVI T3c', 'TYORVI', *TYORVI_CLIFFS, 'Yes.',
       'A foolish man you are.')
# lv-patched/TYORVI.UNK T11 (docs/playtest-2026-10-11-fix7.md finding 4,
# plate T2-03): case "Yes.", "I am going there." removed "Yes." only, so
# after "Tell me more of the Cliffs." -> "I am going there." both of that
# menu's options stayed beside "Yes, accompany me.".
TYORVI_TOLD = ('tyorviMet', 'haveMark', 'avatarPoisoned', 'ezrekalMet',
               'toldCliffs', 'sentToTyorvi', 'hasTea', 'givenTea')
picked('TYORVI T11', 'TYORVI', TYORVI_TOLD, ['Tell me more of the Cliffs.'],
       'I am going there.', 'A foolish man you are.',
       gone=('No reason, really.',))
# The removal the finding blamed (TYORVI 1207) already matches: the lexer
# cuts both strings at \f, so this pick clears its menu (D19b's note).
picked('TYORVI 1207', 'TYORVI', TYORVI_TOLD, ['Tell me more of the Cliffs.'],
       'No reason, really.', 'Just curious, are you?',
       gone=('I am going there.',))
# lv-patched/TYORVI.UNK T10 (finding 3, plates T2-01/05/08): "Do you have
# the Key to the Clouds?" is offered until he gives it (givenTea), not after.
for _given in (0, 1):
    v28 = _flagged(('tyorviMet', 'haveMark', 'sentToTyorvi'))
    v28.setflag('givenTea', _given)
    err, menus = walk(v28, 'TYORVI', ['bye'], label=f'TYORVI T10 {_given}')
    _top = menus[0][0] if menus else []
    check(f'TYORVI T10: givenTea={_given}, the Key question is '
          f'{"not " if _given else ""}offered', err is None and
          ('Do you have the Key to the Clouds?' in _top) != bool(_given),
          str(_top))
# lv-patched/TYORVI.UNK T12 (docs/playtest-2026-10-11-fix9.md finding 3,
# plate T1-03): after the accepted apology (T5 clears tyorviPissed) the
# menu kept "Calm down, Tyorvi.", the apology itself and "Shove off, you
# lush!", and "Shove off" angered him again and ended the talk. Both
# replies accept, the sober and the drunk.
for _drunk, _said in ((0, 'a much better attitude'), (1, 'as you should!')):
    v29 = _flagged(('tyorviMet', 'haveMark', 'tyorviPissed'))
    v29.setflag('tyorviDrunk', _drunk)
    err, menus = walk(v29, 'TYORVI',
                      ['Calm down, Tyorvi.',
                       'I wish to apologize for my rudeness.', 'bye'],
                      label=f'TYORVI T12 drunk={_drunk}')
    _after = menus[2][0] if len(menus) > 2 else []
    check(f'TYORVI T12 drunk={_drunk}: the apology is accepted',
          err is None and any(_said in t for _o, t in v29.sim.barks),
          str([t[:60] for _o, t in v29.sim.barks][-2:]))
    for _opt in ('I wish to apologize for my rudeness.',
                 'Calm down, Tyorvi.', 'Shove off, you lush!'):
        check(f'TYORVI T12 drunk={_drunk}: ...and {_opt!r} leaves the menu',
              bool(_after) and _opt not in _after, str(_after))
# The same slip, D19b's sibling class, in three more NPCs.
# lv-patched/RAGNAR.UNK change 17: "I met someone named Thordis." (the
# greeting's add, original line 148) stayed, and a second pick appended
# "Thordis is a good person." again.
picked('RAGNAR 17', 'RAGNAR', ('ragnarMet', 'thordisMet'), [],
       'I met someone named Thordis.', 'Good that is.')
# lv-patched/EZREKAL.UNK M7: "Tell me again of the Shield." (the greeting's
# add once mentionShield is set, original line 346).
picked('EZREKAL M7', 'EZREKAL', ('ezrekalMet', 'mentionShield'), [],
       'Tell me again of the Shield.', 'great powerful artifact')
# lv-patched/ATLI.UNK change 9: "Who might know where to look for it?"
# (original line 2926). Dispatch only: its road starts at "I have come for
# the Passage Stone.", which the greeting's atliToldTest else overwrites,
# and atliToldTest has no writer, so the flag is set by hand here.
picked('ATLI 9', 'ATLI', ('thordisToldTest', 'atliToldTest'),
       ['I have come for the Passage Stone.',
        'The Hoskulds say you have it.'],
       'Who might know where to look for it?', 'Although hate I do')
# lv-patched/THORDIS.UNK change 7.
THORDIS_TEST = (('thordisMet', 'testFromAtli'), ['Tell me of the Test.'])
picked('THORDIS 7', 'THORDIS', *THORDIS_TEST, 'I will take your Test.',
       'Sure of yourself, you are.')
all_answered('THORDIS 7, fear failure?', 'THORDIS', THORDIS_TEST[0],
             THORDIS_TEST[1] + ['I will take your Test.'], ['Yes.', 'No.'])
# lv-patched/EZREKAL.UNK M1.
picked('EZREKAL M1a', 'EZREKAL', (),
       ['May I know your name?', 'I am from Britannia.',
        'No, I am not from outside.', 'Britannia is not in the Vale.',
        'The Titans are not in Britannia.'],
       'The Ancient Ones are in Britannia.', 'Ah, relieves my heart')
picked('EZREKAL M1b', 'EZREKAL', ('ezrekalMet', 'avatarPoisoned'),
       ['Can you help me?', 'I have been poisoned.', "But I'm dying!",
        'Prepare my funeral?!', "I don't want a funeral!",
        'You said the Ancient Ones were gone!', 'Where will I be until then?',
        "I don't want to be an undead!", 'Cloud City?',
        'How?! How can I be healed?'],
       'How can I awaken the Ancients?', 'something I have thought on')
# lv-patched/RAGNAR.UNK change 14.
picked('RAGNAR 14a', 'RAGNAR', (), ['What is your name?',
                                   'From very far away.'],
       "Yes, I'm peaceful.", 'Peacful you are, but peaceful with Gunnar')
RAGNAR_REFERRAL = ['Atli sent me to you.', 'Atli admires you.']
picked('RAGNAR 14b', 'RAGNAR', ('ragnarMet', 'atliMet'), RAGNAR_REFERRAL,
       'I believe that he is sincere.', 'Fine for you that is.')
picked('RAGNAR 14c', 'RAGNAR', ('ragnarMet', 'atliMet'),
       RAGNAR_REFERRAL + ['I believe that he is sincere.',
                          'He said you know many things.',
                          'Do you know of the Passage Stone?', 'Yes, I do.',
                          'Tell me of the legends.', 'How was she killed?'],
       'Her body was eaten?', 'Gone her legs were.')
# lv-patched/EZREKAL.UNK M2: the four in-conversation "Tell me more of the
# Great Cataclysm." adds now reach the story case. R2 (2026-10-10): its
# not-shieldFixed branch rolls urandom(2) + 1 and speaks for 1 and 2, so the
# case's roll is scripted to 0 (after a 0 for the greeting's urandom(6),
# where 1 is the "Get gone" one).
EZ_BALL_OF_FIRE = ['May I know your name?', 'What do you do?',
                   'High Priestess of what?',
                   'What does the High Priestess do?',
                   'When are the special days?', 'Ball of fire in the sky?',
                   'What happened to the ball of fire?']
picked('EZREKAL M2', 'EZREKAL', (), EZ_BALL_OF_FIRE,
       'Tell me more of the Great Cataclysm.',
       'In the early days of our history', rolls=[0, 0])
# R2: every value the case's roll can take tells one of the two stories
# (the 1994 urandom(3) said nothing for 0, one pick in three, before the
# case ended the conversation). As R1 above: one unscripted probe finds
# the case's roll (the conversation's last) and its range, then each run
# scripts that roll alone.
EZ_STORIES = ('In the early days of our history',
              'Shortly after the Shield of the Ancients was lost')
v25 = Village()
walk(v25, 'EZREKAL', EZ_BALL_OF_FIRE + ['Tell me more of the Great '
                                        'Cataclysm.', 'bye'])
_rolls = v25.sim.urandom_rolls
check('R2: the Cataclysm case rolls urandom', len(_rolls) >= 2, str(_rolls))
_k, _n = len(_rolls) - 1, (_rolls[-1][0] if _rolls else 0)
_said = set()
for _v in range(_n):
    v25 = Village()
    v25.sim.urandom_script = [None] * _k + [_v]
    walk(v25, 'EZREKAL', EZ_BALL_OF_FIRE + ['Tell me more of the Great '
                                            'Cataclysm.', 'bye'])
    _lines = [s for _o, t in v25.sim.barks for s in EZ_STORIES if s in t]
    check(f'R2: Cataclysm roll urandom({_n}) = {_v} tells one story',
          len(_lines) == 1 and v25.sim.urandom_rolls[-1:] == [(_n, _v)],
          f'lines={_lines} rolls={v25.sim.urandom_rolls}')
    _said.update(_lines)
check('R2: both stories are reachable', len(_said) == 2, str(sorted(_said)))
# lv-patched/EZREKAL.UNK M4 (2026-10-10, restoration text): "I have not
# heard from the Ancient Ones." has a reply, and takes its exclusive
# sibling off the menu with it.
EZ_OUTSIDE = ['May I know your name?', 'I am from Britannia.',
              'Yes, I am from outside.']
picked('EZREKAL M4', 'EZREKAL', (), EZ_OUTSIDE,
       'I have not heard from the Ancient Ones.',
       'Answered us the Ancients have not',
       gone=('I have heard from the Ancient Ones.',))
# lv-patched/INGYALD.UNK change 2.
all_answered('INGJALD 2, healed', 'INGJALD', ('ingyaldMet', 'haveMark'), [],
             ['I have been healed!', 'The Shield of the Ancients is restored!'])
# 2026-10-10 exhaustive scan. lv-patched/RAGNAR.UNK change 15: the
# first-meeting "What do you do here?" leaves the menu once answered, and
# the stone thread's "No, I don't" reaches its own case, not the Thordis
# rant ("Blind are you?") the period-ending text matched first.
picked('RAGNAR 15a', 'RAGNAR', (), [], 'What do you do here?',
       'Hard to understand you are')
RAGNAR_STONE = RAGNAR_REFERRAL + ['I believe that he is sincere.',
                                  'He said you know many things.',
                                  'Do you know of the Passage Stone?']
picked('RAGNAR 15b', 'RAGNAR', ('ragnarMet', 'atliMet'), RAGNAR_STONE,
       "No, I don't", 'Then why bother me')
v26 = _flagged(('ragnarMet', 'atliMet'))
err, menus = walk(v26, 'RAGNAR', RAGNAR_STONE + ["No, I don't", 'Farewell.'],
                  label='RAGNAR 15b rant')
check('RAGNAR 15b: ...and not the Thordis rant',
      not any('Blind are you' in t for _o, t in v26.sim.barks),
      str([t[:60] for _o, t in v26.sim.barks][-2:]))
picked('RAGNAR 15c', 'RAGNAR', ('ragnarMet', 'atliMet'), RAGNAR_STONE,
       'Yes, I do.', 'Legends say found the body')
# lv-patched/EZREKAL.UNK M3.
picked('EZREKAL M3a', 'EZREKAL', ('ezrekalMet', 'templeOpen'),
       ['I have opened your temple!'], 'I found great treasure!',
       'Great treasure? What sort')
EZ_HEARD = ['May I know your name?', 'I am from Britannia.',
            'Yes, I am from outside.', 'I have heard from the Ancient Ones.']
for _said in ('They did mention you.', 'They did not mention you.'):
    picked(f'EZREKAL M3b ({_said})', 'EZREKAL', (), EZ_HEARD + [_said],
           'Tell me of the Shield.', 'great powerful artifact')
# lv-patched/EZREKAL.UNK M5 (docs/playtest-2026-10-10-full-run-part5.md
# finding 2, plate s10-01): "How?! How can I be healed?" sets the list to
# one holding "Tell me of the Shield.", and "Perhaps I will try the
# Cliffs." four picks later adds it again while toldOfShield is unset. The
# 1994 add was `+=` (append, 0x17), so the menu listed it twice; `^=`
# (union, 0x19 02) keeps one.
EZ_CLIFFS = ['Can you help me?', 'I have been poisoned.', "But I'm dying!",
             'Prepare my funeral?!', "I don't want a funeral!",
             'You said the Ancient Ones were gone!',
             'Where will I be until then?', "I don't want to be an undead!",
             'Cloud City?', 'How?! How can I be healed?',
             'Where is the Cloud City?', 'Tell me more of the Cloud City.',
             'Are the Ancient Ones still there?',
             'Perhaps I will try the Cliffs.']


def listed_once(label, name, flags, path, opt, also=()):
    """The menu `path` leads to offers `opt` exactly once (and each of
    `also`)."""
    v = _flagged(flags)
    err, menus = walk(v, name, path + [BYE.get(name, 'bye')], label=label)
    after = menus[len(path)][0] if len(menus) > len(path) else []
    check(f'{label}: after {path[-1]!r} the menu offers {opt!r} exactly once',
          err is None and after.count(opt) == 1
          and all(o in after for o in also), str(after))


listed_once('EZREKAL M5', 'EZREKAL', ('ezrekalMet', 'avatarPoisoned'),
            EZ_CLIFFS, 'Tell me of the Shield.',
            also=('Where is the Sacred Circle?',))
picked('EZREKAL M5', 'EZREKAL', ('ezrekalMet', 'avatarPoisoned'), EZ_CLIFFS,
       'Tell me of the Shield.', 'great powerful artifact')
# The same 1994 `+=` found by the closing no-duplicate-menu check below.
# lv-patched/EZREKAL.UNK M6: an unmarked first meeting sets yelledAtAvatar,
# and "May I know your name?" added "I am from Britannia." in that branch
# and again after it.
listed_once('EZREKAL M6', 'EZREKAL', (), ['May I know your name?'],
            'I am from Britannia.', also=('What do you do?',))
# lv-patched/TYORVI.UNK T8: the greeting offers the delivery beside "Calm
# down, Tyorvi.", and the accepted apology added it again.
listed_once('TYORVI T8', 'TYORVI',
            ('haveMark', 'tyorviMet', 'hasTea', 'tyorviPissed'),
            ['Calm down, Tyorvi.', 'I wish to apologize for my rudeness.'],
            'I have something for you from Ezrekal.')
# lv-patched/HRODNY.UNK change 7: the second visit, unpoisoned and unmarked.
HRODNY_VALE = ['What place is this?', 'Zealan Vale?']
all_answered('HRODNY 7a', 'HRODNY', ('hrodnyMet',), HRODNY_VALE,
             ['Anything new?', 'Shades?'])
picked('HRODNY 7a', 'HRODNY', ('hrodnyMet',), HRODNY_VALE, 'Shades?',
       'Ghosts... Spirits...')
picked('HRODNY 7a', 'HRODNY', ('hrodnyMet',), HRODNY_VALE, 'Anything new?',
       'People. Ideas.')
picked('HRODNY 7b', 'HRODNY', ('hrodnyMet', 'haveMark'), [],
       'The Shield of the Ancients is restored!', 'See, so I do!')
# Hrodny's chest key comes ONLY from her errand (Douglas 2026-10-11 removed the
# spare key the map used to place in the village; test_chest_locks pins its
# absence). The healed menu offers 'How can I open the temple?'; picking it
# sets spokeTemple and pops a bag holding a q20 key, the chest's lock id.
_vk = _flagged(('hrodnyMet', 'haveMark'))
_err, _menus = walk(_vk, 'HRODNY',
                    ['I have been healed!', 'How can I open the temple?'],
                    must_offer=('How can I open the temple?',),
                    label='HRODNY key errand')
check('HRODNY key errand: spokeTemple set', _vk.flag('spokeTemple') == 1)
_bags = [_vk.world.items[o] for o in _vk.sim.created
         if _vk.world.items[o].shape == TYPE_SHAPES['TypeBag']]
check('HRODNY key errand: the bag pops on the ground at (19588,23284,0)',
      any((b.x, b.y, b.z) == (19588, 23284, 0) and not b.ethereal
          and not b.destroyed for b in _bags),
      str([(b.x, b.y, b.z, b.ethereal) for b in _bags]))
_keys = [_vk.world.items[o] for b in _bags for o in b.contents
         if _vk.world.items[o].shape == TYPE_SHAPES['TypeKey']]
check('HRODNY key errand: the bag holds one key of quality 20',
      [k.quality for k in _keys] == [20], str([k.quality for k in _keys]))
# lv-patched/THORDIS.UNK change 8.
for _opt in ('The plant exploded!', 'What is happening to me?'):
    picked('THORDIS 8', 'THORDIS',
           ('thordisMet', 'avatarPoisoned', 'thordisToldTest'), [], _opt,
           'Here, the Mark, is.')
# 2026-10-10 replies written for the restoration (Douglas's decision): the
# nine options D19b pinned as having no reply now answer, each with the
# menu change its neighbours make.
# lv-patched/ATLI.UNK change 8.
picked('ATLI 8', 'ATLI',
       ('atliMet', 'avatarPoisoned', 'ezrekalMet'),
       ['I have spoken with Ezrekal.', 'Why does she send them to the cliffs?',
        'Her dirty work?'],
       'Former beauty?', 'Green and good this Vale once was')
# lv-patched/TYORVI.UNK T4.
picked('TYORVI T4a', 'TYORVI', TYORVI_CLIFFS[0] + ('climbedCliffs',),
       TYORVI_CLIFFS[1], 'I already have.',
       'Already climbed them you have?')
picked('TYORVI T4b', 'TYORVI',
       ('tyorviMet', 'haveMark', 'avatarPoisoned', 'ezrekalMet'),
       ['I have spoken to Ezrekal.'], 'She had little to say.',
       'Little to say, had she?')
picked('TYORVI T4c', 'TYORVI',
       ('tyorviMet', 'haveMark', 'tyorviDrunk', 'attemptedCliffs',
        'climbedCliffs'), [], "You weren't at the cliffs.",
       'Gathering my climbing gear I was')
picked('TYORVI T4d', 'TYORVI',
       ('tyorviMet', 'haveMark', 'tyorviDrunk', 'attemptedCliffs'), [],
       'Are you going to the cliffs?', 'Gathering my climbing gear still I am')
# lv-patched/RAGNAR.UNK change 16.
picked('RAGNAR 16a', 'RAGNAR', (),
       ['What is your name?', 'From very far away.', "Yes, I'm peaceful.",
        'I am peaceful with all.', 'You have a point.',
        'You are a cautious fellow.', 'What have they done?'],
       'Who is Thordis?', 'Know Thordis you do not?')
RAGNAR_HRODNY = RAGNAR_REFERRAL + ['I believe that he is sincere.',
                                   'He spoke of you and Hrodny.']
picked('RAGNAR 16b', 'RAGNAR', ('ragnarMet', 'atliMet'), RAGNAR_HRODNY,
       'Do you like her?', 'Like her? Beautiful she is')
picked('RAGNAR 16c', 'RAGNAR', ('ragnarMet', 'atliMet'),
       RAGNAR_HRODNY + ['He said you could help me.',
                        'Do you know of the Passage Stone?', 'Yes, I do.',
                        'Why do you not go there?',
                        'He said you could help me.'],
       'None, thank you.', 'Then go and find the stone')
# lv-patched/TYORVI.UNK T5 (docs/playtest-2026-10-10-menus.md finding 1): an
# accepted apology clears tyorviPissed, so the next talk's top menu is his
# ordinary one again, with the healed/temple options its flags call for,
# and not the one-option "Calm down, Tyorvi." list.
print()
print('  T5: Tyorvi forgives an apology for good')
for _flags, _expect in (
        (('haveMark',), ['I have been healed!']),
        (('haveMark', 'templeOpen'),
         ['I have opened the temple.', 'I have found the Ancient Ones.'])):
    v26 = _flagged(('tyorviMet', 'tyorviPissed') + _flags)
    err, menus = walk(v26, 'TYORVI', ['Calm down, Tyorvi.',
                                      'I wish to apologize for my rudeness.',
                                      'bye'], label='TYORVI T5 apology')
    check(f'T5 {_flags}: the apology clears tyorviPissed',
          err is None and v26.flag('tyorviPissed') == 0,
          f'err={err} tyorviPissed={v26.flag("tyorviPissed")}')
    err, menus = walk(v26, 'TYORVI', ['bye'], label='TYORVI T5 next talk')
    _top = menus[0][0] if menus else []
    check(f'T5 {_flags}: the next talk offers {_expect}, not "Calm down"',
          err is None and all(o in _top for o in _expect)
          and 'Calm down, Tyorvi.' not in _top, str(_top))
# lv-patched/TYORVI.UNK T6 (docs/playtest-2026-10-10-replies.md finding 1):
# after the Key, "Tell me more of the Cliffs." -> "I am going there." ->
# "Yes, accompany me." sets tyorviDrunk again (1994, kept: it is the road to
# "You weren't at the cliffs."), and the drink, its only other clearer, is
# spent. With attemptedCliffs and climbedCliffs set the greeting's
# `if tyorviDrunk and attemptedCliffs` branch replaced every later menu.
# Here the climb is the real EggCloudCliffs hatch with Tyorvi's key in the
# pack. The first talk after it offers "You weren't at the cliffs."; that
# answer sobers him, so every talk after it is his ordinary menu, and the
# healed, temple and gods options come back as their flags are set.
print()
print('  T6: the drunk greeting after the Key is one talk, not a trap')
CLIFF_EGG = json.load(open(MANIFEST))['classes']['EGGCLOUDCLIFFS']
AFTER_KEY = ('tyorviMet', 'haveMark', 'avatarPoisoned', 'ezrekalMet',
             'toldCliffs', 'sentToTyorvi', 'hasTea', 'givenTea')
for _tried in (0, 1):
    _l = f'T6 attemptedCliffs={_tried}'
    v27 = _flagged(AFTER_KEY)
    v27.setflag('attemptedCliffs', _tried)
    v27.additem(TYPE_SHAPES['TypeCliffKey'], quality=170)
    err, menus = walk(v27, 'TYORVI', ['Tell me more of the Cliffs.',
                                      'I am going there.',
                                      'Yes, accompany me.'],
                      label=f'TYORVI {_l} accompany')
    check(f'{_l}: "Yes, accompany me." re-arms tyorviDrunk (1994)',
          err is None and v27.flag('tyorviDrunk') == 1)
    if _tried:
        # The keyless attempt came first: until he climbs, the greeting is
        # "Are you going to the cliffs?" (T4d). He holds the key, so the
        # climb is open and ends this state; the Key question went with
        # the Key (T10).
        err, menus = walk(v27, 'TYORVI', ['Are you going to the cliffs?',
                                          'bye'], label=f'TYORVI {_l} T4d')
        _top = menus[0][0] if menus else []
        check(f'{_l}: before the climb the greeting is T4d, the Key '
              'question gone', err is None
              and 'Are you going to the cliffs?' in _top
              and 'Do you have the Key to the Clouds?' not in _top, str(_top))
    _egg = v27.world.add(73, quality=297, x=19200, y=6400, z=0, npcnum=0x88)
    try:
        v27.sim.run_event(CLIFF_EGG, 0, _egg.objid, event=7)
    except SimError as e:
        check(f'{_l}: the cliff egg runs', False, str(e))
    check(f'{_l}: his key climbs the cliffs',
          v27.flag('climbedCliffs') == 1 and v27.flag('attemptedCliffs') == 1)
    err, menus = walk(v27, 'TYORVI', ["You weren't at the cliffs.", 'bye'],
                      label=f'TYORVI {_l} T4c')
    check(f'{_l}: "You weren\'t at the cliffs." is answered and sobers him',
          err is None and v27.flag('tyorviDrunk') == 0,
          f'err={err} tyorviDrunk={v27.flag("tyorviDrunk")}')
    for _set, _expect in (
            ((), ['Tell me more of the Cliffs.']),
            (('-avatarPoisoned',), ['I have been healed!',
                                    'The Shield of the Ancients is repaired!']),
            (('templeOpen',), ['I have opened the temple.',
                               'I have found the Ancient Ones.']),
            (('godsFree',), ['I have freed the Ancient Ones.'])):
        for _f in _set:
            v27.setflag(_f.lstrip('-'), 0 if _f.startswith('-') else 1)
        err, menus = walk(v27, 'TYORVI', ['bye'], label=f'TYORVI {_l} next')
        _top = menus[0][0] if menus else []
        check(f'{_l}, then {_set or "nothing"}: the next talk offers '
              f'{_expect}, not the drunk greeting',
              err is None and all(o in _top for o in _expect)
              and "You weren't at the cliffs." not in _top, str(_top))
print()
print('  Every menu offered in this file lists each option once')
check(f'no menu shows an option twice ({len(DUP_MENUS)} offending menus)',
      not DUP_MENUS,
      str([(n, sorted({o for o in m if m.count(o) > 1}))
           for n, m in DUP_MENUS][:6]))
print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: '
      f'{passed} passed, {failed} failed')
sys.exit(1 if failed else 0)
