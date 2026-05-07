// fighterArt.js: shared drawing helpers for code-drawn fighters.
// Fighters are Phaser Containers of Rectangles. Body parts are
// stored as named children so animation code (ACS-2) can manipulate
// their positions/rotations directly.
//
// Part layout (relative to container origin at feet center):
//   head:  small square above torso
//   torso: main body rectangle
//   armL / armR: side arms
//   legL / legR: legs beneath torso
// Palette keys: skin, gi, belt, hair, accent

const DEFAULT_PALETTE = {
    skin: 0xf2c28b, gi: 0x888888, belt: 0x222222, hair: 0x222222, accent: 0xf0c674,
};

export function createFighter(scene, x, y, palette) {
    const pal = { ...DEFAULT_PALETTE, ...(palette || {}) };
    const container = scene.add.container(x, y);

    // coords are relative; feet at y=0, head up (negative y)
    const legL = scene.add.rectangle(-6, -10, 8, 20, pal.gi).setOrigin(0.5, 1);
    const legR = scene.add.rectangle(6, -10, 8, 20, pal.gi).setOrigin(0.5, 1);
    const belt = scene.add.rectangle(0, -30, 22, 4, pal.belt).setOrigin(0.5, 1);
    const torso = scene.add.rectangle(0, -30, 22, 26, pal.gi).setOrigin(0.5, 1);
    const armL = scene.add.rectangle(-14, -50, 6, 18, pal.gi).setOrigin(0.5, 0);
    const armR = scene.add.rectangle(14, -50, 6, 18, pal.gi).setOrigin(0.5, 0);
    const head = scene.add.rectangle(0, -56, 16, 14, pal.skin).setOrigin(0.5, 1);
    const hair = scene.add.rectangle(0, -70, 18, 4, pal.hair).setOrigin(0.5, 1);
    const band = scene.add.rectangle(0, -62, 18, 2, pal.accent).setOrigin(0.5, 1);

    container.add([legL, legR, belt, torso, armL, armR, head, band, hair]);
    container.parts = { legL, legR, belt, torso, armL, armR, head, hair, band };
    container.palette = pal;
    return container;
}

// Convenience wrapper used by the select/fight preview screens.
// Draws a non-interactive fighter at (x, y) scaled uniformly. If
// facingLeft is true, the container is flipped on the X axis.
export function drawFighterPreview(scene, x, y, palette, scale = 2, facingLeft = false) {
    const f = createFighter(scene, x, y, palette);
    f.setScale(scale * (facingLeft ? -1 : 1), scale);
    return f;
}
