/* Optional integration test: run against a DISPOSABLE editor world on 1.21.4.
 * Requires mineflayer and rcon-client in BBE_NODE_MODULES; see ../README.md.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { once } = require('node:events');
const { createRequire } = require('node:module');
if (process.env.BBE_RUNTIME_TEST !== '1') throw Error('Set BBE_RUNTIME_TEST=1; use a disposable editor world.');
const dependency = process.env.BBE_NODE_MODULES
  ? createRequire(path.resolve(process.env.BBE_NODE_MODULES, '../package.json')) : require;
const mineflayer = dependency('mineflayer');
const { Rcon } = dependency('rcon-client');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const checks = [];
let bot, rcon, restored = false;
const name = 'ArenaEditTester';
async function cmd(command) { return rcon.send(command); }
async function score(holder, objective = 'bbe.tmp') {
  const value = await cmd(`scoreboard players get ${holder} ${objective}`);
  const match = value.match(/has (-?\d+)/);
  assert.ok(match, value);
  return Number(match[1]);
}
async function number(nbtPath) {
  const value = await cmd('data get storage bbe:session ' + nbtPath);
  const match = value.match(/contents: (-?[\d.]+)(?:[dfb])?$/);
  assert.ok(match, value);
  return Number(match[1]);
}
async function playerPos() {
  const value = await cmd(`data get entity ${name} Pos`);
  return value.slice(value.indexOf('[') + 1, value.indexOf(']')).split(',').map(parseFloat);
}
async function trigger(action) {
  bot.chat(`/trigger bbe.ui set ${action}`);
  await delay(350);
}
async function count(selector) {
  await cmd(`execute store result score $count bbe.tmp if entity ${selector}`);
  return score('$count');
}
async function restore() {
  if (restored || !rcon) return;
  await cmd(`scoreboard players set ${name} bbe.test 0`);
  await cmd('data modify storage bbe:session state set from storage bbe:session test_original');
  await cmd('data remove storage bbe:session test_original');
  await cmd('function bbe:rebuild');
  restored = true;
}
(async () => {
  rcon = await Rcon.connect({host: '127.0.0.1', port: Number(process.env.BBE_RCON_PORT || 25692),
                            password: process.env.BBE_RCON_PASSWORD || 'arena-editor-local-test'});
  assert.equal(await number('state.schema'), 1);
  await cmd('data modify storage bbe:session test_original set from storage bbe:session state');
  bot = mineflayer.createBot({host: '127.0.0.1', port: Number(process.env.BBE_SERVER_PORT || 25691),
                             username: name, auth: 'offline', version: '1.21.4'});
  bot.on('error', error => console.error(error));
  await once(bot, 'spawn', {signal: AbortSignal.timeout(20000)});
  bot.physicsEnabled = false;
  await delay(1600);
  await cmd(`execute as ${name} at @s run function bbe:join`);
  await delay(1200);
  assert.ok(bot.inventory.items().some(item => item.name === 'written_book'), 'Editor book was not granted');
  checks.push('Join grants the clickable editor book');
  const origin = await playerPos();
  assert.ok(await count('@e[tag=bbe.hit]') > 0, 'No spawn hitboxes rendered');
  assert.ok((await cmd('data get entity @e[type=text_display,tag=bbe.overlay,limit=1] text')).includes('#'));
  checks.push('Nearby points render as labeled interaction entities');
  const id = await number('state.next_id');
  await trigger(11);
  const object = `state.objects[{id:${id}}]`;
  assert.ok((await cmd(`data get storage bbe:session ${object}.kind`)).includes('ammo'));
  await cmd(`tp ${name} ${origin[0] + 2.25} ${origin[1]} ${origin[2] + 2.25}`);
  await trigger(6);
  assert.equal(await number(object + '.x'), origin[0] + 2.25);
  await trigger(8);
  assert.equal(await number(object + '.x'), origin[0]);
  await trigger(9);
  assert.equal(await number(object + '.x'), origin[0] + 2.25);
  await trigger(32);
  assert.equal(await number(object + '.x'), origin[0] + 1.75);
  await cmd(`execute as ${name} at @s run function bbe:set_point {id:${id},x:${origin[0]},y:${origin[1]},z:${origin[2]},yaw:131.25,pitch:-10}`);
  assert.equal(await number(object + '.yaw'), 131.25);
  checks.push('Add/move ammo point, undo, redo, negative nudge and exact coordinates');
  await cmd(`tp ${name} ${origin[0]} ${origin[1]} ${origin[2] + 2}`);
  await cmd(`scoreboard players set ${name} bbe.sel 0`);
  await delay(600);
  let hit;
  for (let retry = 0; retry < 30; retry++) {
    hit = Object.values(bot.entities).find(e => e.name === 'interaction' &&
      Math.abs(e.position.x - origin[0]) < .05 && Math.abs(e.position.z - origin[2]) < .05);
    if (hit) break;
    await delay(100);
  }
  assert.ok(hit, 'No interaction entity at test point');
  await bot.lookAt(hit.position.offset(0, .5, 0), true);
  bot.activateEntity(hit);
  await delay(500);
  assert.ok(await score(name, 'bbe.sel') > 0, 'Real right-click did not select a point');
  checks.push('Actual client right-click selects a spawn');
  await cmd(`tp ${name} ${origin[0] - 2} ${origin[1] - 1} ${origin[2] - 2}`);
  await trigger(21);
  await cmd(`tp ${name} ${origin[0] + 2} ${origin[1] + 4} ${origin[2] + 2}`);
  await trigger(22);
  const boxId = await number('state.next_id');
  await trigger(23);
  const box = `state.objects[{id:${boxId}}]`;
  assert.equal(await number(box + '.x1'), origin[0] - 2);
  assert.equal(await number(box + '.x2'), origin[0] + 2);
  assert.equal(await count('@e[tag=bbe.wire]'), 12);
  await trigger(25);
  assert.ok((await cmd('data get storage bbe:session ' + box + '.mode')).includes('keep_out'));
  await trigger(26);
  assert.ok((await cmd('data get storage bbe:session ' + box + '.action')).includes('kill'));
  await trigger(27);
  assert.equal(await number(box + '.enabled'), 0);
  await trigger(27);
  assert.equal(await number(box + '.enabled'), 1);
  checks.push('Corner tools create a 12-edge wireframe; box rule/action/enabled controls work');
  // Isolate this test's boundaries; the original state is restored in finally.
  await cmd('data modify storage bbe:session test_box set from storage bbe:session ' + box);
  await cmd('data remove storage bbe:session state.objects[{kind:"area"}]');
  await cmd('data modify storage bbe:session state.objects append from storage bbe:session test_box');
  await cmd(`data modify storage bbe:session ${box}.mode set value "keep_in"`);
  await cmd('data modify storage bbe:session state.outside_action set value "tp"');
  await cmd('data modify storage bbe:session state.boundary_enabled set value 1b');
  await cmd(`tp ${name} ${origin.join(' ')}`);
  await trigger(18);
  await cmd(`tp ${name} ${origin[0] + 30} ${origin[1]} ${origin[2]}`);
  await delay(800);
  let position = await playerPos();
  assert.ok(Math.abs(position[0] - origin[0]) < .1, 'Leaving keep-in boxes did not return the player');
  await cmd(`execute in minecraft:the_nether run tp ${name} ${origin.join(' ')}`);
  await delay(1000);
  assert.ok((await cmd(`data get entity ${name} Dimension`)).includes('overworld'));
  checks.push('Boundary test teleports an escaped or wrong-dimension editor back');
  await cmd(`data modify storage bbe:session ${box}.mode set value "keep_out"`);
  await cmd(`data modify storage bbe:session ${box}.action set value "kill"`);
  let deaths = 0;
  bot.on('death', () => deaths++);
  await cmd(`tp ${name} ${origin.join(' ')}`);
  await delay(1200);
  assert.ok(deaths > 0, 'Keep-out kill did not kill the client');
  assert.equal(await score(name, 'bbe.test'), 0, 'Kill test did not stop automatically');
  checks.push('Keep-out kill works and exits test mode on death');
  await restore();
  await cmd('save-all flush');
  const report = {minecraft: '1.21.4', checks, passed: checks.length};
  const output = process.env.BBE_TEST_REPORT || 'dev/arena-editor/runtime-results.json';
  fs.mkdirSync(path.dirname(output), {recursive: true});
  fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => {
  try { await restore(); } finally {
    if (bot) bot.quit();
    if (rcon) await rcon.end();
  }
});
