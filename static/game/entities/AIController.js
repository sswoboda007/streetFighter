// AIController: minimal opponent brain. Behaviour:
//   - Far  : walk toward player
//   - Near : attack on cooldown (random light/heavy)
//   - Player attacking and we're close: chance to block
//   - After being hit: brief back-off
//
// Only drives methods on its Fighter (moveLeft/moveRight/attackLight/...).

const NEAR_DIST = 70;
const FAR_DIST = 260;

export class AIController {
    constructor(fighter) {
        this.fighter = fighter;
        this.cooldownMs = 600;
        this.backoffMs = 0;
    }

    update(delta, opponent) {
        const f = this.fighter;
        if (f.isKO || opponent.isKO) { f.stopMoving(); return; }
        if (!f.canAct()) return;

        this.cooldownMs = Math.max(0, this.cooldownMs - delta);
        this.backoffMs = Math.max(0, this.backoffMs - delta);

        const dx = opponent.x - f.x;
        const absDx = Math.abs(dx);
        const dir = Math.sign(dx) || 1;

        // React to incoming attack: sometimes block
        const opponentAttacking = opponent.state === 'attack_light' || opponent.state === 'attack_heavy';
        if (opponentAttacking && absDx < NEAR_DIST + 20 && Math.random() < 0.04) {
            f.startBlock();
            return;
        }
        if (f.state === 'block' && !opponentAttacking) {
            f.stopBlock();
        }

        if (this.backoffMs > 0) {
            // retreat
            if (dir > 0) f.moveLeft(); else f.moveRight();
            return;
        }

        if (absDx > FAR_DIST) {
            if (dir > 0) f.moveRight(); else f.moveLeft();
        } else if (absDx > NEAR_DIST) {
            if (dir > 0) f.moveRight(); else f.moveLeft();
        } else {
            // in range — stop and swing
            if (this.cooldownMs === 0) {
                if (Math.random() < 0.35) f.attackHeavy();
                else f.attackLight();
                this.cooldownMs = f.stats.attack_cooldown_ms + 100;
                // occasional short retreat after swing
                if (Math.random() < 0.25) this.backoffMs = 350;
            }
        }
    }
}
