// SelectScene: shows a row of fighter cards with live code-drawn
// previews. Click a card to enter the FightScene against the next
// fighter in the list (simple auto-opponent for MVP).

import { drawFighterPreview } from '../entities/fighterArt.js';


export class SelectScene extends Phaser.Scene {
    constructor() {
        super('SelectScene');
    }

    create() {
        const w = this.scale.width;
        const h = this.scale.height;

        this.drawBackdrop();

        this.add.text(w / 2, 40, 'SELECT YOUR FIGHTER', {
            fontFamily: 'Courier New', fontSize: '28px', color: '#f0c674',
        }).setOrigin(0.5);
        this.add.text(w / 2, 76, 'Click a character. You will face the next one in line.', {
            fontFamily: 'Courier New', fontSize: '13px', color: '#aaa',
        }).setOrigin(0.5);

        const characters = this.registry.get('characters') || [];
        if (!characters.length) {
            this.add.text(w / 2, h / 2, 'No characters available.', {
                fontFamily: 'Courier New', fontSize: '18px', color: '#f66',
            }).setOrigin(0.5);
            return;
        }

        const cardW = 200;
        const cardH = 320;
        const gap = 20;
        const totalW = characters.length * cardW + (characters.length - 1) * gap;
        let x = (w - totalW) / 2;
        const y = 120;

        characters.forEach((c, i) => {
            const cx = x + cardW / 2;
            const cy = y + cardH / 2;

            const bg = this.add.rectangle(cx, cy, cardW, cardH, 0x1a1a1a, 1)
                .setStrokeStyle(2, 0xb33333)
                .setInteractive({ useHandCursor: true });

            this.add.text(cx, y + 20, c.name, {
                fontFamily: 'Courier New', fontSize: '18px', color: '#f0c674',
            }).setOrigin(0.5);

            // Code-drawn fighter preview
            const preview = drawFighterPreview(this, cx, cy + 10, c.palette, 2.2);

            const s = c.game_stats || {};
            this.add.text(cx, y + cardH - 48,
                `HP  ${s.max_hp}\nDMG ${s.damage_light}/${s.damage_heavy}\nSPD ${s.move_speed}`,
                { fontFamily: 'Courier New', fontSize: '12px', color: '#ccc', align: 'center' }
            ).setOrigin(0.5);

            bg.on('pointerover', () => bg.setStrokeStyle(3, 0xf0c674));
            bg.on('pointerout', () => bg.setStrokeStyle(2, 0xb33333));
            bg.on('pointerdown', () => {
                const opponent = characters[(i + 1) % characters.length];
                this.scene.start('FightScene', { player: c, opponent });
            });

            x += cardW + gap;
        });
    }

    drawBackdrop() {
        const w = this.scale.width;
        const h = this.scale.height;
        const g = this.add.graphics();
        // gradient-ish sky bands
        const bands = [0x1a0a1a, 0x2a1030, 0x4a1a40, 0x6a2040];
        const bandH = h / bands.length;
        bands.forEach((col, i) => {
            g.fillStyle(col, 1);
            g.fillRect(0, i * bandH, w, bandH);
        });
        // far silhouette mountains
        g.fillStyle(0x101020, 1);
        g.beginPath();
        g.moveTo(0, h);
        for (let i = 0; i <= 10; i++) {
            g.lineTo(i * w / 10, h - 80 - (i % 2 === 0 ? 60 : 20));
        }
        g.lineTo(w, h);
        g.closePath();
        g.fillPath();
    }
}
