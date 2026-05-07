import { BootScene } from './scenes/BootScene.js';
import { SelectScene } from './scenes/SelectScene.js';
import { FightScene } from './scenes/FightScene.js';

const config = {
    type: Phaser.AUTO,
    parent: 'game',
    width: 960,
    height: 540,
    pixelArt: true,
    backgroundColor: '#000000',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 1400 },
            debug: false,
        },
    },
    scene: [BootScene, SelectScene, FightScene],
};

new Phaser.Game(config);
