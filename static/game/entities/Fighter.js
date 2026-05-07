// Fighter: a playable/AI-controllable character. Owns an invisible
// physics Rectangle body and a visual container of colored rectangles
// (from fighterArt.createFighter). Drives a small state machine:
//   idle | walk | jump | attack_light | attack_heavy | block | hit | ko
//
// Stats come from the Character API payload's game_stats field.

import { createFighter } from './fighterArt.js';

const STATE = Object.freeze({
    IDLE: 'idle',
    WALK: 'walk',
    JUMP: 'jump',
    ATTACK_LIGHT: 'attack_light',
    ATTACK_HEAVY: 'attack_heavy',
    BLOCK: 'block',
    HIT: 'hit',
    KO: 'ko',
});

const ATTACK_LIGHT_MS = 260;
const ATTACK_HEAVY_MS = 420;
const HIT_STUN_MS = 260;
const BODY_W = 40;
const BODY_H = 90;

export class Fighter {
    constructor(scene, x, y, character, facing) {
        this.scene = scene;
        this.character = character;
        this.stats = character.game_stats;
        this.maxHp = this.stats.max_hp;
        this.hp = this.maxHp;
        this.facing = facing; // 1 = faces right, -1 = faces left

        // Invisible physics body — the authoritative position/velocity
        this.body = scene.add.rectangle(x, y, BODY_W, BODY_H, 0x000000, 0);
        scene.physics.add.existing(this.body);
        this.body.body.setCollideWorldBounds(true);
        this.body.body.setDragX(900);
        this.body.body.setMaxVelocity(400, 900);

        // Visual container — feet at container origin
        this.view = createFighter(scene, x, y + BODY_H / 2, character.palette);
        this.view.setScale(2 * facing, 2);

        this.state = STATE.IDLE;
        this.stateTimer = 0;
        this.animTime = 0;
        this.hasHitThisSwing = false;
        this.blockHeld = false;
    }

    destroy() {
        this.body.destroy();
        this.view.destroy();
    }

    get x() { return this.body.x; }
    get y() { return this.body.y; }
    get isKO() { return this.state === STATE.KO; }

    onGround() {
        return this.body.body.blocked.down || this.body.body.touching.down;
    }

    canAct() {
        return ![STATE.ATTACK_LIGHT, STATE.ATTACK_HEAVY, STATE.HIT, STATE.KO].includes(this.state);
    }

    setState(name, duration = 0) {
        if (this.state === name) return;
        this.state = name;
        this.stateTimer = duration;
        this.hasHitThisSwing = false;
        // reset limb positions
        const p = this.view.parts;
        p.armL.setPosition(-14, -50);
        p.armR.setPosition(14, -50);
        p.legL.setPosition(-6, -10);
        p.legR.setPosition(6, -10);
        p.head.setPosition(0, -56);
        this.view.rotation = 0;
    }

    // ---- input-driven actions ----
    moveLeft() {
        if (!this.canAct()) return;
        this.body.body.setVelocityX(-this.stats.move_speed);
        if (this.onGround() && this.state !== STATE.BLOCK) this.setState(STATE.WALK);
    }

    moveRight() {
        if (!this.canAct()) return;
        this.body.body.setVelocityX(this.stats.move_speed);
        if (this.onGround() && this.state !== STATE.BLOCK) this.setState(STATE.WALK);
    }

    stopMoving() {
        if (!this.canAct()) return;
        if (this.state === STATE.WALK) this.setState(STATE.IDLE);
    }

    jump() {
        if (!this.canAct() || !this.onGround()) return;
        this.body.body.setVelocityY(-700);
        this.setState(STATE.JUMP);
    }

    startBlock() {
        if (!this.canAct() || !this.onGround()) return;
        this.blockHeld = true;
        this.body.body.setVelocityX(0);
        this.setState(STATE.BLOCK);
    }

    stopBlock() {
        this.blockHeld = false;
        if (this.state === STATE.BLOCK) this.setState(STATE.IDLE);
    }

    attackLight() {
        if (!this.canAct() || !this.onGround()) return;
        this.body.body.setVelocityX(0);
        this.setState(STATE.ATTACK_LIGHT, ATTACK_LIGHT_MS);
    }

    attackHeavy() {
        if (!this.canAct() || !this.onGround()) return;
        this.body.body.setVelocityX(0);
        this.setState(STATE.ATTACK_HEAVY, ATTACK_HEAVY_MS);
    }

    takeHit(damage, fromX) {
        if (this.state === STATE.KO) return 0;
        const blocked = this.state === STATE.BLOCK && this.blockHeld;
        const dealt = blocked ? Math.max(1, Math.floor(damage * 0.15)) : damage;
        this.hp = Math.max(0, this.hp - dealt);
        const dir = this.x < fromX ? -1 : 1;
        const kb = blocked ? 120 : 260;
        this.body.body.setVelocity(dir * kb, -180);
        if (this.hp <= 0) {
            this.setState(STATE.KO, 1e9);
        } else if (!blocked) {
            this.setState(STATE.HIT, HIT_STUN_MS);
        }
        return dealt;
    }

    // Returns active attack hitbox or null. Only active during the
    // middle frames of a swing; returns at most once per swing.
    getAttackHitbox() {
        if (this.hasHitThisSwing) return null;
        if (this.state === STATE.ATTACK_LIGHT) {
            const progress = 1 - this.stateTimer / ATTACK_LIGHT_MS;
            if (progress > 0.25 && progress < 0.6) {
                return { cx: this.x + this.facing * 40, cy: this.y - 10, w: 38, h: 36, dmg: this.stats.damage_light };
            }
        } else if (this.state === STATE.ATTACK_HEAVY) {
            const progress = 1 - this.stateTimer / ATTACK_HEAVY_MS;
            if (progress > 0.35 && progress < 0.65) {
                return { cx: this.x + this.facing * 52, cy: this.y - 10, w: 48, h: 44, dmg: this.stats.damage_heavy };
            }
        }
        return null;
    }

    // Auto-face opponent when idle/walking (not during attacks)
    faceOpponent(opponent) {
        if (this.state === STATE.ATTACK_LIGHT || this.state === STATE.ATTACK_HEAVY || this.state === STATE.KO) return;
        this.facing = opponent.x > this.x ? 1 : -1;
    }

    update(delta, opponent) {
        this.stateTimer -= delta;
        this.animTime += delta;

        // sync visual to body (feet at body bottom)
        this.view.x = this.body.x;
        this.view.y = this.body.y + BODY_H / 2;
        this.view.scaleX = 2 * this.facing;

        // auto-return to idle after timed states
        if (this.stateTimer <= 0) {
            if (this.state === STATE.ATTACK_LIGHT || this.state === STATE.ATTACK_HEAVY || this.state === STATE.HIT) {
                this.setState(this.onGround() ? STATE.IDLE : STATE.JUMP);
            }
        }

        // transition out of JUMP when landing
        if (this.state === STATE.JUMP && this.onGround() && this.body.body.velocity.y >= 0) {
            this.setState(STATE.IDLE);
        }

        // if idle and moving horizontally on ground, be in WALK
        if (this.state === STATE.IDLE && this.onGround() && Math.abs(this.body.body.velocity.x) > 20) {
            this.setState(STATE.WALK);
        } else if (this.state === STATE.WALK && Math.abs(this.body.body.velocity.x) < 10) {
            this.setState(STATE.IDLE);
        }

        this.animate();
    }

    animate() {
        const p = this.view.parts;
        switch (this.state) {
            case STATE.IDLE: {
                const bob = Math.sin(this.animTime * 0.006) * 1.2;
                p.head.y = -56 + bob;
                p.armL.y = -50 + bob; p.armR.y = -50 + bob;
                break;
            }
            case STATE.WALK: {
                const s = Math.sin(this.animTime * 0.02) * 4;
                p.legL.y = -10 + Math.max(0, s);
                p.legR.y = -10 + Math.max(0, -s);
                p.armL.y = -50 - s;
                p.armR.y = -50 + s;
                break;
            }
            case STATE.JUMP: {
                p.legL.y = -14; p.legR.y = -14;
                p.armL.y = -56; p.armR.y = -56;
                break;
            }
            case STATE.ATTACK_LIGHT: {
                const progress = 1 - this.stateTimer / ATTACK_LIGHT_MS;
                const t = progress < 0.5 ? progress * 2 : (1 - progress) * 2;
                // front arm extends
                p.armR.x = 14 + t * 22;
                p.armR.y = -50;
                p.armL.x = -14;
                p.armL.y = -50;
                break;
            }
            case STATE.ATTACK_HEAVY: {
                const progress = 1 - this.stateTimer / ATTACK_HEAVY_MS;
                const t = progress < 0.5 ? progress * 2 : (1 - progress) * 2;
                p.armR.x = 14 + t * 30;
                p.armR.y = -52 + t * 6;
                p.armL.x = -12 - t * 4;
                p.armL.y = -48;
                // slight forward lean
                this.view.rotation = t * 0.1 * this.facing;
                break;
            }
            case STATE.BLOCK: {
                p.armL.setPosition(-6, -52);
                p.armR.setPosition(6, -52);
                break;
            }
            case STATE.HIT: {
                // shake + lean back
                const shake = Math.sin(this.animTime * 0.05) * 2;
                p.head.x = shake;
                this.view.rotation = -0.12 * this.facing;
                break;
            }
            case STATE.KO: {
                this.view.rotation = -Math.PI / 2 * this.facing;
                break;
            }
        }
    }
}

// Collision helper: rect hitbox (cx,cy,w,h) vs fighter body rect.
export function hitboxOverlapsFighter(hb, fighter) {
    const bx = fighter.x;
    const by = fighter.y;
    const dx = Math.abs(hb.cx - bx);
    const dy = Math.abs(hb.cy - by);
    return dx <= (hb.w + BODY_W) / 2 && dy <= (hb.h + BODY_H) / 2;
}
