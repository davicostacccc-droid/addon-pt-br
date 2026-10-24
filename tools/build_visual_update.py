"""Package a visual update while proving all previous narration is preserved."""
import json
from pathlib import Path
import shutil
import tempfile
import zipfile
from lupa.lua51 import LuaRuntime
from build_pack import digest

ROOT = Path(__file__).resolve().parents[1]


def main():
    previous=ROOT/'dist/northrend-0.5.0-beta1/AzerothVoz'
    parent=ROOT/'dist/cinema-0.6.0-beta2'
    out=parent/'AzerothVoz'
    zipped=ROOT/'dist/AzerothVoz-0.6.0-beta2-Cinema-12340.zip'
    if out.exists() or zipped.exists(): raise FileExistsError('Preserve previous packages; choose a new version.')
    parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temp:
        stage=Path(temp)/'AzerothVoz';shutil.copytree(previous,stage)
        for file in (ROOT/'addon/AzerothVoz').iterdir():
            if file.name!='Pack.lua' and file.suffix in ('.lua','.toc'):shutil.copyfile(file,stage/file.name)
        shutil.copyfile(ROOT/'docs/BETA-VISUAL-0.6.0.md',stage/'LEIA-ME.md')
        coverage=json.loads((stage/'COBERTURA.json').read_text(encoding='utf-8'))
        coverage.update(version='0.6.0-beta2',content_version='0.5.0-beta1',in_game='pending visual confirmation')
        (stage/'COBERTURA.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
        if (stage/'Pack.lua').read_bytes()!=(previous/'Pack.lua').read_bytes():raise ValueError('Catalog changed')
        if (stage/'manifest.json').read_bytes()!=(previous/'manifest.json').read_bytes():raise ValueError('Manifest changed')
        manifest=json.loads((stage/'manifest.json').read_text(encoding='utf-8'))
        unique={}
        for row in manifest:unique[row['audio'].replace('\\','/')]=row['sha256']
        for relative,expected in unique.items():
            path=(stage/relative).resolve()
            if not path.is_relative_to(stage.resolve()):raise ValueError('Audio outside stage')
            if digest(path)!=expected or digest(previous/relative)!=expected:raise ValueError('Previous audio changed')
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute((ROOT/'tests/wow_stub.lua').read_text(encoding='utf-8'))
        for name in [l.strip() for l in (stage/'AzerothVoz.toc').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]:
            lua.execute((stage/name).read_text(encoding='utf-8'))
            if name!='Pack.lua' and (stage/name).read_bytes()!=(ROOT/'addon/AzerothVoz'/name).read_bytes():raise ValueError('Code differs from source')
        lua.execute("Emit('ADDON_LOADED','AzerothVoz'); QuestFrame:Show(); function GetTitleText() return _title end")
        records=[]
        for directory in ('durotar-0.3.0','kalimdor-0.4.0-beta1','northrend-0.5.0-beta1'):
            records+=json.loads((ROOT/'dist'/directory/'expected-records.json').read_text(encoding='utf-8'))
        page_checks=0
        for sex in (2,3):
            lua.globals()._sex=sex;lua.execute('UnitSex=function() return _sex end')
            for row in records:
                text=lua.eval('AzerothVoz.Expand')(row['translation'])
                pages=lua.eval('AzerothVoz.RoleplayPages')(text)
                strings=[pages[i] for i in range(1,len(pages)+1)]
                if ''.join(strings)!=text or any(len(s)>250 for s in strings):raise ValueError('Pagination corrupted dialogue')
                page_checks+=1
        samples=records[::max(1,len(records)//100)]
        samples+=[r for r in records if r['questID']==12451]
        events=0
        for modern in (False,True):
            lua.globals().AzerothVozDB.roleplay=modern
            for row in samples:
                lua.globals()._text=lua.eval('AzerothVoz.ResolveSource')(row['source'])
                lua.globals()._title=row.get('sourceTitle','English title')
                lua.globals()._guid=f"0xF130{row['npc']:06X}000001" if row['npc'] else None
                lua.eval('Emit')(row['event']);lua.execute('Tick(0.1);Tick(0.1)')
                if lua.eval('AzerothVoz.current.record.questID')!=row['questID']:raise ValueError('Wrong dialogue')
                if modern:
                    lua.execute('assert(AzerothVoz.roleplay:IsShown() and not AzerothVoz.reader:IsShown())')
                    lua.execute('AzerothVoz.roleplay.nextButton.scripts.OnClick(); assert(AzerothVoz.roleplay.manualPage)')
                    lua.execute('AzerothVoz.roleplay.autoButton.scripts.OnClick(); assert(not AzerothVoz.roleplay.manualPage)')
                else:lua.execute('assert(AzerothVoz.controls:IsShown() and not AzerothVoz.roleplay:IsShown())')
                lua.execute("Emit('QUEST_FINISHED');assert(not AzerothVoz.playing and not AzerothVoz.roleplay:IsShown())")
                events+=1
        stage.replace(out)
    with zipfile.ZipFile(zipped,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for file in sorted(out.rglob('*')):
            if file.is_file():archive.write(file,'AzerothVoz/'+file.relative_to(out).as_posix())
    with zipfile.ZipFile(zipped) as archive:
        if archive.testzip() is not None:raise ValueError('Corrupt ZIP')
        for file in out.rglob('*'):
            if file.is_file() and archive.read('AzerothVoz/'+file.relative_to(out).as_posix())!=file.read_bytes():raise ValueError('ZIP mismatch')
    report=dict(version='0.6.0-beta2',content_version='0.5.0-beta1',pagination_checks=page_checks,event_checks=events,
                audio_files_preserved=len(unique),catalog_and_manifest_unchanged=True,zip_verified=True,
                zip_sha256=digest(zipped),zip_bytes=zipped.stat().st_size,in_game='pending player visual confirmation')
    (parent/'VERIFICACAO.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (parent/'SHA256SUMS.txt').write_text(report['zip_sha256']+'  '+zipped.name+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
