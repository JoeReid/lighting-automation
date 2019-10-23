from copy import deepcopy
import random

import stageOrchestration.lighting.timeline_helpers.colors as color

name = __name__.split('.')[-1]
META = {
    'name': name,
    'bpm': 60,
    'timesignature': '4:4',
}

def create_timeline(dc, t, tl, el):
    tl.set_(dc.get_devices(), color.YELLOW, 0)
    tl.set_(dc.get_devices(), color.YELLOW, 130)

    el.add_trigger({
        "deviceid": "audio",
        "func": "audio.start",
        "src": f"{name}/hibana_intro.ogg",
        "timestamp": t('1.1.1'),
    })


    # el.add_trigger({
    #     "deviceid": "rear",
    #     "func": "image.show",
    #     "src": f"logo/superLimitBreak_logo.svg",
    #     "duration": t('10.1.1'),
    #     "timestamp": t('2.1.1'),
    # })

    el.add_trigger({
        "deviceid": "rear",
        "func": "gsap.start",
        "timestamp": t('2.1.1'),
        "duration": 120,
        "elements": {
            "logo": {"src": "logo/superLimitBreak_logo.svg", "height": "1vh", "className": "center"}
        },
        "gsap_timeline": [
            ["logo_scroll", "to", "element::logo", 0, {"margin-top": "1vh"}],
            ["logo_scroll", "to", "element::logo", 100, {"margin-top": "0vh"}],

            ["logo_fade", "to", "element::logo", 0, {"opacity": 0}],
            ["logo_fade", "to", "element::logo", 30, {"opacity": 1}],

            ["logo_seepier", "to", "element::logo", 0, {"filter": "sepia(1) blur(20px)", "autoRound": False}],
            ["logo_seepier", "to", "element::logo", 60, {"filter": "sepia(1) blur(20px)", "autoRound": False}],
            ["logo_seepier", "to", "element::logo", 60, {"filter": "sepia(0) blur(0px)", "autoRound": False}]
        ]
    })


    RAIN = {
        "func": "particles.start",
        "emitters": {
            "rain": {
                "particleImages": ["assets/HardRain.png"],
                "emitterConfig": {
                    "alpha": {"start": 0.5, "end": 0.5},
                    "scale": {"start": 1, "end": 1},
                    "color": {"start": "ffffff", "end": "ffffff"},
                    "speed": {"start": 2000, "end": 2000},
                    "startRotation": {"min": 80, "max": 80},
                    "rotationSpeed": {"min": 0, "max": 0},
                    "lifetime": {"min": 0.6, "max": 0.6},
                    "blendMode": "normal",
                    "frequency": 0.004,
                    "emitterLifetime": 0,
                    "maxParticles": 1000,
                    "pos": {"x": 0, "y": 0},
                    "addAtBack": False,
                    "spawnType": "rect",
                    "spawnRect": {"x": "-0.5vw", "y": "-0.2vh", "w": "1.5vw", "h": "0.1vh"}
                },
                "gsap_timeline": [
                    ["to", "", 0, {"frequency": 1.000}],
                    ["to", "", 10, {"frequency": 0.004}]
                ]
            }
        }
    }
    el.add_trigger({
        "deviceid": "front",
        #"duration": 100,#t('10.1.1'),
        "timestamp": t('3.1.1'),
        **RAIN,
    })


    FIREWORK = {
        "func": "particles.start",
        "emitters": {
            "firework": {
                "particleImages": ["assets/Sparks.png"],
                "emitterConfig": {
                    "alpha": {"start": 1, "end": 0.31},
                    "scale": {"start": 0.5, "end": 1},
                    "color": {"start": "ffffff", "end": "9ff3ff"},
                    "speed": {"start": 100, "end": 100},
                    "acceleration": {"x":0, "y": 200},
                    "startRotation": {"min": 0, "max": 360},
                    "rotationSpeed": {"min": 0, "max": 0},
                    "lifetime": {"min": 1, "max": 3},
                    "blendMode": "normal",
                    "frequency": 0.001,
                    "emitterLifetime": 0.25,
                    "maxParticles": 200,
                    "pos": {"x": "0.5vw", "y": "0.5vh"},
                    "addAtBack": False,
                    "spawnType": "circle",
                    "spawnCircle": {"x": 0, "y": 0, "r": 2}
                }
            }
        }
    }

    def firework(t, x=None, y=None):
        assert t > 0
        _firework = deepcopy(FIREWORK)
        emitterConfig = _firework['emitters']['firework']['emitterConfig']
        emitterConfig['pos']['x'] = f'{x or random.random()}vw'
        emitterConfig['pos']['y'] = f'{y or random.random()}vh'
        el.add_trigger({
            "deviceid": "front",
            "timestamp": t,
            **_firework,
        })

    firework(t('4.1.1'))
    firework(t('5.1.1'))
    firework(t('6.1.1'))
    firework(t('7.1.1'))
