"""Build v17 line variants from the current line 4 model and procedural atlas."""
import base64
import copy
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/mtr/jinan_line4'
CREDIT = '这是GPT-6.1-sol (High)接入Codex制作'
PALETTE = {4: 'A5D431', 6: '55B7D5', 7: 'C65054', 8: '8965AE', 9: 'B69452'}
SEAT_PALETTE = {6: '74BDCF', 7: 'CB7474', 8: '9A83B6', 9: 'BBA071'}

def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def build():
    config_path = ROOT / 'assets/mtr/mtr_custom_resources.json'
    current = json.loads(config_path.read_text(encoding='utf-8'))
    single = copy.deepcopy(current)
    single['vehicles'] = [v for v in current['vehicles'] if v['id'].startswith('jinan_line4_')]
    single['vehicleScripts'] = [s for s in current['vehicleScripts'] if s['id'] == 'jinan_line4_lcd']
    assert len(single['vehicles']) == 4
    single['vehicleScripts'][0]['input']['defaultColor'] = int(PALETTE[4], 16)
    merged = copy.deepcopy(single)
    # Execute only the existing procedural texture authoring section; no mesh rebuild.
    atlas_code = (ROOT / 'source/generate_pack.py').read_text(encoding='utf-8').split('class Mesh:')[0]
    for line, color in PALETTE.items():
        if line == 4:
            continue
        target = ROOT / f'assets/mtr/jinan_line{line}'
        for src in BASE.rglob('*'):
            if not src.is_file():
                continue
            dst = target / src.relative_to(BASE)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.suffix in ['.json', '.obj', '.mtl', '.js', '.bbmodel']:
                dst.write_text(src.read_text(encoding='utf-8').replace('jinan_line4', f'jinan_line{line}'), encoding='utf-8')
            else:
                dst.write_bytes(src.read_bytes())
        code = atlas_code.replace('jinan_line4', f'jinan_line{line}')
        code = code.replace("'#b1d93e'", repr('#' + color)).replace("'#9dd91d'", repr('#' + SEAT_PALETTE[line]))
        code = code.replace('4 号线   LINE 4', f'{line} 号线   LINE {line}').replace("'0401'", repr(f'{line:02d}01'))
        # This atlas row is unused by the native headsign; avoid carrying line 4 station labels.
        code = code.replace('第一医科大学  ←  4  →  彭家庄', f'济南地铁  {line} 号线')
        exec(compile(code, str(ROOT / 'source/generate_pack.py'), 'exec'), {'__file__': str(ROOT / 'source/generate_pack.py')})
        embedded = 'data:image/png;base64,' + base64.b64encode((target / 'textures/atlas.png').read_bytes()).decode()
        for path in (target / 'models').glob('*.bbmodel'):
            data = json.loads(path.read_text(encoding='utf-8'))
            for texture in data.get('textures', []):
                texture['source'] = embedded
            dump(path, data)
        for original in single['vehicles']:
            vehicle = json.loads(json.dumps(original, ensure_ascii=False).replace('jinan_line4', f'jinan_line{line}').replace('济南地铁4号线', f'济南地铁{line}号线'))
            vehicle['color'] = color
            merged['vehicles'].append(vehicle)
        script = json.loads(json.dumps(single['vehicleScripts'][0]).replace('jinan_line4', f'jinan_line{line}'))
        script['input']['defaultColor'] = int(color, 16)
        script_path = target / 'scripts/lcd.js'
        script_path.write_text(script_path.read_text(encoding='utf-8').replace('defaultColor:0xa5d431', 'defaultColor:0x' + color.lower()), encoding='utf-8')
        merged['vehicleScripts'].append(script)
    dump(config_path, merged)
    dump(ROOT / 'pack.mcmeta', {'pack': {'pack_format': 22, 'description': '济南地铁 4/6/7/8/9 号线 · 无标志合辑 v17 | 版本：MTR 4.0.5，JCM 2.3.0 | ' + CREDIT}})
    for name, config, lines, description in [
        ('jinan_line4_no_logo_v17.zip', single, [4], '济南地铁4号线 · 无标志独立版 v17'),
        ('jinan_lines_4_6_7_8_9_v17.zip', merged, list(PALETTE), '济南地铁4/6/7/8/9号线 · 无标志合辑 v17'),
    ]:
        with zipfile.ZipFile(ROOT / 'dist' / name, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('pack.mcmeta', json.dumps({'pack': {'pack_format': 22, 'description': description + ' | 版本：MTR 4.0.5，JCM 2.3.0 | ' + CREDIT}}, ensure_ascii=False))
            archive.write(ROOT / 'pack.png', 'pack.png')
            archive.writestr('assets/mtr/mtr_custom_resources.json', json.dumps(config, ensure_ascii=False, indent=2))
            for line in lines:
                for path in (ROOT / f'assets/mtr/jinan_line{line}').rglob('*'):
                    if path.is_file():
                        archive.write(path, path.relative_to(ROOT).as_posix())
        print(name, (ROOT / 'dist' / name).stat().st_size)
    print('Vehicles:', len(merged['vehicles']), 'scripts:', len(merged['vehicleScripts']))

if __name__ == '__main__':
    build()
