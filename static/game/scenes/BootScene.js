// BootScene: fetches character roster from the API, stores it in the
// game registry, then transitions to SelectScene. No sprite loading
// needed -- every fighter is drawn procedurally at play time.

export class BootScene extends Phaser.Scene {
    constructor() {
        super('BootScene');
    }

    async create() {
        const w = this.scale.width;
        const h = this.scale.height;

        const title = this.add.text(w / 2, h / 2 - 20, 'STREET FIGHTER', {
            fontFamily: 'Courier New', fontSize: '48px', color: '#f0c674',
        }).setOrigin(0.5);

        const status = this.add.text(w / 2, h / 2 + 30, 'LOADING FIGHTERS...', {
            fontFamily: 'Courier New', fontSize: '16px', color: '#aaa',
        }).setOrigin(0.5);

        try {
            const res = await fetch('/api/characters');
            if (!res.ok) throw new Error(await res.text());
            const characters = await res.json();
            this.registry.set('characters', characters);
            this.time.delayedCall(300, () => {
                title.destroy();
                status.destroy();
                this.scene.start('SelectScene');
            });
        } catch (err) {
            status.setColor('#f66');
            status.setText('Failed to load: ' + err.message);
        }
    }
}
