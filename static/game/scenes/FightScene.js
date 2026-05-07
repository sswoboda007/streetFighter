// FightScene: the real fight. 1P vs AI. Round timer, HP bars, K.O.
// Press R to rematch, ESC to return to select.
//
// Controls: A/D move, W jump, S block, J light punch, K heavy punch.

import { Fighter, hitboxOverlapsFighter } from '../entities/Fighter.js';
import { AIController } from '../entities/AIController.js';

const GROUND_Y_RATIO = 0.82;
const ROUND_SECONDS = 60;

export class FightScene extends Phaser.Scene {
    constructor() {
        super('FightScene');
    }

    create(data) {
        const w = this.scale.width;
        const h = this.scale.height;

        this.drawStage();

        // world bounds so fighters can't walk off-screen
        this.physics.world.setBounds(20, 0, w - 40, h * GROUND_Y_RATIO);

        // floor as static body
        const floor = this.add.rectangle(w / 2, h * GROUND_Y_RATIO + 4, w, 8, 0x000000, 0);
        this.physics.add.existing(floor, true);
        this.floor = floor;

        const groundY = h * GROUND_Y_RATIO;
        this.player = new Fighter(this, w * 0.3, groundY - 50, data.player, 1);
        this.enemy = new Fighter(this, w * 0.7, groundY - 50, data.opponent, -1);
        this.ai = new AIController(this.enemy);

        this.physics.add.collider(this.player.body, floor);
        this.physics.add.collider(this.enemy.body, floor);

        // HUD
        this.buildHUD(data.player.name, data.opponent.name);

        // Debug hitbox graphics (toggle with H)
        this.hitGfx = this.add.graphics();
        this.showHitboxes = false;

        this.timeLeft = ROUND_SECONDS * 1000;
        this.over = false;
        this.message = null;

        // Input
        this.keys = this.input.keyboard.addKeys({
            left: 'A', right: 'D', up: 'W', down: 'S',
            light: 'J', heavy: 'K',
            rematch: 'R', back: 'ESC', debug: 'H',
        });

        // Intro banner
        this.introBanner('FIGHT!');
    }

    update(_, delta) {
        if (this.over) {
            this.handleOverInput();
            this.player.update(delta, this.enemy);
            this.enemy.update(delta, this.player);
            return;
        }

        this.timeLeft = Math.max(0, this.timeLeft - delta);
        this.timerText.setText(String(Math.ceil(this.timeLeft / 1000)).padStart(2, '0'));

        // Player input
        const k = this.keys;
        const p = this.player;
        if (p.canAct()) {
            if (k.left.isDown) p.moveLeft();
            else if (k.right.isDown) p.moveRight();
            else p.stopMoving();

            if (Phaser.Input.Keyboard.JustDown(k.up)) p.jump();
            if (Phaser.Input.Keyboard.JustDown(k.light)) p.attackLight();
            if (Phaser.Input.Keyboard.JustDown(k.heavy)) p.attackHeavy();

            if (k.down.isDown) p.startBlock();
            else if (p.state === 'block') p.stopBlock();
        }

        // Auto-facing (not during attacks)
        this.player.faceOpponent(this.enemy);
        this.enemy.faceOpponent(this.player);

        // AI
        this.ai.update(delta, this.player);

        // Physics/anim update
        this.player.update(delta, this.enemy);
        this.enemy.update(delta, this.player);

        // Hit resolution
        this.resolveHits(this.player, this.enemy);
        this.resolveHits(this.enemy, this.player);

        // HUD bars
        this.drawHpBar(this.playerBarG, 20, 30, 380, 24, this.player.hp / this.player.maxHp, 0x3a9bff);
        this.drawHpBar(this.enemyBarG, this.scale.width - 400, 30, 380, 24, this.enemy.hp / this.enemy.maxHp, 0xff4040, true);

        // Debug
        if (Phaser.Input.Keyboard.JustDown(k.debug)) this.showHitboxes = !this.showHitboxes;
        this.drawDebugHitboxes();

        // End conditions
        if (this.player.isKO || this.enemy.isKO) {
            this.endRound(this.enemy.isKO ? 'YOU WIN!' : 'YOU LOSE');
        } else if (this.timeLeft <= 0) {
            const winner = this.player.hp === this.enemy.hp
                ? "TIME UP - DRAW"
                : (this.player.hp > this.enemy.hp ? 'TIME UP - YOU WIN!' : 'TIME UP - YOU LOSE');
            this.endRound(winner);
        }

        if (Phaser.Input.Keyboard.JustDown(this.keys.back)) this.scene.start('SelectScene');
    }

    resolveHits(attacker, defender) {
        const hb = attacker.getAttackHitbox();
        if (!hb) return;
        if (hitboxOverlapsFighter(hb, defender)) {
            const dealt = defender.takeHit(hb.dmg, attacker.x);
            attacker.hasHitThisSwing = true;
            this.spawnImpact(hb.cx, hb.cy, dealt > hb.dmg * 0.5);
            this.cameras.main.shake(80, 0.004);
        }
    }

    spawnImpact(x, y, strong) {
        const r = this.add.circle(x, y, strong ? 14 : 10, 0xf0c674, 0.9);
        this.tweens.add({
            targets: r, scale: strong ? 2.4 : 1.8, alpha: 0,
            duration: 180, onComplete: () => r.destroy(),
        });
    }

    endRound(text) {
        if (this.over) return;
        this.over = true;
        this.player.stopMoving();
        this.enemy.stopMoving();
        const w = this.scale.width;
        const h = this.scale.height;
        this.message = this.add.text(w / 2, h / 2, text, {
            fontFamily: 'Courier New', fontSize: '52px', color: '#f0c674',
            stroke: '#000', strokeThickness: 6,
        }).setOrigin(0.5).setScale(0);
        this.tweens.add({ targets: this.message, scale: 1, duration: 350, ease: 'Back.Out' });
        this.hint = this.add.text(w / 2, h / 2 + 60, 'R: rematch   ESC: select', {
            fontFamily: 'Courier New', fontSize: '16px', color: '#fff',
        }).setOrigin(0.5);
    }

    handleOverInput() {
        if (Phaser.Input.Keyboard.JustDown(this.keys.rematch)) {
            this.scene.restart({ player: this.player.character, opponent: this.enemy.character });
        } else if (Phaser.Input.Keyboard.JustDown(this.keys.back)) {
            this.scene.start('SelectScene');
        }
    }

    introBanner(text) {
        const w = this.scale.width;
        const h = this.scale.height;
        const t = this.add.text(w / 2, h / 2, text, {
            fontFamily: 'Courier New', fontSize: '72px', color: '#f0c674',
            stroke: '#000', strokeThickness: 8,
        }).setOrigin(0.5).setScale(0);
        this.tweens.add({
            targets: t, scale: 1.2, duration: 400, ease: 'Back.Out',
            yoyo: true, hold: 350,
            onComplete: () => t.destroy(),
        });
    }

    buildHUD(playerName, enemyName) {
        const w = this.scale.width;
        this.add.text(20, 6, playerName, { fontFamily: 'Courier New', fontSize: '16px', color: '#6cf' });
        this.add.text(w - 20, 6, enemyName, { fontFamily: 'Courier New', fontSize: '16px', color: '#f66' }).setOrigin(1, 0);
        this.playerBarG = this.add.graphics();
        this.enemyBarG = this.add.graphics();
        this.timerText = this.add.text(w / 2, 32, '60', {
            fontFamily: 'Courier New', fontSize: '28px', color: '#f0c674',
        }).setOrigin(0.5);
    }

    drawHpBar(g, x, y, w, h, pct, color, rightToLeft = false) {
        g.clear();
        g.fillStyle(0x000000, 0.7); g.fillRect(x - 2, y - 2, w + 4, h + 4);
        g.fillStyle(0x222222, 1); g.fillRect(x, y, w, h);
        const fillW = Math.max(0, Math.floor(w * pct));
        g.fillStyle(color, 1);
        if (rightToLeft) g.fillRect(x + w - fillW, y, fillW, h);
        else g.fillRect(x, y, fillW, h);
        g.lineStyle(2, 0xf0c674, 1); g.strokeRect(x, y, w, h);
    }

    drawDebugHitboxes() {
        this.hitGfx.clear();
        if (!this.showHitboxes) return;
        for (const f of [this.player, this.enemy]) {
            this.hitGfx.lineStyle(1, 0x00ff00, 1);
            this.hitGfx.strokeRect(f.x - 20, f.y - 45, 40, 90);
            const hb = f.getAttackHitbox();
            if (hb) {
                this.hitGfx.lineStyle(1, 0xff0000, 1);
                this.hitGfx.strokeRect(hb.cx - hb.w / 2, hb.cy - hb.h / 2, hb.w, hb.h);
            }
        }
    }

    drawStage() {
        const w = this.scale.width;
        const h = this.scale.height;
        const g = this.add.graphics();
        // sky bands
        const bands = [0x1a0a1a, 0x2a1030, 0x4a1a40, 0x6a2040];
        const bandH = (h * GROUND_Y_RATIO) / bands.length;
        bands.forEach((col, i) => { g.fillStyle(col, 1); g.fillRect(0, i * bandH, w, bandH); });
        // sun
        g.fillStyle(0xf0c674, 0.5); g.fillCircle(w * 0.78, h * 0.28, 55);
        // silhouette skyline
        g.fillStyle(0x0a0a18, 1);
        g.beginPath();
        g.moveTo(0, h * GROUND_Y_RATIO);
        for (let i = 0; i <= 14; i++) {
            const x = (i * w) / 14;
            const y = h * GROUND_Y_RATIO - 40 - (i % 3 === 0 ? 80 : (i % 2 === 0 ? 40 : 20));
            g.lineTo(x, y);
        }
        g.lineTo(w, h * GROUND_Y_RATIO);
        g.closePath();
        g.fillPath();
        // ground
        g.fillStyle(0x3a2018, 1); g.fillRect(0, h * GROUND_Y_RATIO, w, h - h * GROUND_Y_RATIO);
        g.fillStyle(0x5a3028, 1);
        for (let x = 0; x < w; x += 40) g.fillRect(x, h * GROUND_Y_RATIO, 20, 4);
    }
}

